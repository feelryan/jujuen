# AI 驅動的測試策略與案例生成 / AI-Driven Testing Strategies & Case Generation

## Mental model｜心智模型

在引入 AI 輔助測試時，工程師的角色從「測試撰寫者 (Test Writer)」轉變為「測試策展人 (Test Curator)」與「測試架構師 (Test Architect)」。

### 1. The Adversarial Partner (對抗性夥伴)
不要只讓 AI 驗證你的程式碼是對的（Confirmation Bias），要利用 AI 找出你的程式碼哪裡會錯。將 AI 視為一個不知疲倦的 QA 工程師，專門負責挑戰你的邏輯漏洞。
> **Shift:** Instead of asking "Write a test for this function," ask "What are the edge cases and potential failure modes for this logic?"

### 2. White-Box Knowledge, Black-Box Testing (白箱知識，黑箱測試)
雖然我們將原始碼（白箱）提供給 AI，但在生成測試時，應明確指示 AI 採取「黑箱」視角——關注公開介面 (Public Interface) 的行為與回傳值，而非內部實作細節。這能避免生成出脆弱 (Brittle) 的測試。

### 3. The "Arrange-Act-Assert" Generator
AI 非常擅長處理測試中的樣板代碼 (Boilerplate)。你的心智模型應該是：
- **Human**: 定義測試場景 (Scenarios) 與斷言邏輯 (Assertion Logic)。
- **AI**: 生成繁瑣的 Setup (Mock data, Dependencies) 與 Teardown。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Edge Case Discovery Pattern (邊界案例探索模式)
人類開發者常陷入 "Happy Path" 思維。使用 AI 來窮舉邊界條件。
- **Prompt 技巧**: "Analyze the following function. List 5-10 edge cases, including boundary values, null/undefined inputs, and malformed data structures. Then generate unit tests for these cases."
- **應用**: 複雜的表單驗證、數學運算、日期時間處理。

### 2. Data-Driven / Parameterized Testing (資料驅動測試)
AI 非常擅長將單一測試案例擴展為參數化測試 (Parameterized Tests)。
- **做法**: 給 AI 一個基礎測試，要求它將其重構為 Table-driven test (如 Jest 的 `test.each` 或 Pytest 的 `@pytest.mark.parametrize`)，並自動填入多組測試數據。

### 3. Synthetic Mock Data Generation (合成 Mock 資料生成)
手寫巨大的 JSON Mock 或 SQL Insert 語句非常痛苦且容易出錯。
- **Pattern**: 提供 TypeScript Interface 或 Database Schema，要求 AI 生成符合特定情境（如：缺少欄位、超長字串、特殊字元）的 Mock Data。
- **Prompt**: "Generate a JSON object compliant with this Interface for a user who has a strictly valid profile but an expired credit card."

### 4. Characterization Testing for Legacy Code (遺留代碼的特徵測試)
面對沒有測試的遺留代碼 (Legacy Code)，在重構前需要先確保行為不變。
- **做法**: 將舊程式碼貼給 AI，要求："Write a test suite that captures the *current* behavior of this code, bugs and all. Do not fix the bugs yet."
- 這建立了安全網 (Safety Net)，讓你可以放心地進行後續重構。

### 5. Testing the "Untestable" (測試難以測試的部分)
對於 Regex (正規表達式) 或複雜的 SQL 查詢，AI 是極佳的解釋器與測試生成器。
- **做法**: "Explain this Regex, then generate a set of strings that match it and a set of strings that should fail but look similar."

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Mirror Test (鏡像測試 / 同義反覆)
AI 有時會直接把實作邏輯複製貼上變成測試邏輯。
- **症狀**: 測試碼與實作碼長得一模一樣。
- **後果**: 這種測試毫無價值，因為如果實作寫錯了，測試也會跟著錯（False Positive）。
- **解法**: 審查時確認測試是否真的在驗證「預期行為」，而不僅僅是重複「實作步驟」。

### 2. Testing Implementation Details (測試實作細節)
AI 為了追求覆蓋率，常會 Mock 私有方法 (Private Methods) 或依賴特定的內部變數狀態。
- **後果**: 重構代碼時，功能沒壞但測試全紅了 (Brittle Tests)。
- **解法**: 在 Prompt 中明確限制："Only test the public API. Do not mock private functions unless absolutely necessary."

