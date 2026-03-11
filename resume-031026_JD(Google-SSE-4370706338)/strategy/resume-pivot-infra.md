# 履歷重構：從 Web App 轉向 Infrastructure/Tools / Resume Pivot: From Web App to Infra/Tools

## Why this matters｜為什麼這個主題重要

這份 Google Cloud JD (Diagnostics, Tools) 與你目前的履歷（Web Application / Full Stack）存在明顯的 **「訊號錯位」（Signal Mismatch）**。

1.  **JD 的核心需求**：強調 "System Programming"（系統程式設計）、"Diagnostics"（診斷）、"Hardware Interaction"（硬體互動）與 "Data Center Automation"（資料中心自動化）。
2.  **你目前的履歷訊號**：強調 "React/Node.js"、"UI Localization"、"Payment Integration" 與 "e-commerce"。
3.  **風險**：若不重構，Recruiter 或 Hiring Manager 可能會認為你是一位優秀的「前端/全端工程師」，但不具備處理底層系統、硬體測試艦隊（Test Fleet）或大規模診斷工具的經驗，導致在簡歷篩選階段被刷掉，或在面試中被問到錯誤方向的問題（如過多前端問題，而非系統設計）。

**本策略的目標**：將你的 "Cloud-Native" 與 "GCP Architect" 經驗重新包裝，從「開發給使用者看的 App」轉向「開發給工程師用的 **Tools** 與 **Infrastructure**」。

---

## Step‑by‑step strategy｜具體行動步驟

建議在 **1-2 週** 內完成以下步驟，針對此職缺客製化一份專用履歷。

### Phase 1: Resume Surgery (履歷手術) - Week 1

1.  **移除/弱化 Web App 關鍵字**：
    *   大幅刪減 `React`、`UI`、`Frontend`、`CSS`、`Payment Gateway` 等字眼。這些對此職缺是雜訊。
    *   將 "Full Stack" 的敘述轉為 "End-to-End System Design"。
2.  **強化 Infrastructure & Automation 關鍵字**：
    *   將重點放在 `GCP`、`Docker`、`CI/CD`、`Pipeline`、`Automation`、`Monitoring`。
    *   針對 JD 中的 "Diagnostics"，回想過去專案中是否有「除錯工具」、「自動化檢測」、「日誌分析系統」的開發經驗，並將其寫成 Bullet points。
3.  **重塑 Chunghwa Telecom (CHT) 的經驗**：
    *   雖然 CHT 是較早期的經歷，但其中的 **IoT/Sensor (e-SAV)** 與 **National Emergency Message Alert** 最接近 JD 要求的 "Hardware Interaction" 與 "High availability"。
    *   **行動**：將這段經歷的技術描述加深，強調「感測器數據處理」、「高併發警報系統」與「系統整合」。

### Phase 2: Narrative Reframing (故事重述) - Week 2

1.  **挖掘 "Internal Tools" 故事**：
    *   JD 提到 "Enhance the diagnostic infrastructure"。回想你在 Innova 或 Hiveel 是否開發過供內部團隊使用的 Dashboard、Script 或自動化流程？
    *   **行動**：將這些「內部工具」的開發經驗提升為主要貢獻，這比「面向客戶的功能」更符合此職缺。
2.  **連結 GCP 證照與實務**：
    *   你有 "Professional Cloud Architect" 證照。在履歷中，不要只列在 Certifications，要在 Experience 中證明你如何應用 GCP 架構觀念來解決「系統診斷」或「效能優化」問題。

---

## Examples & templates｜範例與句型

以下是針對你的履歷內容進行「重構」的具體範例。請參考這些句型修改你的 Bullet Points。

### 1. Innova Solutions (Current Role)
*   **Before (Web App focus):**
    > "Designed and developed features for Imaging Share including backend mechanisms and frontend interactive components. (Ex: UI Localization...)"
*   **After (Infra/Tools focus):**
    > "Engineered **automated infrastructure provisioning workflows** on GCP (Storage Bucket Auto-Creation), reducing customer onboarding time by X%."
    > "Designed **system-level diagnostic mechanisms** for the Imaging Share platform, enabling automated audit reporting and proactively detecting data synchronization failures."
    > "Optimized CI/CD pipelines and integrated **AI-assisted code analysis tools**, enhancing build reliability and developer velocity."

