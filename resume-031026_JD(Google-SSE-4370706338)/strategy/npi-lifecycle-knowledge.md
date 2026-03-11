# 領域知識：NPI (新產品導入) 與資料中心自動化 / Domain Knowledge: NPI & Data Center Automation

## Why this matters｜為什麼這個主題重要

這份 JD 來自 **Google Cloud MSCA (ML, Systems, & Cloud AI)** 團隊，其核心職責是確保支撐 Google 服務（如 Search, YouTube, Vertex AI）的**底層硬體與基礎設施**（如 TPU, Servers）能夠順利量產並維持健康狀態。

1.  **JD 的關鍵字是「硬體生命週期」而非單純的「軟體開發」**：
    JD 明確提到 "New Product Introduction (NPI)"、"Test Fleet"、"HPC manufacturing"。若你僅展現 Web App 或 SaaS 的開發經驗，面試官會擔心你無法理解「硬體測試」的特殊性（例如：硬體壞了不能像軟體一樣 rollback，測試週期長，資源昂貴）。
2.  **你的履歷需要「翻譯」**：
    你擁有極強的 CI/CD 與 Cloud-native 經驗。在這個職位上，你需要將這些經驗重新包裝：**CI/CD Pipeline $\rightarrow$ Manufacturing Test Pipeline**；**Cloud Monitoring $\rightarrow$ Fleet Diagnostics**。
3.  **NPI 是 Google 硬體工程的核心節奏**：
    理解 NPI 流程（EVT/DVT/PVT）能讓你在 System Design 與行為面試中，展現出你能夠與硬體工程師（Hardware Engineers）及供應鏈團隊協作，這是 Senior 工程師必備的 Cross-functional 溝通能力。

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: 建立領域詞彙與概念對照 (Concept Mapping)
目標：將你熟悉的軟體概念映射到硬體/資料中心領域。

*   **學習 NPI 階段**：
    *   理解硬體開發階段：**Proto** $\rightarrow$ **EVT** (Engineering Validation Test) $\rightarrow$ **DVT** (Design Validation Test) $\rightarrow$ **PVT** (Production Validation Test) $\rightarrow$ **Mass Production (MP)**。
    *   *Action*: 閱讀 Google SRE Book 中關於 "Managing Critical State" 或硬體維運的章節，或搜尋 "Hardware NPI process explained for software engineers"。
*   **建立對照表**：
    *   Unit Test $\rightarrow$ **Component Diagnostic** (測試 CPU, RAM, Network 卡本身是否正常)。
    *   Integration Test $\rightarrow$ **System Stress Test** (組裝後燒機測試)。
    *   Continuous Deployment $\rightarrow$ **Factory Image Provisioning** (在工廠端自動灌入 OS 與測試程式)。
    *   Production Monitoring $\rightarrow$ **Fleet Health Monitoring** (監控資料中心數萬台機器的健康度)。

### Week 2: 研究 Google 的基礎設施與工具 (Tooling Research)
目標：在面試中能提及相關技術名詞，證明你有做功課。

*   **關鍵技術關鍵字**：
    *   **OpenBMC / IPMI**：伺服器管理介面（如何遠端重啟一台死機的電腦）。
    *   **gRPC / Protobuf**：Google 內部微服務與硬體通訊的標準。
    *   **TPU (Tensor Processing Unit)**：閱讀 Google Cloud TPU 的架構白皮書，了解它是如何被部署的（Pod, Slice）。
*   **思考 "Test Fleet" 的挑戰**：
    *   當你有 10,000 台機器在跑測試，如何自動化排程？如何處理 "Flaky Tests"（硬體不穩還是測試程式寫爛）？如何自動隔離壞掉的機器（Auto-drain/Repair）？

### Week 3: 系統設計針對性練習 (Targeted System Design)
目標：準備一題「設計一個硬體自動化測試平台」。

*   **練習題目**：Design a distributed diagnostic system for data centers.
    *   **Scope**: 支援 NPI 階段（頻繁變更測試邏輯）與 Production 階段（大規模定期掃描）。
    *   **Components**: Scheduler (派發測試任務), Worker/Agent (在機器上執行測試), Result Store (存儲 Log), Analyzer (判斷是 Pass/Fail)。
    *   **Key Challenges**:
        *   **Scalability**: 如何同時管理數百萬台機器？
        *   **Reliability**: 如果測試程式本身 crash 了怎麼辦？
        *   **Security**: 測試程式通常需要高權限 (Root)，如何確保安全？

### Week 4: 故事重構 (Narrative Refinement)
目標：修改自我介紹與行為面試故事。

*   將你在 Innova Solutions 的 "Medical Imaging Platform" 經驗，強調為 **"High-reliability & Compliance-heavy system"**。這與硬體製造的高標準（不能出錯、詳細的 Audit Log）非常相似。
*   強調你在 **CI/CD** 的經驗是 **"Automating the verification lifecycle"**，這正是 NPI 需要的技能。

