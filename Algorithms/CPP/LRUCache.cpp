class LRUCache{
    size_t cp;
    unordered_map<int, list<pair<int, int>>::iterator> mp;
    list<pair<int, int>> l;
    
public:
    LRUCache(int capacity): cp(capacity) {}
    
    int get(int key) {
        auto it = mp.find(key);
        if (it != mp.end()){
            l.splice(l.begin(), l, it->second);
            return it->second->second;
        }
            
        return -1;
    }
    
    void set(int key, int value) {
        auto it = mp.find(key);
        if (it != mp.end()) {
            l.splice(l.begin(), l, it->second);
            it->second->second = value;
            return;
        }
        
        if (l.size() < cp)
        {
            l.emplace_front(key, value);
            mp[key] = l.begin();
            return;
        }
        
        mp.erase(l.back().first);
        l.pop_back();
        l.emplace_front(key, value);
        mp[key] = l.begin();
        return;
    }
};

