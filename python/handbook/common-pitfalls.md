# 常見反模式與陷阱 / Anti-patterns & Common Pitfalls

在 Python 的靈活性背後，隱藏著一些初學者甚至資深工程師都容易踩到的地雷。本章節不討論語法錯誤，而是聚焦於那些「語法正確但邏輯致命」的設計缺陷。掌握這些反模式（Anti-patterns），能讓你寫出更健壯、可測試且易於維護的程式碼。

## Mental model｜心智模型

要避開 Python 的常見陷阱，必須建立正確的 **執行時機（Execution Timing）** 與 **物件參照（Object Reference）** 心智模型：

1.  **定義時 vs. 執行時 (Definition Time vs. Runtime)**：
    *   Python 的 `def`、`class` 語句是可執行的程式碼。
    *   **關鍵概念**：函式的預設參數（Default Arguments）是在「定義時（Definition Time）」被評估並建立物件，而不是在每次「呼叫時」重新建立。這解釋了為何 Mutable Default Arguments 會導致狀態殘留。

2.  **一切皆物件與參照 (Everything is an Object & Reference)**：
    *   Python 的變數標籤（Label）指向記憶體中的物件。
    *   當你傳遞一個 List 或 Dictionary 進函式時，你傳遞的是參照（Reference）。如果在函式內修改了它，外部的物件也會改變（Side Effect）。

3.  **模組載入機制 (Module Loading)**：
    *   `import` 語句會執行該檔案內的頂層程式碼。
    *   **Circular Import** 通常發生在兩個模組在「載入階段」就互相需要對方已經定義好的符號，導致雞生蛋、蛋生雞的死鎖。

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 Sentinel Value 處理預設參數
當參數需要是 Mutable（如 `list`, `dict`）時，永遠使用 `None` 作為預設值，並在函式內部進行初始化。

```python
# Best Practice
def append_to(element, target: list = None):
    if target is None:
        target = []  # 每次呼叫都會建立新的 list
    target.append(element)
    return target
```

### 2. 依賴注入 (Dependency Injection) 取代 Global State
避免使用 `global` 關鍵字或模組層級的變數來儲存應用程式狀態（如資料庫連線、使用者 Session）。

*   **Pattern**：將狀態封裝在 Class 實例中，或透過函式參數傳遞。
*   **Why**：Global state 會導致單元測試困難（測試間互相干擾）與並發競爭條件（Race Conditions）。

### 3. 解構循環依賴 (Breaking Circular Imports)
當 Module A 需要 Module B，且 Module B 需要 Module A 時：

*   **Refactor (推薦)**：將共用的邏輯或型別定義提取到第三個獨立模組 `common.py` 或 `types.py`。
*   **Type Checking Only**：如果只是為了 Type Hinting 而引入，使用 `TYPE_CHECKING` 區塊。
*   **Delayed Import**：將 import 移至函式或方法內部（僅在必要時使用，會隱藏依賴關係）。

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 僅在靜態分析時載入，執行時不會觸發 Circular Import
    from .other_module import ComplexClass

def process(obj: "ComplexClass"):
    ...
```

### 4. 閉包延遲綁定 (Late Binding Closures) 的解法
在迴圈中建立 lambda 或函式時，變數是透過「名稱」查找，而不是「值」綁定。

```python
# Best Practice: 使用預設參數強制綁定當前值
handlers = []
for i in range(5):
    # i=i 將當下的 i 值綁定到區域變數 i
    handlers.append(lambda x, i=i: x + i)
