這是一個非常好的練習方式。由於 JSON 格式繁瑣且內容較多，為了確保品質並避免輸出截斷，我將分批次產出。

以下是 **第一批次 (第 1 至 5 題)**，涵蓋了 Two Pointers 的基礎概念、對撞指標 (Opposite Direction)、快慢指標 (Fast-Slow Pointers) 以及其在陣列與鏈結串列中的應用。

```json
[
  {
    "no": "1",
    "level": "easy",
    "keywords": "Two Pointers, Array, Sorted, Time Complexity",
    "parentNo": null,
    "images": null,
    "codeSnippet": "Input: numbers = [2,7,11,15], target = 9\nOutput: [1,2] (1-based index)",
    "question": [
      {
        "t": "給定一個已按非遞減順序排列的整數陣列，請找出兩個數，使它們相加等於特定的目標數。",
        "en": "Given an array of integers that is already sorted in non-decreasing order, find two numbers such that they add up to a specific target number.",
        "wg": [
          {"t": "非遞減順序", "en": "non-decreasing order", "ps": "N"},
          {"t": "整數陣列", "en": "array of integers", "ps": "N"}
        ]
      },
      {
        "t": "您需要返回這兩個數的索引（以 1 為起始），且必須使用常數額外空間。",
        "en": "You need to return the indices of the two numbers (1-based) and must use constant extra space.",
        "wg": [
          {"t": "索引", "en": "indices", "ps": "N"},
          {"t": "常數額外空間", "en": "constant extra space", "ps": "N"}
        ]
      },
      {
        "t": "請問下列哪種方法最能滿足時間與空間複雜度的要求？",
        "en": "Which of the following approaches best meets the time and space complexity requirements?",
        "wg": [
          {"t": "複雜度", "en": "complexity", "ps": "N"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 使用巢狀迴圈檢查每一對組合，時間複雜度為 O(n^2)。",
        "en": "(A) Use nested loops to check every pair, with a time complexity of O(n^2).",
        "wg": [
          {"t": "巢狀迴圈", "en": "nested loops", "ps": "N"}
        ]
      },
      {
        "t": "(B) 使用雜湊表儲存已訪問過的數字，時間複雜度 O(n)，空間複雜度 O(n)。",
        "en": "(B) Use a hash map to store visited numbers, with time complexity O(n) and space complexity O(n).",
        "wg": [
          {"t": "雜湊表", "en": "hash map", "ps": "N"}
        ]
      },
      {
        "t": "(C) 使用雙指標，一個指向開頭，一個指向結尾，根據和的大小移動指標，時間複雜度 O(n)，空間複雜度 O(1)。",
        "en": "(C) Use two pointers, one at the start and one at the end, moving pointers based on the sum, with time complexity O(n) and space complexity O(1).",
        "wg": [
          {"t": "雙指標", "en": "two pointers", "ps": "N"}
        ]
      },
      {
        "t": "(D) 使用二分搜尋法針對每個元素尋找差值，時間複雜度 O(n log n)。",
        "en": "(D) Use binary search for the complement of each element, with time complexity O(n log n).",
        "wg": [
          {"t": "二分搜尋法", "en": "binary search", "ps": "N"},
          {"t": "差值", "en": "complement", "ps": "N"}
        ]
      }
    ],
    "answer": "(C)",
    "why": {
      "t": "因為陣列已經排序，我們可以利用雙指標技巧。若兩數之和大於目標，則移動右指標向左使和變小；若小於目標，則移動左指標向右使和變大。這能在線性時間內完成且不需額外空間。",
      "en": "Since the array is sorted, we can use the two pointers technique. If the sum is greater than the target, move the right pointer left to decrease the sum; if less, move the left pointer right to increase it. This runs in linear time without extra space.",
      "wg": [
        {"t": "線性時間", "en": "linear time", "ps": "N"}
      ]
    }
  },
  {
    "no": "2",
    "level": "medium",
    "keywords": "Two Pointers, In-place, Array, Duplicates",
    "parentNo": null,
    "images": null,
    "codeSnippet": "int removeDuplicates(vector<int>& nums);",
    "question": [
      {
        "t": "在一個已排序的陣列中，您需要原地刪除重複出現的元素，使得每個元素只出現一次。",
        "en": "Given a sorted array, you need to remove the duplicates in-place such that each element appears only once.",
        "wg": [
          {"t": "原地", "en": "in-place", "ps": "Adv"},
          {"t": "重複出現的", "en": "duplicates", "ps": "N"}
        ]
      },
      {
        "t": "返回移除後陣列的新長度。您不可以使用額外的陣列空間。",
        "en": "Return the new length of the array after removal. You must not use extra array space.",
        "wg": []
      },
      {
        "t": "在使用雙指標解法時（快慢指標），當 `nums[fast] != nums[slow]` 時，下一步操作應該是什麼？",
        "en": "When using the two pointers approach (fast and slow pointers), what should be the next operation when `nums[fast] != nums[slow]`?",
        "wg": [
          {"t": "快慢指標", "en": "fast and slow pointers", "ps": "N"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 將 `slow` 指標向後移動一步，然後將 `nums[fast]` 的值複製給 `nums[slow]`。",
        "en": "(A) Move the `slow` pointer one step forward, then copy the value of `nums[fast]` to `nums[slow]`.",
        "wg": []
      },
      {
        "t": "(B) 直接將 `nums[fast]` 的值複製給 `nums[slow]`，然後移動 `slow`。",
        "en": "(B) Directly copy the value of `nums[fast]` to `nums[slow]`, then move `slow`.",
        "wg": []
      },
      {
        "t": "(C) 僅移動 `fast` 指標，不做任何複製。",
        "en": "(C) Only move the `fast` pointer without doing any copying.",
        "wg": []
      },
      {
        "t": "(D) 交換 `nums[fast]` 與 `nums[slow]` 的值。",
        "en": "(D) Swap the values of `nums[fast]` and `nums[slow]`.",
        "wg": [
          {"t": "交換", "en": "swap", "ps": "V"}
        ]
      }
    ],
    "answer": "(A)",
    "why": {
      "t": "`slow` 指標維護的是不重複序列的尾端。當發現一個新元素（`nums[fast]` 與當前尾端不同）時，應先擴展不重複區域（`slow++`），再填入新值。",
      "en": "The `slow` pointer maintains the end of the unique sequence. When a new element is found (`nums[fast]` differs from the current end), extend the unique region (`slow++`) first, then fill in the new value.",
      "wg": [
        {"t": "維護", "en": "maintain", "ps": "V"},
        {"t": "序列", "en": "sequence", "ps": "N"}
      ]
    }
  },
  {
    "no": "3",
    "level": "easy",
    "keywords": "Two Pointers, String, Palindrome",
    "parentNo": null,
    "images": null,
    "codeSnippet": "Input: s = \"A man, a plan, a canal: Panama\"\nOutput: true",
    "question": [
      {
        "t": "驗證一個字串是否為迴文，只考慮字母和數字字符，並忽略字母大小寫。",
        "en": "Validate if a string is a palindrome, considering only alphanumeric characters and ignoring cases.",
        "wg": [
          {"t": "迴文", "en": "palindrome", "ps": "N"},
          {"t": "字母和數字", "en": "alphanumeric", "ps": "Adj"}
        ]
      },
      {
        "t": "若使用雙指標法，當左指標指向的字符非字母數字時，應該如何處理？",
        "en": "If using the two pointers method, how should you handle it when the character at the left pointer is non-alphanumeric?",
        "wg": []
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 返回 False，因為字串包含非法字符。",
        "en": "(A) Return False, because the string contains invalid characters.",
        "wg": [
          {"t": "非法字符", "en": "invalid characters", "ps": "N"}
        ]
      },
      {
        "t": "(B) 將左指標向右移動一步，跳過該字符，繼續比較。",
        "en": "(B) Move the left pointer one step to the right to skip the character and continue comparing.",
        "wg": [
          {"t": "跳過", "en": "skip", "ps": "V"}
        ]
      },
      {
        "t": "(C) 將右指標向左移動一步，直到遇到字母數字。",
        "en": "(C) Move the right pointer one step to the left until an alphanumeric character is found.",
        "wg": []
      },
      {
        "t": "(D) 立即終止迴圈並返回 True。",
        "en": "(D) Immediately terminate the loop and return True.",
        "wg": [
          {"t": "終止", "en": "terminate", "ps": "V"}
        ]
      }
    ],
    "answer": "(B)",
    "why": {
      "t": "題目要求忽略非字母數字字符。因此，當指標遇到這類字符時，應直接跳過（移動指標）而不進行比較，直到找到下一個有效字符。",
      "en": "The problem requires ignoring non-alphanumeric characters. Therefore, when a pointer encounters such a character, it should simply skip it (move the pointer) without comparing, until the next valid character is found.",
      "wg": [
        {"t": "有效字符", "en": "valid character", "ps": "N"}
      ]
    }
  },
  {
    "no": "4",
    "level": "medium",
    "keywords": "Two Pointers, Greedy, Array, Container With Most Water",
    "parentNo": null,
    "images": null,
    "codeSnippet": "Input: height = [1,8,6,2,5,4,8,3,7]\nOutput: 49",
    "question": [
      {
        "t": "給定 n 個非負整數代表高度圖，每條垂直線的寬度為 1。",
        "en": "Given n non-negative integers representing an elevation map where the width of each vertical line is 1.",
        "wg": [
          {"t": "非負整數", "en": "non-negative integers", "ps": "N"},
          {"t": "高度圖", "en": "elevation map", "ps": "N"}
        ]
      },
      {
        "t": "找出兩條線，使得它們與 x 軸共同構成的容器可以容納最多的水。",
        "en": "Find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "wg": [
          {"t": "容器", "en": "container", "ps": "N"},
          {"t": "容納", "en": "contain", "ps": "V"}
        ]
      },
      {
        "t": "在使用雙指標（左右兩端向內縮）時，決定移動哪一個指標的正確邏輯是什麼？",
        "en": "When using two pointers (shrinking from both ends), what is the correct logic for deciding which pointer to move?",
        "wg": [
          {"t": "向內縮", "en": "shrinking inward", "ps": "V"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 總是移動高度較高的那個指標。",
        "en": "(A) Always move the pointer with the greater height.",
        "wg": []
      },
      {
        "t": "(B) 總是移動高度較矮的那個指標。",
        "en": "(B) Always move the pointer with the smaller height.",
        "wg": []
      },
      {
        "t": "(C) 同時移動兩個指標。",
        "en": "(C) Move both pointers simultaneously.",
        "wg": [
          {"t": "同時", "en": "simultaneously", "ps": "Adv"}
        ]
      },
      {
        "t": "(D) 隨機移動其中一個指標。",
        "en": "(D) Randomly move one of the pointers.",
        "wg": []
      }
    ],
    "answer": "(B)",
    "why": {
      "t": "容器的容量由較短的板子決定（短板效應）。如果移動較高的板子，寬度變小且高度受限於短板，面積一定變小或不變；只有移動短板，才有可能找到更高的板子來增加面積。",
      "en": "The capacity of the container is determined by the shorter line (bucket effect). If you move the taller line, the width decreases and the height is limited by the shorter line, so the area will decrease or stay the same; only by moving the shorter line is it possible to find a taller line to increase the area.",
      "wg": [
        {"t": "短板效應", "en": "bucket effect", "ps": "N"}
      ]
    }
  },
  {
    "no": "5",
    "level": "medium",
    "keywords": "Two Pointers, Linked List, Cycle Detection, Floyd's Algorithm",
    "parentNo": null,
    "images": null,
    "codeSnippet": "struct ListNode { int val; ListNode *next; };",
    "question": [
      {
        "t": "給定一個鏈結串列的頭節點，判斷該鏈結串列中是否有環（Cycle）。",
        "en": "Given the head of a linked list, determine if the linked list has a cycle in it.",
        "wg": [
          {"t": "鏈結串列", "en": "linked list", "ps": "N"},
          {"t": "環", "en": "cycle", "ps": "N"}
        ]
      },
      {
        "t": "若使用 Floyd 判圈演算法（快慢指標），當快指標與慢指標相遇時，代表什麼？",
        "en": "If using Floyd's Cycle-Finding Algorithm (Fast and Slow Pointers), what does it signify when the fast pointer meets the slow pointer?",
        "wg": [
          {"t": "相遇", "en": "meet", "ps": "V"},
          {"t": "代表", "en": "signify", "ps": "V"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 鏈結串列沒有環，已到達尾端。",
        "en": "(A) The linked list has no cycle and the end has been reached.",
        "wg": []
      },
      {
        "t": "(B) 鏈結串列中有環。",
        "en": "(B) There is a cycle in the linked list.",
        "wg": []
      },
      {
        "t": "(C) 兩個指標都回到了起點。",
        "en": "(C) Both pointers have returned to the starting point.",
        "wg": []
      },
      {
        "t": "(D) 鏈結串列的長度是偶數。",
        "en": "(D) The length of the linked list is even.",
        "wg": []
      }
    ],
    "answer": "(B)",
    "why": {
      "t": "快指標每次移動兩步，慢指標移動一步。如果鏈結串列中有環，快指標最終會「追上」慢指標（進入環中繞圈）；若無環，快指標會先到達 null。",
      "en": "The fast pointer moves two steps at a time, while the slow pointer moves one. If there is a cycle, the fast pointer will eventually 'catch up' to the slow pointer (lapping it inside the cycle); if no cycle, the fast pointer will reach null first.",
      "wg": [
        {"t": "追上", "en": "catch up", "ps": "V"}
      ]
    }
  }
]
```