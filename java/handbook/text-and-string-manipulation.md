# 字串處理與 Text Blocks 實務 / Text and String Manipulation with Text Blocks

## Mental model｜心智模型

在 Java 中處理字串時，資深工程師的心智模型通常建立在三個核心認知上：**不可變性（Immutability）**、**編譯器優化邊界（Compiler Optimization Boundaries）**，以及**二維文本的視覺化（2D Text Visualization）**。

When handling strings in Java, a senior engineer's mental model is typically built on three core concepts: **Immutability**, **Compiler Optimization Boundaries**, and **2D Text Visualization**.

1. **不可變性與 String Pool (Immutability & String Pool)**
   字串在 Java 中是不可變的。任何修改（如拼接、替換）都會產生新物件。JVM 透過 String Pool 來快取字面值（Literals）以節省記憶體，但這也意味著頻繁的字串操作會產生大量短命物件（Garbage），對 GC 造成壓力。
   Strings are immutable in Java. Any modification (concatenation, replacement) creates a new object. The JVM uses the String Pool to cache literals and save memory, but this also means frequent string manipulations generate a massive amount of short-lived objects (Garbage), putting pressure on the GC.

2. **編譯器優化邊界 (Compiler Optimization Boundaries)**
   現代 Java（Java 9+）的編譯器非常聰明，會利用 `invokedynamic` 與 `StringConcatFactory` 自動將單行內的 `+` 拼接優化得非常高效。然而，編譯器的視角無法跨越「迴圈邊界」。在迴圈內使用 `+` 依然是效能殺手。
   Modern Java compilers (Java 9+) are smart enough to optimize inline `+` concatenations highly efficiently using `invokedynamic` and `StringConcatFactory`. However, the compiler's vision cannot cross "loop boundaries." Using `+` inside a loop remains a performance killer.

3. **二維文本的視覺化 (2D Text Visualization for Text Blocks)**
   將 Text Blocks（Java 15+）視為「二維」的字串。編譯器會根據最左側的非空白字元或結尾的 `"""` 來決定「附帶空白（Incidental Whitespace）」的裁切線。你所見即所得，不再需要滿畫面的 `\n` 與 `+`。
   Treat Text Blocks (Java 15+) as "2D" strings. The compiler determines the cut-off line for "incidental whitespace" based on the leftmost non-whitespace character or the closing `"""`. What you see is what you get, eliminating screens full of `\n` and `+`.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 使用 Text Blocks 處理結構化文本 / Use Text Blocks for Structured Text
在處理 JSON、SQL、HTML 或 XML 等多行文本時，全面改用 Text Blocks，並搭配 `.formatted()` 進行變數替換。
When dealing with multi-line text like JSON, SQL, HTML, or XML, fully migrate to Text Blocks and use `.formatted()` for variable substitution.

```java
// Pattern: Text Blocks + .formatted()
String jsonPayload = """
    {
        "userId": "%s",
        "status": "ACTIVE",
        "roles": ["%s", "%s"]
    }
    """.formatted(userId, primaryRole, secondaryRole);
```

### 2. 現代字串 API 的精準選型 / Precise Selection of Modern String APIs
放棄老舊的 `.trim()` 和 `.length() == 0`，改用具備 Unicode 意識的現代 API。
Abandon the legacy `.trim()` and `.length() == 0`, and use modern, Unicode-aware APIs.
- 使用 `.isBlank()` 來檢查字串是否為空或僅包含空白字元。 / Use `.isBlank()` to check if a string is empty or contains only whitespaces.
- 使用 `.strip()` 取代 `.trim()`（`.strip()` 能正確處理所有 Unicode 空白字元，而 `.trim()` 只能處理 ASCII 空間的空白）。 / Use `.strip()` instead of `.trim()` (`.strip()` correctly handles all Unicode whitespaces, whereas `.trim()` only handles ASCII whitespaces).

### 3. 集合字串拼接的最佳實踐 / Best Practices for Collection String Concatenation
當需要將 `List<String>` 轉換為逗號分隔的字串時，不要手寫迴圈，使用 `String.join` 或 Streams API。
When converting a `List<String>` to a comma-separated string, do not write manual loops; use `String.join` or the Streams API.

```java
List<String> tags = List.of("java", "spring", "backend");

// Best Practice 1: Simple join
String result1 = String.join(", ", tags);

// Best Practice 2: Stream with prefix and suffix
String result2 = tags.stream()
    .map(String::toUpperCase)
    .collect(Collectors.joining(", ", "[", "]")); 
    // Output: [JAVA, SPRING, BACKEND]
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ Anti-pattern 1: 迴圈內的字串拼接 / String Concatenation Inside Loops
這是最常見的效能地雷。在迴圈內使用 `+=` 會在每次迭代時創建新的 `StringBuilder` 和 `String` 物件，導致 $O(N^2)$ 的時間與空間複雜度。
This is the most common performance minefield. Using `+=` inside a loop creates a new `StringBuilder` and `String` object on every iteration, leading to $O(N^2)$ time and space complexity.

```java
// ❌ Bad: Creates O(N^2) garbage
String result = "";
for (String item : items) {
    result += item + ","; 
}

