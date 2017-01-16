// Marathon OOP Design Solution
class Marathon {
public:
	// Marathon constructor, construct runners and sensors, init cap, num, max_sensor_id, min_sensor_id
	Marathon (int num_runners, int num_sensors, int num): cap(num), num(0), min_sensor_id(-1), max_sensor_id(-1) {
		for (int i = 0; i < runner_id.size(); i++) {
			Runner* runner = new Runner(i);
			runners.emplace_back(runner);
		}

		for (int i = 0; i < sensor_id.size(); i++) {
			Sensor* sensor = new Sensor(i);
			sensors.emplace_back(sensor);
		}
	}
	// Destructor, de-allocate memory for runners and sensors
	~Marathon() {
		for (int i = 0; i < runner_id.size(); i++) {
			delete runners[i];
			runners[i] = NULL;
		}

		for (int i = 0; i < sensor_id.size(); i++) {
			delete sensors[i];
			sensors[i] = NULL;
		}
	}

	// When runner pass sensor, updates top_K_runners list, Runner info and Sensor info.
    // When to update top K runners list? Firstly, when top_k_list's size is less than k.
    // Secondly, when top K runners list.size() is full, only considering sensor id > min sensor id.
	void update(int runner_id, int sensor_id) {
		runners[runner_id].set_last_sensor(sensor_id);
		sensors[sensor_id].add_runner(runner_id);
		if (num < cap) {
			if (sensor_id == 0) { ++num;}
			update_map(sensor_id, runner_id, sensor_id != 0);		
		}
		// If current ranking number equals to K, then we have to pop the min sensor's last runner id.  
		else {
			if (sensor_id <= min_sensor_id) return;
			if (!runners_sensors_iter.count(runner_id)) {
				runners_sensors_iter.erase(runner_ranking.back());
				sensor_runner_map[min_sensor_id].pop_back();
				runner_ranking.pop_back();
				if (sensor_runner_map[min_sensor_id].empty()) {
					// sensors[min_sensor_id]->next->prev = NULL;
					// sensors[min_sensor_id]->prev = NULL;
					sensor_runner_map.erase(min_sensor_id);
					sensors_end_iter.erase(min_sensor_id);
					++min_sensor_id;
				}	
			}
			update_map(sensor_id, runner_id, runners_iter.count(runner_id));
		}
	}
    
    // How to update runner ranking list?
    // Sensor runner map can be cross linked list, the first is sensor list, each sensor list have a list of runner with runner iterator pointing to runner ranking list.
    // Sensor runner map maintains the size of K from max_sensor_id to min_sensor_id.
    // Runner Sensors iterator means that each runner corresponds to an iterator pointing to sensor's list.
    // If sensors'list empty, do not need to delete the empty entry
	void update_map(int sid, int rid, bool do_erase) {
		// Erase the runner id, if the runner exists in ranking list before
		if (do_erase) {
			auto& p = runners_sensors_iter[rid];
			runner_ranking.erase(p->second);
			sensor_runner_map[sid-1].erase(p);
			runners_sensors_iter.erase(rid);
			// If sid-1 have no runner in list, erase the sensor entry
			if (sensor_runner_map[sid-1].empty()) {
				//if (sensors[sid-1]->prev) { }
				sensor_runner_map.erase(sid-1);
			}
		}

		if (sid > max_sensor_id) {
			max_sensor_id = sid;
			auto pos = runner_ranking.insert(runner_ranking.begin(), rid);
		} else {
			int sid_tmp = sid;
			while (!sensor_runner_map.count(sid_tmp)) { ++sid_tmp};
			auto iter = sensor_runner_map[sid_tmp].back().second;
			++iter;
			auto pos = runner_ranking.insert(iter, rid);
		}
        
		sensor_runner_map[sid].emplace_back({rid, pos});
		runners_sensors_iter[rid] == sensor_runner_map[sid].end()-1;
	}

	list<int> get_top_K_runners() const { return runner_ranking;}								// From No. 1 to No. K

private:
	int cap;																					// Keep tracks top cap ranking
	int num;																					// Current top num ranking available
	int max_sensor_id;
	int min_sensor_id;
	vector<Runner*> runners;																	// Pointers to runner info
	vector<Sensor*> sensors;
    // runner_ranking list is the runner's current location.
	list<int> runner_ranking;                                                                   // Sensor list to find non empty sensors
	unordered_map<int, list<pair<int, list<int>::iterator>>> sensor_runner_map;					// Sensor Runner Map, key: sensor, value: pair, runner and ranking iter
	unordered_map<int, list<int>::iterator> runners_sensors_iter;								// Record runner position in sensor list
}

class Runner {
public:
	Runner(int x): id(x), last_sensor(-1) {}

	void set_last_sensor(int sensor_id) { last_sensor = sensor_id;}
private:
	int id;
	int last_sensor;
};

class Sensor {
public:
	Sensor(int sid): id(sid) {}
	void add_runner(int rid) { runner_list.emplace_back(rid);}

private:
	int id;
	// Sensor *prev, *next;
	vector<int> runner_list;
};


int main() {
	Marathon m;
}
