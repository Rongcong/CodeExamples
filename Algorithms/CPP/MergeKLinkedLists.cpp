/** Merge k Linked Lists
 * Author: Rongcong Xu
 * Email: rongcong@umich.edu
 * 
 * Merge k sorted linked lists and return it as one sorted list. Analyze and describe its complexity.
 * 
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    // My solution is to adopt divide and conquer method. 
    ListNode* mergeKLists(vector<ListNode*>& lists) {
        if(lists.empty()) return NULL;
        return divideLists(lists, 0, lists.size()-1);
    }
private:
    // Divide the lists into two halfs until two or one list
    ListNode* divideLists(vector<ListNode*>& lists, int l, int r) {
        // if there are more than two lists in this part, we recursively call divide Lists
        if(r-l>1){
            int mid = (l+r)/2;
            ListNode* lA = divideLists(lists, l, mid);
            ListNode* lB = divideLists(lists, mid+1, r);
            return merge2Lists(lA, lB);
        }
        
        return (r == l) ? lists[l] : merge2Lists(lists[l], lists[r]);
    }
    // Reorder two linked lists into one sorted list, return pointer. Remember to release memory when return. 
    ListNode* merge2Lists(ListNode* lA, ListNode* lB){
        ListNode* dummyHead = new ListNode(0);
        ListNode* cur = dummyHead;
        while(lA && lB) {
            if(lA->val < lB->val){
                cur->next = lA;
                lA = lA->next;
            } else {
                cur->next = lB;
                lB = lB->next;               
            }

            cur = cur->next;
        }
        cur->next = lA ? lA : lB;
        ListNode* head = dummyHead->next;
        delete dummyHead;
        return head;
    }
};