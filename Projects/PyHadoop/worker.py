import os
import sh
import socket
import threading
import time
import json
import helper
from multiprocessing import Process

class Worker:
    def __init__(self, worker_num, port_num, master_port, master_heartbeat_port):

        # save inputs
        self.worker_num = worker_num
        self.port_num = port_num
        self.master_port = master_port
        self.master_heartbeat_port = master_heartbeat_port

        # create an INET, STREAMing socket
        td = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        td.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to the server
        # NOTE: use socket.gethostname() if you want server to listen on 0.0.0.0
        td.bind(('127.0.0.1', self.port_num))

        # become a server socket
        td.listen(20)

        # create the new thread called set_up_thread
        setup_thread = threading.Thread(target=self.setup)
        setup_thread.start()

        # start waiting for the message
        while True:
            # wait to accept message from Master
            (clientsocket, addr) = td.accept()
            print("Worker: connection from ", addr)

            # Receive a message
            msg = helper.recv_message(clientsocket=clientsocket)
            self.handle_msg(message=msg)
        td.close()


    # Upon receiving message from Master
    def handle_msg(self, message):
        msg = json.loads(message)
        print(msg)

        # start execution of the given executable on each input file for loop
        if (msg["message_type"] == "new_worker_job"):
            # use sh.Command to execute map/reducer function with input file name and output directory
            output_dir = msg["output_directory"]
            for input_file in msg["input_files"]:
                output_file = os.path.join(output_dir, os.path.split(input_file)[1]);
                cmd = sh.Command(msg["executable"])
                inf = open(input_file, "r")
                cmd(_in=inf, _out=output_file)
                inf.close();
            # once worker's job is done, send a TCP message to the Master's main socket
            self.send_msg(status="finished")


    def heartbeat(self):
        message = {"message_type": "heartbeat", "worker_number": self.worker_num};
        message_json = str.encode(json.dumps(message));
        while (True):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            sock.sendto(message_json, ('127.0.0.1', self.master_heartbeat_port))
            sock.close()
            time.sleep(2)


    # after initialization, it should send a ready message to master's TCP socket
    def setup(self):
        print("set up worker num {}".format(self.worker_num))
        # create a new heartbeat thread that will communicate with the Master
        heartbeat_thread = threading.Thread(target=self.heartbeat)
        heartbeat_thread.start()
        # after initialization, send a message to the Master's socket letting it know that worker is ready to work
        self.send_msg(status="ready")


    def send_msg(self, status):
        # send a message to the Master's socket letting it know that worker is ready to work or finished work
        # rply_msg in json form
        rply_msg = {
            "message_type": "status",
            "worker_number": self.worker_num,
            "status": status
        }
        data = json.dumps(rply_msg)
        # set up socket, connect to master, send msg and close
        sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sd.connect(('127.0.0.1', self.master_port))
        sd.sendall(str.encode(data))
        sd.close()