### 2. Chunghwa Telecom (Past Role - Crucial for Hardware/System Signal)
*   **Before (Project Mgmt focus):**
    > "Led architecture/design for e-SAV (Sensor, Alert, Video) cloud platform..."
*   **After (System/Hardware focus):**
    > "Architected a **distributed IoT telemetry platform** (e-SAV) integrating thousands of hardware sensors and video streams for real-time monitoring."
    > "Designed high-throughput interfaces for the National Emergency Message Alert System, ensuring **low-latency delivery** across heterogeneous hardware networks."

### 3. Skills Section (Reordering)
*   **Remove:** HTML/CSS (or move to very end).
*   **Highlight:** Python, Java, C++, Bash/Shell Scripting (add if you know it), GCP (Compute Engine, GKE, Stackdriver/Cloud Operations), Linux System Fundamentals.

---

## Signals for interviewers｜要讓面試官看到的訊號

當面試官（通常是 Tech Lead 或 Manager）看到修改後的履歷時，他們應該接收到以下訊號：

1.  **Automation Mindset (自動化思維)**：這個人不是在手動修 bug，而是在寫「工具」來自動發現並修復 bug。
    *   *Signal:* "Automated Actions," "CI/CD improvements," "Scripting."
2.  **System Visibility (系統可觀測性)**：這個人懂得如何監控系統健康狀態，這正是 "Diagnostics" 的核心。
    *   *Signal:* "Audit reports," "Monitoring," "Alerting platforms."
3.  **Hardware/Low-level Empathy (硬體同理心)**：即使近期做 Cloud，他過去有處理 Sensor/IoT 的經驗，能理解硬體限制與網路延遲。
    *   *Signal:* "Sensor data," "IoT platform," "Emergency Alert System."
4.  **Google-Ready (即戰力)**：他已經是 GCP Architect，不需要教他什麼是 Pub/Sub 或 GKE，他可以直接開始設計診斷工具。

---

## Common pitfalls｜常見錯誤與避免方式

1.  **陷阱：過度強調 UI/UX 細節**
    *   *錯誤*：在面試或履歷中詳細描述如何使用 React Hooks 優化前端渲染。
    *   *修正*：此職缺關注 "Diagnostics Tools"。除非該工具是前端 Dashboard，否則請將重點放在「數據如何被採集、傳輸與分析」的後端/系統流程。
2.  **陷阱：忽略 "System Programming" 的定義**
    *   *錯誤*：認為寫 CRUD API 就是 System Programming。
    *   *修正*：Google 的 System Programming 通常指與 OS 互動、資源管理、Concurrency 控制。請複習 Linux 基礎（Process, Thread, Memory Management, File System），並在履歷中暗示你對這些底層機制有概念（例如：提到 Performance Tuning）。
3.  **陷阱：Chunghwa Telecom 經驗寫得太像「PM」**
    *   *錯誤*：只寫 "Produced specs" 或 "Guided delivery"。
    *   *修正*：必須強調 **Technical Contribution**。即使是架構設計，也要具體說明解決了什麼技術難題（如：頻寬限制、即時性要求）。

---

## Checklist｜檢查清單

在投遞申請前，請確認完成以下項目：

- [ ] **關鍵字替換**：已刪除 80% 的前端關鍵字 (React, CSS, UI)，並替換為 Infrastructure 關鍵字 (Automation, Provisioning, Telemetry, Diagnostics)。
- [ ] **CHT 經歷升級**：已將 Chunghwa Telecom 的經歷擴充，強調 IoT、Sensor 與 System Design，以呼應 JD 的 "Hardware interaction"。
- [ ] **量化工具影響**：針對 Innova 的經歷，已將重點從「功能開發」轉為「流程自動化」與「效率提升」，並附上數據（如：減少 X% 時間）。
- [ ] **技能排序**：在 Skills 欄位中，將 GCP、Python、Java、System Design 排在最前，JavaScript/Web 相關技能移至最後。
- [ ] **GCP 證照應用**：在 Summary 或 Experience 中，用一句話連結 GCP Architect 證照與實際的系統設計能力（而不僅僅是列出證照名稱）。