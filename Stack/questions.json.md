由於 JSON 格式繁複且篇幅較長，為了確保內容品質與格式正確，我將分批次產出。以下是第一批次（第 1 至 5 題），涵蓋 Stack 的基礎觀念、複雜度分析與常見應用。

```json
[
  {
    "no": "1",
    "level": "easy",
    "keywords": "Data Structure, Stack, LIFO, Concept",
    "parentNo": null,
    "images": null,
    "codeSnippet": null,
    "question": [
      {
        "t": "堆疊 (Stack) 是一種遵循特定操作順序的線性資料結構。",
        "en": "A Stack is a linear data structure that follows a particular order in which the operations are performed.",
        "wg": [
          {"t": "線性資料結構", "en": "linear data structure", "ps": "N"},
          {"t": "遵循", "en": "follows", "ps": "V"}
        ]
      },
      {
        "t": "請問下列哪一個縮寫最能準確描述堆疊的運作原則？",
        "en": "Which of the following acronyms best describes the working principle of a Stack?",
        "wg": [
          {"t": "縮寫", "en": "acronym", "ps": "N"},
          {"t": "運作原則", "en": "working principle", "ps": "N"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) FIFO (先進先出)",
        "en": "(A) FIFO (First In, First Out)",
        "wg": []
      },
      {
        "t": "(B) LIFO (後進先出)",
        "en": "(B) LIFO (Last In, First Out)",
        "wg": []
      },
      {
        "t": "(C) LRU (最近最少使用)",
        "en": "(C) LRU (Least Recently Used)",
        "wg": []
      },
      {
        "t": "(D) RANDOM (隨機存取)",
        "en": "(D) RANDOM (Random Access)",
        "wg": []
      }
    ],
    "answer": "(B)",
    "why": {
      "t": "堆疊運作於後進先出 (LIFO) 的原則，這意味著最後被加入堆疊的元素將是第一個被移除的。",
      "en": "A Stack operates on the Last In, First Out (LIFO) principle, meaning the last element added to the stack will be the first one to be removed.",
      "wg": [
        {"t": "後進先出", "en": "Last In, First Out", "ps": "N"},
        {"t": "移除", "en": "removed", "ps": "V"}
      ]
    }
  },
  {
    "no": "2",
    "level": "medium",
    "keywords": "Time Complexity, Big O, Push, Pop",
    "parentNo": null,
    "images": null,
    "codeSnippet": null,
    "question": [
      {
        "t": "在實作良好的堆疊中，執行 `push` (推入) 和 `pop` (彈出) 操作的時間複雜度通常為何？",
        "en": "What is the typical time complexity for `push` and `pop` operations in a well-implemented Stack?",
        "wg": [
          {"t": "實作良好", "en": "well-implemented", "ps": "Adj"},
          {"t": "時間複雜度", "en": "time complexity", "ps": "N"}
        ]
      },
      {
        "t": "假設不考慮動態陣列調整大小時的最壞情況。",
        "en": "Assume the worst-case scenario of dynamic array resizing is not considered.",
        "wg": [
          {"t": "動態陣列", "en": "dynamic array", "ps": "N"},
          {"t": "調整大小", "en": "resizing", "ps": "Gerund"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) O(1)",
        "en": "(A) O(1)",
        "wg": []
      },
      {
        "t": "(B) O(n)",
        "en": "(B) O(n)",
        "wg": []
      },
      {
        "t": "(C) O(log n)",
        "en": "(C) O(log n)",
        "wg": []
      },
      {
        "t": "(D) O(n log n)",
        "en": "(D) O(n log n)",
        "wg": []
      }
    ],
    "answer": "(A)",
    "why": {
      "t": "堆疊操作只涉及頂端元素的存取，不需要遍歷整個資料結構，因此其操作是常數時間。",
      "en": "Stack operations only involve accessing the top element and do not require traversing the entire data structure, so the operations are constant time.",
      "wg": [
        {"t": "涉及", "en": "involve", "ps": "V"},
        {"t": "遍歷", "en": "traversing", "ps": "Gerund"},
        {"t": "常數時間", "en": "constant time", "ps": "N"}
      ]
    }
  },
  {
    "no": "3",
    "level": "medium",
    "keywords": "Recursion, Stack Overflow, Memory Management",
    "parentNo": null,
    "images": null,
    "codeSnippet": "void recursiveFunction() {\n    recursiveFunction();\n}",
    "question": [
      {
        "t": "當一個遞迴函式沒有設定終止條件時 (如上方程式碼所示)，會發生什麼情況？",
        "en": "What happens when a recursive function has no termination condition (as shown in the code snippet above)?",
        "wg": [
          {"t": "遞迴函式", "en": "recursive function", "ps": "N"},
          {"t": "終止條件", "en": "termination condition", "ps": "N"}
        ]
      },
      {
        "t": "請從記憶體管理的角度選擇最貼切的錯誤描述。",
        "en": "Please select the most accurate error description from a memory management perspective.",
        "wg": [
          {"t": "記憶體管理", "en": "memory management", "ps": "N"},
          {"t": "觀點", "en": "perspective", "ps": "N"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 記憶體洩漏 (Memory Leak)",
        "en": "(A) Memory Leak",
        "wg": []
      },
      {
        "t": "(B) 堆疊溢位 (Stack Overflow)",
        "en": "(B) Stack Overflow",
        "wg": []
      },
      {
        "t": "(C) 堆積損毀 (Heap Corruption)",
        "en": "(C) Heap Corruption",
        "wg": []
      },
      {
        "t": "(D) 死結 (Deadlock)",
        "en": "(D) Deadlock",
        "wg": []
      }
    ],
    "answer": "(B)",
    "why": {
      "t": "每次函式呼叫都會在呼叫堆疊 (Call Stack) 上佔用一個新的堆疊框架 (Stack Frame)。",
      "en": "Each function call occupies a new stack frame on the Call Stack.",
      "wg": [
        {"t": "呼叫堆疊", "en": "Call Stack", "ps": "N"},
        {"t": "堆疊框架", "en": "Stack Frame", "ps": "N"}
      ]
    },
    "why_2": {
      "t": "無限遞迴會耗盡分配給堆疊的記憶體空間，導致堆疊溢位。",
      "en": "Infinite recursion exhausts the memory space allocated to the stack, leading to a Stack Overflow.",
      "wg": [
        {"t": "耗盡", "en": "exhausts", "ps": "V"},
        {"t": "分配", "en": "allocated", "ps": "V"}
      ]
    }
  },
  {
    "no": "4",
    "level": "medium",
    "keywords": "Application, Parentheses Matching, Algorithm",
    "parentNo": null,
    "images": null,
    "codeSnippet": null,
    "question": [
      {
        "t": "在編寫編譯器或直譯器時，我們需要驗證程式碼中的括號是否成對匹配 (例如：`{ [ ] }` 是合法的，但 `( [ ) ]` 是不合法的)。",
        "en": "When writing a compiler or interpreter, we need to verify if parentheses in the code are matched pairs (e.g., `{ [ ] }` is valid, but `( [ ) ]` is invalid).",
        "wg": [
          {"t": "編譯器", "en": "compiler", "ps": "N"},
          {"t": "直譯器", "en": "interpreter", "ps": "N"},
          {"t": "驗證", "en": "verify", "ps": "V"}
        ]
      },
      {
        "t": "哪種資料結構最適合用來解決這個問題？",
        "en": "Which data structure is most suitable for solving this problem?",
        "wg": [
          {"t": "適合", "en": "suitable", "ps": "Adj"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 佇列 (Queue)",
        "en": "(A) Queue",
        "wg": []
      },
      {
        "t": "(B) 雜湊表 (Hash Map)",
        "en": "(B) Hash Map",
        "wg": []
      },
      {
        "t": "(C) 堆疊 (Stack)",
        "en": "(C) Stack",
        "wg": []
      },
      {
        "t": "(D) 連結串列 (Linked List)",
        "en": "(D) Linked List",
        "wg": []
      }
    ],
    "answer": "(C)",
    "why": {
      "t": "堆疊適合處理巢狀結構。",
      "en": "Stack is suitable for handling nested structures.",
      "wg": [
        {"t": "巢狀結構", "en": "nested structures", "ps": "N"}
      ]
    },
    "why_2": {
      "t": "遇到左括號時推入堆疊，遇到右括號時檢查堆疊頂端是否為對應的左括號，這完全符合 LIFO 特性。",
      "en": "Push onto the stack when a left parenthesis is encountered, and check if the stack top is the corresponding left parenthesis when a right parenthesis is encountered, which perfectly fits the LIFO characteristic.",
      "wg": [
        {"t": "對應的", "en": "corresponding", "ps": "Adj"}
      ]
    }
  },
  {
    "no": "5",
    "level": "hard",
    "keywords": "Expression Evaluation, Postfix, Reverse Polish Notation",
    "parentNo": null,
    "images": null,
    "codeSnippet": "Expression: 3 4 + 2 * 7 /",
    "question": [
      {
        "t": "給定上述的後序運算式 (Postfix Expression / Reverse Polish Notation)，",
        "en": "Given the above Postfix Expression (Reverse Polish Notation),",
        "wg": [
          {"t": "後序運算式", "en": "Postfix Expression", "ps": "N"}
        ]
      },
      {
        "t": "若使用堆疊來進行求值，請問計算結束後，堆疊頂端的最終結果為何？",
        "en": "If a Stack is used for evaluation, what is the final result at the top of the stack after the calculation ends?",
        "wg": [
          {"t": "求值", "en": "evaluation", "ps": "N"},
          {"t": "最終結果", "en": "final result", "ps": "N"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 1",
        "en": "(A) 1",
        "wg": []
      },
      {
        "t": "(B) 2",
        "en": "(B) 2",
        "wg": []
      },
      {
        "t": "(C) 3.5",
        "en": "(C) 3.5",
        "wg": []
      },
      {
        "t": "(D) 14",
        "en": "(D) 14",
        "wg": []
      }
    ],
    "answer": "(B)",
    "why": {
      "t": "計算過程如下：3, 4 推入 -> 遇到 + -> 彈出 4, 3 計算 3+4=7 -> 推入 7。",
      "en": "The calculation process is as follows: Push 3, 4 -> Encounter + -> Pop 4, 3, calculate 3+4=7 -> Push 7.",
      "wg": []
    },
    "why_2": {
      "t": "接著 2 推入 -> 遇到 * -> 彈出 2, 7 計算 7*2=14 -> 推入 14 -> 7 推入 -> 遇到 / -> 彈出 7, 14 計算 14/7=2。",
      "en": "Then push 2 -> Encounter * -> Pop 2, 7, calculate 7*2=14 -> Push 14 -> Push 7 -> Encounter / -> Pop 7, 14, calculate 14/7=2.",
      "wg": []
    }
  }
]
```