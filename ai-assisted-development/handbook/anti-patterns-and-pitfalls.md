# 常見反模式與幻覺陷阱 / Common Anti-patterns & Hallucination Pitfalls

## Mental model｜心智模型

### 1. 它是「機率鸚鵡」，不是「真理預言家」 (Probabilistic Engine, Not Oracle)
AI 模型（LLM）本質上是一個巨大的「文字接龍」機器。它優化的是**「合理性 (Plausibility)」**而非**「正確性 (Truthfulness)」**。
- **The Gap:** AI 產出的程式碼通常看起來非常正確（語法完美、變數命名合理），這會導致人類大腦放鬆警惕，產生「認知順暢感 (Cognitive Ease)」。
- **The Mindset:** 把 AI 當作一個**「極度自信但偶爾會喝醉的資深實習生」**。它讀過所有的書，但有時候會把兩本書的內容記混，並且在被質疑時會編造藉口。

### 2. 驗證成本不對稱 (Asymmetry of Verification Cost)
生成程式碼的成本趨近於零，但**閱讀與除錯**別人（或 AI）寫的程式碼成本極高。
- 如果你無法在 1 分鐘內理解 AI 生成的 10 行程式碼，你實際上是在引入技術債。
- **Rule of Thumb:** 如果你看不懂，就不要 Commit。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 知識錨定 (Grounding / RAG for Coding)
為了減少幻覺，不要依賴 AI 的「內建記憶」，而是提供「外部真理」。
- **做法：** 在 Prompt 中明確貼上該 Library 的最新官方文件、API 定義或 Interface。
- **Why:** 強迫 AI 根據你提供的上下文生成，而不是根據它 2 年前的訓練數據瞎猜。

### 2. 隔離測試模式 (Isolation Testing Pattern)
不要直接將 AI 生成的程式碼貼入龐大的專案邏輯中。
- **做法：** 要求 AI 同時生成一個單獨的單元測試 (Unit Test) 或小型腳本來驗證該段程式碼。
- **Flow:** `Prompt` -> `Code + Test` -> `Run Test` -> `Verify` -> `Integrate`.

### 3. 蘇格拉底式審查 (Socratic Review)
當 AI 給出解決方案時，反問它。
- **Prompt:** "Are there any edge cases this code misses?" (這段程式碼漏掉了哪些邊界情況？) 或 "Is this method deprecated in the latest version?" (這個方法在最新版棄用了嗎？)
- **Why:** LLM 在「自我反思」模式下，往往能糾正第一輪生成的錯誤。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 幽靈依賴 (The Phantom Dependency / Hallucinated Libraries)
這是最危險的幻覺之一。AI 會編造出**「聽起來很合理但根本不存在」**的函式庫或方法。
- **徵兆：** 程式碼引用了 `import { magicFunction } from 'popular-lib'`，但該 library 根本沒有這個 export。
- **風險：** 輕則報錯，重則遭遇 **Supply Chain Attack**（駭客註冊了 AI 常幻覺出的套件名稱，並植入惡意代碼，等你 `npm install`）。

### 2. 上下文汙染 (Context Pollution)
開發者為了省事，把幾十個無關的檔案全部貼給 AI，希望它修復一個小 bug。
- **後果：** AI 的注意力被分散（Lost in the Middle），開始混淆不同檔案的變數名，或者產出似是而非的架構建議。
- **修正：** 只提供與任務直接相關的 Interface 和邏輯片段。

### 3. 盲目迴圈 (The Doom Loop of Debugging)
當 AI 提供的解法報錯時，開發者直接把錯誤訊息貼回去，AI 給出新解法又報錯，如此反覆。
- **現象：** AI 開始在兩個錯誤解法之間反覆橫跳，或者開始修改原本正確的設定檔。
- **修正：** 停止對話。重新閱讀官方文件，或者開啟一個新的 Chat Session，用更精確的語言描述問題。

### 4. 過度自信的邏輯漏洞 (Confident Logic Gaps)
AI 生成的程式碼跑得動，不會 Crash，但邏輯是錯的。
- **常見案例：**
  - **Off-by-one errors:** 迴圈次數多一次或少一次。
  - **Security Flaws:** 直接使用 `eval()`，或者在 SQL 查詢中沒有使用參數化查詢（因為訓練數據裡有很多不安全的範例）。
  - **Silent Failures:** 錯誤處理只寫了 `try { ... } catch (e) { // do nothing }`。

---

## Checklists & workflows｜檢查清單與流程

在將 AI 程式碼合併到主分支前，請執行 **"A.I.D."** 檢查：

### Accuracy (準確性驗證)
- [ ] **存在性檢查：** 檢查所有 import 的套件、呼叫的函數是否真的存在於官方文件中？（防止幽靈依賴）
- [ ] **版本檢查：** 這是最新語法嗎？還是 3 年前的過時寫法（如 React Class Components vs Hooks）？
- [ ] **邊界檢查：** 輸入為 null、空陣列或極大值時，這段程式碼會崩潰嗎？

### Intent (意圖理解)
- [ ] **可解釋性：** 我能逐行解釋這段程式碼在做什麼嗎？
- [ ] **一致性：** 變數命名風格、錯誤處理方式是否與現有專案一致？

### Defense (防禦性)
- [ ] **無機密洩漏：** 程式碼中是否包含 API Key、密碼或內部 IP？
- [ ] **無安全漏洞：** 是否有 SQL Injection、XSS 或不安全的 Deserialization 風險？

---

## Real-world examples｜實戰案例

### Case 1: The "Perfect" Function that Didn't Exist
**情境：** 開發者詢問如何用 Python 的 `pandas` 處理某種複雜的時間序列轉換。
**AI 回答：**
```python
# AI Generated
import pandas as pd
df = pd.read_csv('data.csv')
# 看起來很合理，名字很像 pandas 風格
df['date'] = df['date'].dt.to_business_day_offset(holidays='US') 
```
**陷阱：** `to_business_day_offset` 根本不存在。Pandas 有類似的功能，但語法完全不同。開發者直接複製貼上，導致 Runtime Error。
**修正：** 查閱 Pandas 官方文檔，確認正確 API 為 `pd.tseries.offsets.CustomBusinessDay`。

### Case 2: The Security Blind Spot
**情境：** 要求 AI 撰寫一個 Node.js 腳本來驗證使用者密碼。
**AI 回答：**
```javascript
// AI Generated
const crypto = require('crypto');
function hashPassword(password) {
  // 使用了快速但不再安全的 MD5，且沒有加 Salt
  return crypto.createHash('md5').update(password).digest('hex');
}
```
**陷阱：** AI 訓練資料中包含大量舊的教學文章，導致它預設使用 MD5。這在現代資安標準下是不合格的。
**修正：** 在 Prompt 中明確要求：「Use bcrypt or argon2 for password hashing with proper salting.」

### Case 3: The Context Confusion
**情境：** 專案中有 `User` (SQL Model) 和 `UserDto` (API Response)。開發者把兩個檔案都貼給 AI，要求寫一個轉換函式。
**AI 幻覺：**
```typescript
// AI 混淆了屬性
function toDto(user: User): UserDto {
  return {
    id: user.id,
    fullName: user.name, // User 模型裡其實叫 'username'
    isActive: user.status === 'ACTIVE' // User 模型裡其實是用 boolean 'is_active'
  };
}
```
**陷阱：** TypeScript 可能會報錯，但在動態語言（如 Python/JS）中，這種錯誤可能直到 Runtime 才會被發現。
**教訓：** 不要假設 AI 能完美記住上下文中的所有欄位名稱，**必須人工比對欄位映射**。