/* 	Design a simplified version of Twitter where users can post tweets, follow/unfollow another user and is able to see the 10 most recent tweets in the user's news feed. Your design should support the following methods:
 *
 * 	postTweet(userId, tweetId): Compose a new tweet.
 * 	getNewsFeed(userId): Retrieve the 10 most recent tweet ids in the user's news feed. Each item in the news feed must be posted by users who the user followed or by the user herself. Tweets must be ordered from most recent to least recent.
 * 	follow(followerId, followeeId): Follower follows a followee.
 * 	unfollow(followerId, followeeId): Follower unfollows a followee.
 *
 * 	Twitter twitter = new Twitter();
 *
 * 	// User 1 posts a new tweet (id = 5).
 *	twitter.postTweet(1, 5);
 *
 *	// User 1's news feed should return a list with 1 tweet id -> [5].
 *	twitter.getNewsFeed(1);
 *
 *	// User 1 follows user 2.
 *	twitter.follow(1, 2);
 *
 *	// User 2 posts a new tweet (id = 6).
 *	twitter.postTweet(2, 6);
 *
 *	// User 1's news feed should return a list with 2 tweet ids -> [6, 5].
 *	// Tweet id 6 should precede tweet id 5 because it is posted after tweet id 5.
 *	twitter.getNewsFeed(1);
 *
 *	// User 1 unfollows user 2.
 *	twitter.unfollow(1, 2);
 *
 *	// User 1's news feed should return a list with 1 tweet id -> [5],
 *	// since user 1 is no longer following user 2.
 *	twitter.getNewsFeed(1);
 */

class Tweet {
public:
    // Every tweet should keep track of tweetID and timestamp
	Tweet(int tweetId, int timestamp) {
		this->tweetId = tweetId;
		this->timestamp = timestamp;
		next = nullptr;
	}
	// Allow user and twitter to access tweet's protected/private member
	friend class User;
	friend class Twitter;
private:
	int tweetId;
	int timestamp;
	Tweet *next;
};

class User {
    /* What users need to do? Basic: Post tweets, follow and unfollow (Remove tweets?).  
     * What actions should a user have? 
     * A user should have constructor, destructor, follow, unfollow. 
     */
public:
    // User should keep track of its tweets and its followers
    // Since users do not know how many tweets will be, it's better to use linked lists
    // We do not need to keep followers in any order, we can use a hash map to keep track of followees including itself. 
    // Initialize a user, we only need its' userId. 
	User(int userId) {
		this->userId = userId;
		tweetsHead = nullptr;
		followees.insert(userId);//first follow himself
	}
	// When we delete a user, we need to destory all user's tweets. 
	~User(){
		Tweet* tmp = tweetsHead;
		while (tweetsHead) {
			tmp = tweetsHead->next;
			delete tweetsHead;
			tweetsHead = tmp;
		}
	}
	// When a user post, we need to create a new Tweet node and replace the first node with the new node.
	void post(int tweetId, int timestamp) {
		Tweet *t = new Tweet(tweetId, timestamp);
		t->next = tweetsHead;
		tweetsHead = t;
	}
	// Hash function is fast for random access with key.
	void follow(int followeeId) {
		followees.insert(followeeId);
	}
	// If we unfollow, just delete the key in hash set. 
	void unfollow(int followeeId) {
		if(followees.count(followeeId) && followeeId != userId) followees.erase(followeeId);
	}
	// Allow twitter to access user's private member. 
	friend class Twitter;
private:
	int userId;
	Tweet *tweetsHead;
	unordered_set<int> followees;
};

class Twitter {
public:
	/** Initialize your data structure here. */
	Twitter() {

	}
	
	~Twitter() {
		for (auto& p : userMap) {
			delete p.second;
		}
	}
	/** Compose a new tweet. */
	void postTweet(int userId, int tweetId) {
		if (!userMap.count(userId)) {
			User *newUser = new User(userId);
			userMap[userId] = newUser;
		}
		userMap[userId]->post(tweetId, timestamp);
		++timestamp;
	}
    //comparator used in priority_queue
    struct Comparator {
		bool operator() (const Tweet* tp1, const Tweet* tp2) {
		    return tp1->timestamp < tp2->timestamp;
		}
	};
	/** Retrieve the 10 most recent tweet ids in the user's news feed. Each item in the news feed must be posted by users who the user followed or by the user herself. Tweets must be ordered from most recent to least recent. */
	vector<int> getNewsFeed(int userId) {
		vector<int> res;
		if (!userMap.count(userId)) return res;
		priority_queue<Tweet*, vector<Tweet*>, Comparator> p;
		for (auto& u : userMap[userId]->followees) {//construct priority queue
			if (userMap[u]->tweetsHead != nullptr) {
			    p.push(userMap[u]->tweetsHead);
			}
		}
		for (int i = 0; i < 10 && !p.empty(); ++i) {
			Tweet* t = p.top();
			res.push_back(t->tweetId);
			p.pop();
			if (t->next) p.push(t->next);
		}
		return res;
	}

	/** Follower follows a followee. If the operation is invalid, it should be a no-op. */
	void follow(int followerId, int followeeId) {
		if (!userMap.count(followerId)) {
			User *u = new User(followerId);
			userMap[followerId] = u;
		}
		if (!userMap.count(followeeId)) {
			User *u = new User(followeeId);
			userMap[followeeId] = u;
		}
		userMap[followerId]->follow(followeeId);
	}

	/** Follower unfollows a followee. If the operation is invalid, it should be a no-op. */
	void unfollow(int followerId, int followeeId) {
		if (!userMap.count(followerId) || !userMap.count(followeeId)) 
		    return;
		
		userMap[followerId]->unfollow(followeeId);
	}
private:
    // Global time stamp. 
	int timestamp = 0;
	// Hash map to associate userId with User instances.
	unordered_map<int, User*> userMap;
};
/**
* Your Twitter object will be instantiated and called as such:
* Twitter obj = new Twitter();
* obj.postTweet(userId,tweetId);
* vector<int> param_2 = obj.getNewsFeed(userId);
* obj.follow(followerId,followeeId);
* obj.unfollow(followerId,followeeId);
*/