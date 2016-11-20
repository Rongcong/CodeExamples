import collections
import heapq
import os
import threading
import socket
import worker
import json
import shutil
import time
import datetime
import sys
import helper
from multiprocessing import Process

class Master:
    def __init__(self, num_workers, port_num):
        self.num_workers = num_workers
        self.port_num = port_num

        # keep a list of workers and a sepetate list of ready workers  
        self.all_workers = range(0, num_workers)

        # store all workers that are currently working, or currently ready
        # key: "worker_num"
        # val: "worker_job"
        self.ready_workers = {}
        self.busy_workers = {}

        # store all the job messages
        # item: dict {"job_id", "job_message"}
        self.job_queue = []

        # key: worker_num, val: process reference
        # terminate all the processes inside it when receive shutdown message
        self.worker_processes = {}

        # the job that the master is currently working on
        # {"job_id": XXX, "job_message": XXX}
        # "job_message" is the message received from send_job
        self.curr_job = {}

        # The counter for job, start from 0
        self.job_counter = -1

        # there should be four status for master
        # free, map, group and reduce
        self.status = "free"

        # dict to track the workers' heartbeat
        # key: worker num, val: last heartbeat time
        self.heartBeat = {};

        # create the folder var
        var_dir = self.__get_output_directory(status="var")

        if (os.path.isdir(var_dir)):
            shutil.rmtree(var_dir)
        os.makedirs(var_dir)

        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
        # bind the socket to the server, replace "localhost" with '127.0.0.1'
        # NOTE: use socket.gethostname() if you want server to listen on 0.0.0.0
        s.bind(('127.0.0.1', port_num))

        # become a server socket, 1 more connection to receive jobs sent
        s.listen(20)

        # create the new thread called set_up_thread
        set_up_thread = threading.Thread(target=self.set_up_master, args=())
        set_up_thread.start()

        # start waiting for the message
        while True:
            # connect
            clientsocket, address = s.accept()
            print("Master: connection from ", address)

            # Receive a message
            message = helper.recv_message(clientsocket=clientsocket)
            self.handle_msg(message=message)         
        s.close();


    def map(self, job):
        # begin the map process
        job_id = job["job_id"]
        job_message = job["job_message"]

        # update the current job
        self.curr_job = job

        output_directory = self.__get_output_directory(status="mapper", job_id=job_id)

        all_input_files = [os.path.join(job_message["input_directory"], name) for name in os.listdir(job_message["input_directory"]) if os.path.isfile(os.path.join(job_message["input_directory"], name))]
        files_count = len(all_input_files)
        workers_count = len(self.ready_workers)

        avg_files_count = int(files_count/workers_count)
        extra_files_count = files_count%workers_count

        file_num = 0
        worker_counter = 0;
        ready_indexs = list(self.ready_workers.keys());
        for worker_num in ready_indexs:
            input_files = []
            # these workers should have one additional file
            if (worker_counter < extra_files_count):
                input_files = all_input_files[file_num:(file_num + avg_files_count + 1)]
                file_num += (avg_files_count + 1)
            elif avg_files_count > 0:
                input_files = all_input_files[file_num:(file_num + avg_files_count)]
                file_num += avg_files_count
            else:
                # number of availabe workers is larger than number of input files
                # some workers no job
                break

            worker_counter += 1;
            worker_job = {
                "message_type": "new_worker_job",
                "input_files": input_files,
                "executable": job_message["mapper_executable"],
                "output_directory": output_directory
            }
            self.send_worker_job(worker_num=worker_num, worker_job=worker_job)

            # store the worker's job in busy_workers, remove it from free list
            self.busy_workers[worker_num] = worker_job
            del self.ready_workers[worker_num];
        # end of for
        self.status = "map"


    def reduce(self, grouper_filenames):
        job_id = self.curr_job["job_id"]
        job_message = self.curr_job["job_message"]

        # the length of grouper_filenames is equal to the length of ready workers
        output_directory = self.__get_output_directory(status="reducer", job_id=job_id)

        counter = 0;
        index_list = list(self.ready_workers.keys());
        for worker_num in index_list:
            if counter >= len(grouper_filenames):
                break;
            worker_job = {
                "message_type": "new_worker_job",
                "input_files": [grouper_filenames[counter]],
                "executable": job_message["reducer_executable"],
                "output_directory": output_directory
            }

            self.send_worker_job(worker_num=worker_num, worker_job=worker_job)
            self.busy_workers[worker_num] = worker_job;
            del self.ready_workers[worker_num];
            counter += 1;

        self.status = "reduce"


    def send_worker_job(self, worker_num, worker_job):
        # send the worker's job to one worker
        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # connect to the worker process
            s.connect(('127.0.0.1', self.port_num + worker_num + 1))
            s.sendall(str.encode(json.dumps(worker_job)))
        except socket.error as e:
            pass
        s.close()


    def handle_msg(self, message):
        msg = json.loads(message)
        print(msg)
        if (msg["message_type"] == "shutdown"):
        # shutdown and terminate all created processes
            print("shutdown signal received.");
            for worker_num in self.worker_processes:
                if self.worker_processes[worker_num].is_alive():
                    print("worker num " + str(worker_num) + " is terminated");
                    self.worker_processes[worker_num].terminate();
                    self.worker_processes[worker_num].join();

        elif (msg["message_type"] == "status"):
            if (msg["status"] == "ready"):
                if (msg["worker_number"] in self.busy_workers):
                    # the worker restarts, the master should send the same job again
                    # the worker should be still in busy list
                    self.send_worker_job(worker_num=msg["worker_number"], 
                                         worker_job=self.busy_workers[msg["worker_number"]])

                else:
                    # this worker is newly created or dead no working and restarted
                    # NOTE: worker should be removed from ready list if dead not working
                    self.ready_workers[msg["worker_number"]] = 1;

                    # execute the first job in the job queue
                    if (self.status == "free" and len(self.job_queue) > 0):
                        job = self.job_queue[0]
                        self.job_queue.pop(0)
                        self.map(job=job)

            elif (msg["status"] == "finished"):
                worker_num = msg["worker_number"]

                # add the worker back to ready_workers
                self.ready_workers[worker_num] = 1;

                # remove the worker from busy workers
                if (worker_num in self.busy_workers):
                    del self.busy_workers[worker_num]

                # all the busy workers have finished their jobs
                if (len(self.busy_workers) == 0):
                    if (self.status == "map"):
                        # begin the group part
                        input_dir = self.__get_output_directory(status="mapper", job_id=self.curr_job["job_id"])
                        output_dir = self.__get_output_directory(status="grouper", job_id=self.curr_job["job_id"])
                        grouper_filenames = self.__staff_run_group_stage(input_dir=input_dir, 
                                                                         output_dir=output_dir, 
                                                                         num_workers=len(self.ready_workers))

                        # begin the reduce part
                        self.reduce(grouper_filenames=grouper_filenames)

                    elif (self.status == "reduce"):
                        # all workers have finished executing the reduce stage
                        # move the output from the reducer-output directory to the final output directory
                        job_id = self.curr_job["job_id"]
                        job_message = self.curr_job["job_message"]
                        source = self.__get_output_directory(status="reducer", job_id=job_id)
                        dest = job_message["output_directory"]
                        if not os.path.isdir(dest):
                            os.mkdir(dest);
                        files = os.listdir(source)

                        for f in files:
                            shutil.copy(os.path.join(source, f), os.path.join(dest, f))

                        # if the job queue is not empty, start another job's map stage
                        if (len(self.job_queue) != 0):
                            job = self.job_queue[0]
                            self.job_queue.pop(0)
                            self.map(job=job)
                        else:
                            # set the status to be free
                            self.status = "free"

        elif (msg["message_type"] == "new_master_job"):
            self.job_counter += 1
            # create four directories needed for this job
            os.mkdir(self.__get_output_directory(status="job", job_id=self.job_counter))
            os.mkdir(self.__get_output_directory(status="mapper", job_id=self.job_counter))
            os.mkdir(self.__get_output_directory(status="grouper", job_id=self.job_counter))
            os.mkdir(self.__get_output_directory(status="reducer", job_id=self.job_counter))

            if (self.status == "free" and len(self.ready_workers) > 0):
                # if there are workers that are free now
                # start the map part
                self.map(job={"job_id": self.job_counter, "job_message": msg})

            else:
                # just put the job on the job queue
                self.job_queue.append({"job_id": self.job_counter, "job_message": msg})


    def set_up_master(self):
        print("create {} workers and listen on port_num {}".format(self.num_workers, self.port_num))

        for i in range(0, self.num_workers):
            self.worker_processes[i] = Process(target=self.WorkerCreater, args=(i, ));
            self.worker_processes[i].start();

        heartbeat_listener_thread = threading.Thread(target=self.heartbeat_listener, args=())
        fault_handler_thread = threading.Thread(target=self.fault_handler, args=())

        heartbeat_listener_thread.start()
        fault_handler_thread.start()


    def WorkerCreater(self, worker_index):
        new_worker = worker.Worker(worker_num=worker_index,
                                   port_num=self.port_num+worker_index+1,
                                   master_port=self.port_num,
                                   master_heartbeat_port=self.port_num-1);


    # listen to the heartbeat of worker threads, call fault handler if one worker dies
    def heartbeat_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        sock.bind(('127.0.0.1', self.port_num - 1));
        while True:
            data, addr = sock.recvfrom(1024);
            msg = json.loads(data.decode("utf-8"))
            if (msg["message_type"] == "heartbeat"):
                self.heartBeat[msg["worker_number"]] = datetime.datetime.now().time(); 
        sock.close() 


    def fault_handler(self):
        while True:
            due = datetime.datetime.now().time();
            time.sleep(10);
            print("fault_handler awaken at:");
            print(datetime.datetime.now().time().isoformat());

            for i in range(0, self.num_workers):
               if i not in self.heartBeat or self.heartBeat[i] < due:
                   # this worker is dead
                   # restart the process, note that job redispatch is done by handle_msg
                   print("worker num " + str(i) + " is dead, restarting it...");
                   self.worker_processes[i].terminate();
                   self.worker_processes[i].join();
                   if i in self.ready_workers:
                       self.ready_workers.pop(i, None);
		   # if it is busy, should still in busy list
                   self.worker_processes[i] = Process(target=self.WorkerCreater, args=(i, )); 
                   self.worker_processes[i].start();


    def __get_output_directory(self, status, job_id=None):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        if (status == "var"):
            output_directory = os.path.join(current_directory, "var/")
        elif (status == "job"):
            output_directory = os.path.join(current_directory, "var/job-{}/".format(job_id))
        else:
            output_directory = os.path.join(current_directory, "var/job-{}/{}-output/".format(job_id, status))
        return output_directory
                        

    def __staff_run_group_stage(self, input_dir, output_dir, num_workers):
        # Loop through input directory and get all the files generated in Map stage
        filenames = []

        for in_filename in os.listdir(input_dir):
            if in_filename == ".DS_Store":
                continue
            filename = input_dir + in_filename

            # Open file, sort it now to ease the merging load later
            with open(filename, 'r') as f_in:
                content = sorted(f_in)

            # Write it back into the same file
            with open(filename, 'w+') as f_out:
                f_out.writelines(content)

            # Remember it in our list
            filenames.append(filename)

        # Create a new file to store ALL the sorted tuples in one single
        sorted_output_filename = os.path.join(output_dir, 'sorted.out')
        sorted_output_file = open(sorted_output_filename, 'w+')

        # Open all files in a single map command! Python is cool like that!
        files = map(open, filenames)

        # Loop through all merged files and write to our single file above
        for line in heapq.merge(*files):
            sorted_output_file.write(line)

        sorted_output_file.close()

        # Create a circular buffer to distribute file among number of workers
        grouper_filenames = []
        grouper_fhs = collections.deque(maxlen=num_workers)

        for i in range(num_workers):
            # Create temp file names
            basename = "file{0:0>4}.out".format(i)
            filename = os.path.join(output_dir, basename)

            # Open files for each worker so we can write to them in the next loop
            grouper_filenames.append(filename)
            fh = open(filename, 'w')
            grouper_fhs.append(fh)

        # Write lines to grouper output files, allocated by key
        prev_key = None
        sorted_output_file = open(os.path.join(output_dir, 'sorted.out'), 'r')

        for line in sorted_output_file:
            # Parse the line (must be two strings separated by a tab)
            tokens = line.rstrip().split("\t", 2)
            assert len(tokens) == 2
            key, value = tokens

            # If it's a new key, then rotate circular queue of grouper files
            if prev_key != None and key != prev_key:
                grouper_fhs.rotate(1)

            # Write to grouper file
            fh = grouper_fhs[0]
            fh.write(line)

            # Update most recently seen key
            prev_key = key

        # Close grouper output file handles
        for fh in grouper_fhs:
            fh.close()

        # Delete the sorted output file
        sorted_output_file.close()
        # os.remove(sorted_output_filename)

        # Return array of file names generated by grouper stage
        return grouper_filenames

