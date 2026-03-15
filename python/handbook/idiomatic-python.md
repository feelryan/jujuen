# Pythonic 思維與核心慣例 / Idiomatic Python & Core Conventions

## Mental model｜心智模型

要寫出 Pythonic 的程式碼，必須從「翻譯其他語言的邏輯」轉變為「利用 Python 的原生協議（Protocols）」。

### 1. 鴨子型別與協議 (Duck Typing & Protocols)
在 Java 或 C++ 中，我們關注物件的「繼承關係」；在 Python 中，我們關注物件的「行為」。
*   **Mental Shift**: 不要問「這是不是一個 List？」，要問「這能不能被迭代（Iterable）？」。
*   **Magic Methods**: Python 的核心語法（如 `len(x)`, `x[i]`, `for x in obj`）其實都是語法糖，背後對應著 `__len__`, `__getitem__`, `__iter__` 等魔術方法。實作這些方法，你的物件就能像內建型別一樣自然地運作。

### 2. EAFP vs LBYL
*   **LBYL (Look Before You Leap)**: 傳統做法。先檢查條件（if file exists），再執行（open file）。容易產生 Race Condition。
*   **EAFP (Easier to Ask for Forgiveness than Permission)**: Pythonic 做法。直接執行（try open），出了錯再處理（except FileNotFoundError）。這通常更乾淨且效能更好。

### 3. 扁平優於巢狀 (Flat is better than nested)
Python 強調可讀性。如果你的程式碼充滿了深層縮排（Deep Indentation），通常意味著邏輯需要被重構為 Generator、Comprehension 或拆分為函式。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 迭代與生成 (Iteration & Generation)
避免使用 C-style 的索引迴圈，善用 Python 的迭代工具。

*   **Looping**:
    ```python
    # Bad (C-style)
    for i in range(len(items)):
        print(i, items[i])

    # Good (Pythonic)
    for index, item in enumerate(items):
        print(index, item)
    ```
*   **List/Dict Comprehensions**: 用於替代簡單的 `map` 或 `filter` 邏輯，但不要過度巢狀化。
    ```python
    # Good
    names = [user.name for user in users if user.is_active]
    ```

### 2. 裝飾器模式 (Decorators)
將「橫切關注點（Cross-cutting concerns）」如 Log、權限驗證、快取等邏輯從主函式中抽離。

```python
import functools

def retry(max_retries=3):
    def decorator(func):
        @functools.wraps(func) # 保留原函式的 metadata
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    continue
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator

@retry(max_retries=5)
def fetch_data(url):
    pass
```

### 3. 上下文管理器 (Context Managers)
任何涉及「開啟/關閉」、「鎖定/解鎖」、「設定/復原」的資源管理，都應使用 `with` 語句。

*   **Custom Context Manager**: 使用 `contextlib` 簡化實作。
    ```python
    from contextlib import contextmanager

    @contextmanager
    def temp_env_var(key, value):
        import os
        old_value = os.environ.get(key)
        os.environ[key] = value
        try:
            yield
        finally:
            if old_value is None:
                del os.environ[key]
            else:
                os.environ[key] = old_value
    ```

### 4. 屬性存取 (Properties)
不要像 Java 一樣寫顯式的 Getter/Setter 方法。先使用公開屬性（Public Attributes），需要邏輯控制時再轉為 `@property`。

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 可變預設參數 (Mutable Default Arguments)
這是 Python 最經典的陷阱。函式預設參數只會在定義時被評估一次。

*   **Anti-pattern**:
    ```python
    def append_to(element, target=[]): # 所有的 call 都會共用同一個 list
        target.append(element)
        return target
    ```
*   **Correction**:
    ```python
    def append_to(element, target=None):
        if target is None:
            target = []
        target.append(element)
        return target
    ```

### 2. 過度使用 List Comprehension
當邏輯超過兩行，或者包含多層迴圈時，Comprehension 會變得難以閱讀。

