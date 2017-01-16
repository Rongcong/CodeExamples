#include <deque>
#include <iostream>
#include <vector>

using namespace std;

class Scheduler {
public:
	vector<vector<pair<int, int>>> schedule_game(int n){
		vector<vector<pair<int, int>>> rst(n-1);
		deque<int> dq1, dq2;

		for(int i=0; i<n/2; i++) {
			dq1.push_back(i);
			dq2.push_back(i+n/2);
		}

		auto it1 = dq1.begin();
		++it1;

		for(int i=0; i<n-1; i++){
			for(int j=0; j<n/2; j++)
				rst[i].push_back({dq1[j], dq2[j]});

			dq1.insert(it1, dq2.front());
			dq2.pop_front();
			dq2.push_back(dq1.back());
			dq1.pop_back();
		}
		
		return rst;
	}
};

int main() {
	Scheduler s1;
	vector<vector<pair<int,int>>> rst = s1.schedule_game(4);

	for (int i = 0; i < n-1; i++){
		for (auto &p : rst[i]) {
			cout << p.first << " vs "<< p.second << " ";
		}
		cout << endl;
	}

	return 0;
}