```

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Mutable Default Arguments (可變預設參數)
這是 Python 面試必考題，也是最常見的 Bug 來源。

*   **Anti-pattern**:
    ```python
    def add_employee(emp, emp_list=[]):
        emp_list.append(emp)
        return emp_list
    
    # 第一次呼叫正常
    print(add_employee("Alice")) # ['Alice']
    # 第二次呼叫驚喜：'Alice' 還在裡面！
    print(add_employee("Bob"))   # ['Alice', 'Bob']
    ```
*   **後果**：所有使用預設值的呼叫都共享同一個 List 物件，導致資料汙染。

### 2. Broad Exception Catching (濫捕異常)
*   **Anti-pattern**:
    ```python
    try:
        do_something()
    except Exception:  # 或更糟：except:
        pass
    ```
*   **後果**：這會吞掉 `SyntaxError` (在某些動態執行情境)、`KeyboardInterrupt` (如果是 bare except) 或其他邏輯錯誤，讓除錯變成地獄。
*   **修正**：只捕捉預期的異常（如 `KeyError`, `ValueError`），或至少在 catch 後記錄完整的 traceback。

### 3. Modifying a List While Iterating (邊迭代邊修改)
*   **Anti-pattern**:
    ```python
    numbers = [1, 2, 3, 4, 5]
    for n in numbers:
        if n % 2 == 0:
            numbers.remove(n) # 這會導致索引跳號，漏掉檢查某些元素
    ```
*   **修正**：迭代副本 `for n in numbers[:]:` 或使用 List Comprehension 產生新列表。

### 4. Shadowing Built-ins (遮蔽內建函式)
*   **Anti-pattern**:
    ```python
    id = 123          # 遮蔽了內建的 id()
    list = [1, 2, 3]  # 遮蔽了 list() 建構式
    str = "hello"     # 遮蔽了 str()
    ```
*   **後果**：當你後續試圖使用 `list(some_iterable)` 轉換資料時，會拋出 `TypeError: 'list' object is not callable`。

## Checklists & workflows｜檢查清單與流程

在 Code Review 或重構階段，請使用以下清單自我檢核：

### 程式碼安全性與穩定性檢查
- [ ] **預設參數檢查**：搜尋函式定義 `def .*=.*:`，檢查是否有 `=[]` 或 `={}`。
- [ ] **全域變數檢查**：搜尋 `global` 關鍵字。是否有更好的設計（如 Class 屬性或 ContextVar）可以取代？
- [ ] **異常處理檢查**：搜尋 `except Exception` 或 `except:`。是否真的需要捕捉所有錯誤？是否有 Log 紀錄？
- [ ] **命名檢查**：變數名稱是否遮蔽了 `id`, `type`, `list`, `dict`, `str`, `input` 等內建關鍵字？
- [ ] **迭代修改檢查**：是否有迴圈在迭代容器（List/Dict）的同時，對該容器進行 `remove` 或 `pop` 操作？

### Circular Import 排除流程
當遇到 `ImportError: cannot import name X` 時：
1.  **畫出依賴圖**：A -> B -> A。
2.  **辨識共同點**：A 和 B 是否都依賴某個共用的資料結構或常數？
3.  **提取 (Extract)**：建立 Module C，將共用部分移入 C。
4.  **重構**：讓 A -> C, B -> C。
5.  **最後手段**：若無法提取，考慮將 import 語句移入函式內部（Local Import）。

## Real-world examples｜實戰案例

### 案例 1：Singleton 的誤用與測試災難

**情境**：一個網路爬蟲專案，使用全域變數 `_cache = {}` 來儲存已爬取的 URL。

```python
# bad_crawler.py
_cache = {}

def crawl(url):
    if url in _cache:
        return _cache[url]
    # ... fetching logic ...
    _cache[url] = result
    return result
```

**問題**：
當撰寫單元測試時，Test A 跑完後 `_cache` 裡面有髒資料，導致 Test B 預期會發送請求卻直接讀到 Cache，測試莫名失敗。

**重構方案 (Dependency Injection)**：

```python
# good_crawler.py
class Crawler:
    def __init__(self, cache: dict = None):
        self.cache = cache if cache is not None else {}

    def crawl(self, url):
        if url in self.cache:
            return self.cache[url]
        # ... logic ...
        self.cache[url] = result
        return result

# 測試時可以輕鬆隔離
def test_crawl_new_url():
    crawler = Crawler(cache={}) # 乾淨的環境
    # ...
```

### 案例 2：Django/FastAPI 中的 Circular Import

**情境**：`User` Model 需要引用 `Post` Model (一對多)，而 `Post` Model 的某個方法又需要引用 `User` Model (例如檢查權限)。

**Anti-pattern (直接引用)**：
*   `models/user.py`: `from .post import Post`
*   `models/post.py`: `from .user import User` -> **Crash!**

**重構方案 (字串參照與 TYPE_CHECKING)**：

```python
# models/post.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 僅供 IDE 和 MyPy 使用
    from .user import User

class Post:
    # 在 ORM 定義關聯時使用 "字串" 類別名稱，框架會延遲解析
    author = ForeignKey("User", on_delete=CASCADE)

    def can_edit(self, user: "User") -> bool:
        return self.author_id == user.id
```

### 案例 3：File Handle 洩漏

**情境**：開啟檔案後發生異常，導致檔案未關閉。

```python
# Anti-pattern
f = open('data.txt', 'w')
f.write(content) # 如果這裡爆錯，f.close() 永遠不會執行
f.close()
```

**Best Practice (Context Manager)**：

```python
# 即使發生異常，__exit__ 也會確保檔案被關閉
with open('data.txt', 'w') as f:
    f.write(content)
```