### 3. Hallucinated APIs (幻覺 API)
AI 可能會使用該測試框架中不存在的斷言方法 (Matchers) 或錯誤的 Mock 語法。
- **例子**: 在 Jest 中使用了 Pytest 風格的斷言，或者捏造了一個不存在的 `.toBeApproximatelyCloseTo()`。
- **解法**: 始終運行測試。不要相信 AI 寫的測試能直接跑通。

### 4. Context Leakage in Mocks (Mock 資料洩漏)
- **風險**: 為了讓 AI 生成測試，開發者不小心貼上了含有真實個資 (PII) 或 Production Database 的資料作為範例。
- **解法**: 使用 AI 前先進行資料脫敏 (Sanitization)，或要求 AI "Generate generic dummy data based on this structure."

---

## Checklists & workflows｜檢查清單與流程

### Workflow: AI-Assisted Test Driven Development (AI-TDD)

1.  **Draft Interface**: 寫下函數簽名 (Signature) 與註解 (Docstring) 描述預期行為。
2.  **Generate Tests**: 要求 AI 根據簽名生成 "Happy Path" 與 "Edge Cases" 測試。
3.  **Review & Refine**: 人工審查測試邏輯，刪除測試實作細節的部分。
4.  **Implement**: 撰寫程式碼直到測試通過（或讓 AI 根據測試寫實作）。
5.  **Expand**: 要求 AI 補充更多邊界案例或參數化測試。

### Checklist: Reviewing AI-Generated Tests

- [ ] **可執行性 (Executability)**: 測試真的能跑嗎？是否有引用不存在的 library 或 helper function？
- [ ] **獨立性 (Isolation)**: 測試是否依賴外部真實 API 或資料庫？（AI 是否忘記 Mock 外部依賴？）
- [ ] **斷言有效性 (Assertion Validity)**: 斷言 (Assert) 是否真的驗證了關鍵邏輯？還是只是檢查了 `returnValue is not null` 這種無效驗證？
- [ ] **可讀性 (Readability)**: 測試描述 (Test Description) 是否清晰說明了「在什麼情況下 (Given)，做什麼 (When)，預期什麼 (Then)」？
- [ ] **隱私安全 (Privacy)**: 生成的 Mock Data 是否包含敏感資訊或看起來太像真實數據？

---

## Real-world examples｜實戰案例

### Example 1: Generating Edge Cases for Business Logic

**Scenario**: 一個計算購物車折扣的函數，邏輯複雜（滿額折、VIP 折、排除特定商品）。

**Prompt**:
```text
I have a function `calculateCartTotal(cart: Cart, user: User): number`.
Business rules:
1. 10% off if total > $100.
2. VIP gets an extra 5% off.
3. Items tagged 'on_sale' do not count towards the $100 threshold but still get the VIP discount.

Please generate a set of Jest test cases covering:
1. Standard happy paths.
2. Edge cases (e.g., total exactly $100, empty cart, user is null).
3. Complex combinations (VIP user with only 'on_sale' items).
Use `test.each` for better readability.
```

**Result (Concept)**: AI 會生成一個清晰的 Table-driven test，幫你列出你可能漏掉的組合（例如：剛好 $100 元是否打折？）。

### Example 2: Mocking Complex Data

**Scenario**: 前端需要測試一個顯示使用者儀表板的 Component，後端 API 回傳結構很深。

**Prompt**:
```text
Here is the TypeScript interface for the UserDashboard response:
[Paste Interface Code...]

Create a mock data object named `mockRiskyUser` representing a user who:
1. Has a 'suspended' account status.
2. Has 0 recent transactions.
3. Has a 'null' avatar URL.
4. Has a last login date in the future (invalid data case).
```

### Example 3: Converting Bug Reports to Test Cases

**Scenario**: 收到一個 Bug Report，使用者輸入含有 Emoji 的字串導致系統崩潰。

**Prompt**:
```text
We found a bug where emoji input crashes the `sanitizeInput` function.
Here is the current function: [Paste Code].

Please write a failing unit test that reproduces this bug using various emoji and special unicode characters.
Then, suggest a fix for the function to make the test pass.
```

**Value**: 這不僅修復了 Bug，還自動建立了一個「回歸測試 (Regression Test)」，防止未來再次發生同樣錯誤。