// ✅ Good: Use StringBuilder for loops
StringBuilder sb = new StringBuilder();
for (String item : items) {
    sb.append(item).append(",");
}
```

### ❌ Anti-pattern 2: Text Blocks 的縮排陷阱 / Text Block Indentation Traps
Text Blocks 的縮排是由「最左側邊界」決定的。如果結尾的 `"""` 沒有正確對齊，可能會意外保留或刪除需要的空白。
Text Block indentation is determined by the "leftmost boundary". If the closing `"""` is not aligned correctly, you might accidentally keep or strip necessary whitespaces.

```java
// ❌ Bad: 結尾的 """ 往左退了，導致每一行前面都會多出 4 個空白
// Bad: The closing """ is shifted left, causing 4 extra spaces at the start of each line
String query = """
        SELECT *
        FROM users
    """; 

// ✅ Good: 結尾的 """ 與內容對齊，或獨立一行控制基準線
// Good: The closing """ aligns with the content, or stands alone to control the baseline
String query = """
    SELECT *
    FROM users
    """;
```

### ❌ Anti-pattern 3: 濫用 `String.intern()` / Abusing `String.intern()`
有些開發者為了節省記憶體，對所有動態字串呼叫 `.intern()`。這會導致 String Pool（存在於 Heap 中）過度膨脹，增加 GC 掃描負擔。除非你在做極端場景的記憶體優化（例如快取數百萬個重複的短字串），否則**不要**手動呼叫 `.intern()`。
Some developers call `.intern()` on all dynamic strings to save memory. This bloats the String Pool (which resides in the Heap) and increases GC scanning overhead. Unless you are doing extreme memory optimization (e.g., caching millions of duplicated short strings), **do not** call `.intern()` manually.

---

## Checklists & workflows｜檢查清單與流程

### 字串拼接決策樹 / String Concatenation Decision Tree
- [ ] **單行 / 少量變數拼接？ (Inline / Few variables?)** 👉 直接使用 `+` (Trust the compiler).
- [ ] **在迴圈中動態拼接？ (Dynamic concatenation in a loop?)** 👉 使用 `StringBuilder`.
- [ ] **處理集合或陣列？ (Processing Collections/Arrays?)** 👉 使用 `String.join()` 或 `Collectors.joining()`.
- [ ] **多行文本、SQL、JSON 模板？ (Multi-line text, SQL, JSON templates?)** 👉 使用 `Text Blocks (""")` + `.formatted()`.

### Code Review 檢查清單 / Code Review Checklist
- [ ] **Null-Safety:** 比較字串時，是否將常數放在前面？（例如 `"ACTIVE".equals(status)` 而不是 `status.equals("ACTIVE")`） / *Are constants placed first in string comparisons to prevent NullPointerException?*
- [ ] **Blank Check:** 是否使用了 `StringUtils.isBlank()` 或 Java 11+ 的 `.isBlank()`，而不是危險的 `!= null && !str.isEmpty()`？ / *Are you using `.isBlank()` instead of verbose and error-prone null/empty checks?*
- [ ] **Text Block Escaping:** 在 Text Blocks 中，如果行尾需要避免自動換行，是否使用了 `\` 符號？如果需要保留行尾空白，是否使用了 `\s`？ / *In Text Blocks, did you use `\` to prevent newlines, or `\s` to preserve trailing spaces?*

---

## Real-world examples｜實戰案例

### 實戰 1：重構複雜的 SQL 查詢 / Refactoring Complex SQL Queries

在沒有 Text Blocks 之前，Java 程式碼中的 SQL 往往難以閱讀且容易出錯（忘記加空格）。
Before Text Blocks, SQL in Java code was often unreadable and error-prone (e.g., forgetting spaces).

**Before (Legacy Way):**
```java
String sql = "SELECT u.id, u.name, p.role " +
             "FROM users u " +
             "JOIN profiles p ON u.id = p.user_id " + // 容易漏掉結尾的空白 / Easy to miss trailing space
             "WHERE u.status = ? " +
             "ORDER BY u.created_at DESC";
```

**After (Modern Way):**
```java
// 乾淨、可直接複製到 DataGrip/DBeaver 執行的 SQL
// Clean SQL that can be copy-pasted directly to DataGrip/DBeaver
String sql = """
    SELECT u.id, u.name, p.role
    FROM users u
    JOIN profiles p ON u.id = p.user_id
    WHERE u.status = ?
    ORDER BY u.created_at DESC
    """;
```

### 實戰 2：控制 Text Blocks 的換行與空白 / Controlling Newlines and Spaces in Text Blocks

有時候我們需要寫很長的單行字串，但為了程式碼可讀性希望在編輯器中換行；或者我們需要嚴格保留行尾的空白字元。
Sometimes we need to write a very long single-line string but want to wrap it in the editor for readability; or we need to strictly preserve trailing spaces.

```java
// 使用 \ 來取消自動換行 (Cancel implicit newline)
// 使用 \s 來強制保留空白 (Force preserve space)
String formattedText = """
    This is a very long warning message that \
    should actually be displayed on a single line \
    in the final output.
    
    Name: %s\s
    Age:  %d
    """.formatted(userName, userAge);
```
*(註：上述例子中，`This is a very long...` 在實際輸出時會是單行，而 `Name: %s\s` 確保了替換後若有需要，行尾的空白不會被編譯器優化掉。 / Note: The long message will be a single line in output, and `\s` ensures trailing spaces are not stripped by the compiler.)*