---

## Examples & templates｜範例與句型

### 1. 履歷/自我介紹的「轉譯」範例 (Reframing Experience)

*   **Original (Web focus):**
    > "Designed and developed features for Imaging Share including backend mechanisms... Drove CI/CD and code quality improvements."
*   **Reframed for this Role (Infra/NPI focus):**
    > "Architected **automated validation pipelines** for a mission-critical medical platform, ensuring strict compliance similar to **stage-gate NPI processes**. Designed **diagnostic mechanisms** to detect system anomalies early, reducing release failures by X%."
    *   *(解析：將 Web 功能開發轉化為「驗證流程」與「診斷機制」，直接命中 JD 的痛點。)*

### 2. 面試問答句型 (Interview Scripts)

**Q: How do you handle a situation where a test is failing intermittently? (Flaky tests)**

*   **Answer Template:**
    > "In my experience with distributed systems, flakiness is the enemy of velocity.
    > 1.  **Isolation**: First, I'd quarantine the affected environment (or **Device Under Test**) to prevent noise in the fleet.
    > 2.  **Bisection**: Use automated bisection (like `git bisect` but for hardware configs or firmware versions) to identify the root cause—whether it's a software race condition or a **hardware signal integrity issue**.
    > 3.  **Telemetry**: I'd look at the **system-level metrics** (thermal, voltage, memory errors) during the failure window to correlate hardware states with software failures."

**Q: You don't have direct hardware NPI experience. How will you adapt?**

*   **Answer Template:**
    > "That's true, but I see a strong parallel between **Software Development Lifecycle (SDLC)** and **Hardware NPI**.
    > In my previous role, I managed the release lifecycle for regulated medical software. We had phases equivalent to EVT/DVT where we validated specific specs before moving to a broader rollout.
    > I bring the **software engineering rigor**—automated testing, version control for configs, and scalable data analysis—that can modernize traditional hardware testing workflows."

### 3. 提問環節 (Questions to Ask)

*   "How does the team balance the speed of **NPI iterations** (where requirements change daily) with the stability required for the **production test fleet**?"
*   "Are we moving towards **'Infrastructure as Code'** for defining the test environments in the factories?"

---

## Signals for interviewers｜要讓面試官看到的訊號

若你照著上述策略準備，面試官會在筆記中寫下：

1.  **"System Thinker"**: Ryan 不只會寫 Code，他理解系統的全貌（從硬體層到應用層）。
2.  **"Automation Mindset"**: 他極度討厭手動操作，會想辦法把工廠測試流程自動化、腳本化。
3.  **"Reliability Focused"**: 他的醫療軟體背景讓他具備「零容錯」的思維，這非常適合 Google 的 Data Center 等級要求。
4.  **"Quick Learner"**: 雖然沒有硬體背景，但他已經掌握了 NPI 的術語，並能用軟體工程的方法論來解決硬體問題。

---

## Common pitfalls｜常見錯誤與避免方式

1.  **錯誤：過度強調 UI/Frontend 技能**
    *   *Avoid*: 花時間講 React Component 的優化。
    *   *Fix*: 即使講 Innova 的專案，也要聚焦在 **Backend API, Data Pipeline, GCP Infrastructure, CI/CD Automation**。JD 裡雖然提到 UI，但那是給內部工具用的，不是重點。
2.  **錯誤：把 NPI 當成單純的軟體發布**
    *   *Avoid*: 認為 rollback 就像 `git revert` 一樣簡單。
    *   *Fix*: 承認硬體修復的成本很高（Lead time 長），所以強調 **"Shift-left testing"**（在設計階段就盡早測試）的重要性。
3.  **錯誤：忽略「規模化」(Scale)**
    *   *Avoid*: 設計一個只能跑在單機上的 Python script。
    *   *Fix*: 隨時思考：「如果這個 Script 要同時跑在 50,000 台機器上，會發生什麼事？網路會不會爆？Log 會不會塞滿硬碟？」

---

## Checklist｜檢查清單

- [ ] 我能清楚解釋 **EVT, DVT, PVT** 的區別，並能用軟體開發階段（Alpha, Beta, RC）做類比。
- [ ] 我準備好了一個關於 **"Automated Diagnosis"** (自動化診斷) 的系統設計草案。
- [ ] 我閱讀了至少一篇關於 **Google Data Center / TPU Architecture** 的技術文章。
- [ ] 我將履歷中的 CI/CD 經驗，口語練習轉化為 **"Validation Pipeline"** 的敘述方式。
- [ ] 我準備好回答：「當軟體測試 Pass 但硬體實際運作 Fail 時，你會怎麼 Debug？」