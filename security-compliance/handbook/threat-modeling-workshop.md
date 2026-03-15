# 威脅建模實戰工作坊 / Practical Threat Modeling Workshop

## Mental model｜心智模型

在進入技術細節之前，我們必須建立正確的心智模型：**威脅建模（Threat Modeling）不是「找駭客來攻擊」，而是一場「結構化的悲觀主義」腦力激盪。**

許多工程師習慣思考「如何讓功能運作（Happy Path）」，而威脅建模要求我們切換視角，思考「如何讓功能壞掉（Adversarial Thinking）」。

### 核心思維：The Four Questions
根據 Adam Shostack 的經典定義，每一場威脅建模工作坊都應該圍繞這四個問題展開：
1.  **What are we building?**（我們在打造什麼？）→ 產出：資料流圖（DFD）。
2.  **What can go wrong?**（哪裡會出錯？）→ 產出：威脅列表（使用 STRIDE）。
3.  **What are we going to do about it?**（我們該如何應對？）→ 產出：緩解措施與工單（Mitigation & Tickets）。
4.  **Did we do a good job?**（我們做得好嗎？）→ 產出：回顧與驗證。

### 信任邊界（Trust Boundaries）
這是威脅建模中最重要的概念。想像你的系統是一座城堡，**信任邊界**就是城牆與護城河。
- 資料在同一個信任區域內流動（例如：後端 Service A 到後端 Service B，且兩者都在私有子網內）通常風險較低。
- **一旦資料跨越了信任邊界**（例如：從公開 Internet 到 API Gateway，或從 Web Server 到 Database），那就是攻擊最可能發生的地方，也是我們檢查的重點。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 儘早開始（Shift Left）
不要等到上線前一週才做。最佳時機是在 **設計階段（Design Phase）**。此時修改架構的成本最低（只是擦掉白板上的線），一旦程式碼寫好，修改成本將是指數級上升。

### 2. 專注於資料流（Data Flow），而非程式流程（Control Flow）
- **Do:** 畫出資料如何從 A 移動到 B（Data Flow Diagram, DFD）。
- **Don't:** 畫出 UML Sequence Diagram 或 Class Diagram。攻擊者關心的是「資料去哪了」以及「誰能接觸到資料」，而不是你的 Class 繼承結構。

### 3. STRIDE 記憶法
在工作坊中，使用 STRIDE 模型來引導討論，確保沒有遺漏常見的攻擊面向：
- **S**poofing (偽冒)：我可以假裝是別人嗎？
- **T**ampering (竄改)：我可以修改傳輸中或儲存的資料嗎？
- **R**epudiation (抵賴)：我做了壞事後，你能證明是我做的嗎？（Log 是否足夠？）
- **I**nformation Disclosure (資訊洩漏)：我能看到我不該看的資料嗎？
- **D**enial of Service (阻斷服務)：我能讓系統崩潰或變慢嗎？
- **E**levation of Privilege (權限提升)：一般使用者能變成管理員嗎？

### 4. 讓開發者主導，資安人員引導
威脅建模不該是資安團隊「審計」開發團隊。它應該是開發團隊「解釋」架構，資安專家協助「提問」。最了解系統弱點的人，往往是寫這段程式碼的人。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 分析癱瘓（Analysis Paralysis）
試圖為整個系統（包含 OS、網路層、硬體）建立完美的模型。
- **後果**：會議超時，產出為零，大家覺得威脅建模是在浪費時間。
- **修正**：專注於**本次變更的範圍**（Scope）。假設底層 OS 和 AWS 基礎設施是安全的（除非你的產品就是 OS），聚焦在你的 Application Layer。

### ❌ 只有問題，沒有行動（Findings without Tickets）
大家在會議中討論得很熱烈，發現了很多漏洞，但會議結束後沒有人記錄。
- **後果**：漏洞依然存在，下次開會還在討論一樣的事。
- **修正**：威脅建模的唯一有效產出是 **Bug Tracking System (Jira/GitHub) 上的 Tickets**。

### ❌ 忽略業務邏輯漏洞
過度專注於技術漏洞（如 SQL Injection），而忽略了業務邏輯（Business Logic）風險。
- **例子**：雖然 API 有防禦 XSS，但允許使用者購買商品時將 `quantity` 設為負數，導致退款給使用者。
- **修正**：STRIDE 中的 Tampering 和 Elevation of Privilege 必須包含業務規則的檢核。

