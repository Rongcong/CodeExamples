/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    /* Iterative solution for divide-and-conquer method
     * According to the problem, we can only use constant memory and since recursive method will not achieve constant memory,
     * iterative divde-and-conquer will be the best choice. 
     *
     * This is a bottom-up solution. We arrange small unit(seg_size represent sorted array unit size) by swapping and then mergging, and then swapping again and merge.
     */
    ListNode* sortList(ListNode* head) {
        // If list only contains less than 2 elements, we just return the head. 
        if (!head || !head->next) 
            return head;
            
        ListNode *left, *right, *next, **end, **mid, **cur = &head;
        int i, seg_size = 1;
        
        while (true) {
            for (i = 0, mid = cur; i < seg_size && *mid; ++i, mid = &(*mid)->next);
            
            if (i < seg_size || !*mid) {
                if (*cur == head) 
                    return head;
                    
                seg_size *= 2; 
                cur = &head; 
                continue;                 
            }
            // Find the end of the list 
            for (i = 0, end = mid; i < seg_size && *end; i++, end = &(*end)->next); 
            // Assign the cur(start) to the left, and mid to the right and next to the end
            left = *cur, right = *mid, next = *end;
            *mid = *end = NULL;
            // Merge left and right lists into one list
            while (left && right) {
                if (left->val < right->val) { 
                    *cur = left; 
                    left = left->next; 
                }
                else { 
                    *cur = right; 
                    right = right->next; 
                }
                cur = &(*cur)->next;
            }
            // Either left or right list will be empty, insert rest nodes into list
            *cur = left ? left : right;
            // ListNode* cend = left ? *mid : *end;
            while (*cur) 
                cur = &(*cur)->next;
                
            *cur = next;
        }
    }
};