*   **Anti-pattern**:
    ```python
    result = [x * y for x in range(10) if x > 5 for y in range(5) if y < 3]
    ```
*   **Correction**: 使用傳統迴圈或將邏輯拆分為 Generator Function。

### 3. 手動管理資源 (Manual Resource Management)
避免使用 `file = open(...)` 然後手動 `file.close()`，因為在發生異常時 `close()` 可能不會被執行。永遠使用 `with open(...)`。

### 4. 濫用 `isinstance` 或 `type`
除非絕對必要，否則不要檢查具體型別。這破壞了鴨子型別（Duck Typing）的靈活性。

*   **Anti-pattern**: `if type(x) == list: ...`
*   **Correction**: 假設它是一個 Iterable，或者使用 `collections.abc` 中的抽象基底類別（如 `Sequence`）進行檢查。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或重構時，使用此清單檢查程式碼是否足夠 Pythonic。

### Code Review Checklist
- [ ] **資源管理**：是否有使用 `try...finally` 來釋放資源（檔案、連線、鎖）？如果是，請改用 Context Manager (`with` statement)。
- [ ] **迴圈邏輯**：是否使用了 `range(len(x))`？如果是，請改用 `enumerate(x)` 或 `zip(x, y)`。
- [ ] **字串串接**：是否在迴圈中使用 `+=` 串接字串？如果是，請改用 `''.join(list)` 以提升效能。
- [ ] **參數陷阱**：是否有使用 Mutable 物件（List, Dict）作為函式預設參數？
- [ ] **魔術方法**：是否實作了自定義類別？如果是，是否實作了 `__repr__` 以便於除錯？
- [ ] **資料結構**：是否使用了大量的 Tuple 索引存取（如 `p[0], p[1]`）？如果是，請考慮使用 `NamedTuple` 或 `dataclass` 增加語意。

### Decision Tree: Choosing the Right Iteration Tool
1. **需要轉換每個元素？** -> Use `map()` or List Comprehension.
2. **需要過濾元素？** -> Use `filter()` or List Comprehension with `if`.
3. **資料量很大或無限？** -> Use Generator Expression `(...)` or `yield`.
4. **需要同時遍歷兩個 List？** -> Use `zip()`.
5. **需要索引值？** -> Use `enumerate()`.

---

## Real-world examples｜實戰案例

### Scenario: Refactoring Legacy Data Processing
將一段充滿 Java 風格的 Python 程式碼重構為 Pythonic 風格。

#### ❌ Before: Verbose & Imperative
```python
class UserDataProcessor:
    def process_users(self, users):
        active_emails = []
        for i in range(len(users)):
            user = users[i]
            if user.get_status() == 'active':
                if user.get_email() != None:
                    active_emails.append(user.get_email().lower())
        return active_emails
```

#### ✅ After: Pythonic & Declarative
```python
class UserDataProcessor:
    def process_users(self, users: list[User]) -> list[str]:
        # 使用 List Comprehension 結合過濾與轉換
        # 假設 User 物件屬性已改為 Property 存取
        return [
            user.email.lower()
            for user in users
            if user.status == 'active' and user.email
        ]
```

### Scenario: Creating a Config Loader (Magic Methods)
讓設定檔物件可以像 Dictionary 一樣被存取，但又具備物件的特性。

```python
class Config:
    def __init__(self, **kwargs):
        self._data = kwargs

    def __getitem__(self, key):
        # 允許 config['db_host'] 存取
        return self._data[key]

    def __getattr__(self, name):
        # 允許 config.db_host 存取
        # 這是 EAFP 的展現：找不到屬性時才觸發此方法
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __repr__(self):
        # 友善的 Debug 訊息
        return f"Config({self._data})"

# Usage
conf = Config(db_host="localhost", db_port=5432)
print(conf.db_host)      # Output: localhost
print(conf['db_port'])   # Output: 5432
```