---

## Checklists & workflows｜檢查清單與流程

### 實戰工作坊流程 (Timebox: 60-90 mins)

#### Step 1: 繪製 DFD (15-20 mins)
在白板（或 Miro/Lucidchart）上畫出架構。
- [ ] **External Entities (外部實體)**: 使用者、第三方 API、Cron Jobs。
- [ ] **Processes (處理程序)**: Web Server, Lambda, Microservice。
- [ ] **Data Stores (資料儲存)**: SQL, Redis, S3, Log Files。
- [ ] **Data Flows (資料流)**: 連接上述元件的箭頭。
- [ ] **Trust Boundaries (信任邊界)**: 用虛線畫出不同信任區域（如 Internet vs VPC, User Space vs Kernel Space）。

#### Step 2: 識別威脅 (STRIDE Round-Robin) (30-40 mins)
針對每一個跨越「信任邊界」的資料流，依序問：
- [ ] **S**: 這裡的來源身分驗證（AuthN）夠強嗎？Token 會被竊取嗎？
- [ ] **T**: 這裡的 Input Validation 做了嗎？簽章（Signature）驗證了嗎？
- [ ] **R**: 這筆交易寫入 Audit Log 了嗎？Log 會被刪改嗎？
- [ ] **I**: 傳輸加密（TLS）了嗎？敏感資料是否明文存入 Log？
- [ ] **D**: 如果我在這裡發送 100 萬次請求會怎樣？有 Rate Limiting 嗎？
- [ ] **E**: 這裡的授權檢查（AuthZ）是否依賴前端傳來的參數？

#### Step 3: 決定對策與記錄 (15-20 mins)
針對發現的威脅，決定處理方式：
- [ ] **Mitigate**: 修改設計或程式碼來修復（開 Ticket）。
- [ ] **Eliminate**: 移除該功能或元件以消除風險。
- [ ] **Transfer**: 轉移風險（例如使用 AWS Cognito 而非自建 Auth）。
- [ ] **Accept**: 風險極低，業務決定接受（必須記錄決策與原因）。

---

## Real-world examples｜實戰案例

### 案例：使用者上傳頭像功能 (Profile Picture Upload)

#### 1. Diagram (DFD 描述)
`User (Browser)` --[HTTPS Upload]--> `API Gateway` --[Invoke]--> `Resize Lambda` --[Save]--> `S3 Bucket`

**信任邊界**：
1. Browser 與 API Gateway 之間（Internet 到 VPC）。
2. Lambda 與 S3 之間（運算環境到儲存環境）。

#### 2. Threat Analysis (STRIDE 應用)

| STRIDE 類別 | 潛在威脅 (What can go wrong?) | 緩解措施 (Mitigation) |
| :--- | :--- | :--- |
| **Spoofing** | 惡意使用者 A 呼叫 API，但修改 UserID 參數，假裝是使用者 B 上傳圖片。 | **Check**: 不信任前端傳來的 ID，從 Validated JWT Token 中解析 UserID。 |
| **Tampering** | 使用者上傳一個名為 `image.jpg` 的檔案，但內容其實是 PHP Shell Script。 | **Check**: 驗證 Magic Bytes (File Header) 而非僅驗證副檔名；確保 S3 設為不可執行。 |
| **Info Disclosure** | 上傳失敗時，API 回傳的 Error Message 包含了 Stack Trace 或 S3 Bucket Name。 | **Check**: 實作全域錯誤處理 (Global Error Handler)，僅回傳通用錯誤訊息。 |
| **Denial of Service** | 攻擊者上傳一個 5GB 的超大檔案，耗盡 Lambda 記憶體或頻寬預算。 | **Check**: 在 API Gateway 層級設定 Payload Size Limit (e.g., 5MB)。 |
| **Elevation of Privilege** | 透過上傳覆蓋了系統關鍵檔案（若路徑未妥善處理）。 | **Check**: 檔案重新命名（使用 UUID），不使用使用者提供的原始檔名。 |

#### 3. Output (Action Items)
- [JIRA-101] 實作檔案 Magic Bytes 檢查邏輯。
- [JIRA-102] 設定 API Gateway 上傳大小限制為 5MB。
- [JIRA-103] 確認 S3 Bucket Policy 禁止 `public-read` (除非透過 CloudFront)。