# 填補缺口：軟硬體整合與 Linux 系統經驗 / Bridging the Gap: Hardware Interaction & Linux

## Why this matters｜為什麼這個主題重要

這份 JD 來自 **Google Cloud MSCA (ML, Systems, & Cloud AI)** 團隊，他們負責的是 Google 資料中心（Data Centers）、TPU 與硬體基礎設施的「診斷（Diagnostics）」與「新產品導入（NPI）」。

對於你的背景（Ryan Hsiao）而言，這是一個關鍵的轉折點：
1.  **The "Application" vs. "Infrastructure" Gap**: 你的近期履歷（Innova, Hiveel）高度集中在 **Cloud-Native Application (Web/SaaS)** 層級（React, Node.js, Spring Boot）。
2.  **The Hidden Asset**: JD 偏好 "Software interacting with hardware" 與 "Linux OS"。你擁有 **15+ 年經驗**，且早期在 **Chunghwa Telecom (中華電信)** 的專案涉及 "Sensor, Alert, Video"，這其實就是物聯網（IoT）與硬體整合的前身。此外，你的學歷背景（土木/力學工程）在資料中心硬體領域其實是隱藏加分項（理解物理系統）。
3.  **Critical Success Factor**: 如果面試官認為你只是個「寫網頁後端的」，你會被刷掉。你必須證明你懂得 **「程式碼如何與底層系統（OS/Hardware）互動」**。

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: Resume Archaeology (挖掘過往硬體/系統經驗)
你必須把 2011-2017 中華電信的經歷「現代化」並「放大」，因為那是你與 Hardware 最直接的連結。

*   **Action**: 回想 e-SAV (Sensor, Alert, Video) 專案。
    *   當時如何從 Sensor 收集數據？（Serial Port? TCP/IP? Custom Protocol?）
    *   遇到過什麼硬體連線不穩、數據掉包的問題？如何解決？
    *   **目標**：找出 1-2 個「因為硬體限制導致軟體必須特殊設計」的故事。

### Week 2: Re-framing Cloud as "Linux Systems" (將雲端經驗轉譯為系統經驗)
你現在是 Google Cloud Architect，不要只談「使用 GCP 服務」，要談「在 Linux 環境下維運」。

*   **Action**: 針對你目前的 GCP 經驗，準備以下除錯（Debugging）案例：
    *   **Resource Constraints**: 曾經遇過 Container OOM (Out of Memory) 嗎？你如何用 Linux 工具（如 `top`, `htop`, `free`, `vmstat`）去分析？
    *   **I/O Issues**: 曾經遇過 Disk 讀寫太慢嗎？
    *   **Networking**: 曾經遇過連線 timeout 嗎？如何用 `tcpdump` 或 `netstat` / `ss` 排查？
    *   **目標**：證明你不只會寫 Java/JS，還懂程式跑在 Linux Kernel 上時發生了什麼事。

### Week 3: Study the "Diagnostics" Domain (補強領域知識)
JD 提到 "Diagnostic tools" 和 "NPI (New Product Introduction)"。

*   **Action**: 理解 NPI 流程。
    *   Google 伺服器上線前，需要跑一連串測試（CPU stress test, Memory check, Disk I/O check）。
    *   你的角色是寫工具來「自動化」這些測試。
    *   **思考練習**：如果讓你用 Python 寫一個 script，去檢查 1000 台機器的硬碟健康度（SMART data），你會怎麼設計？（這很可能是面試考題）。

---

## Examples & templates｜範例與句型

### 1. Resume Bullet Points Refinement (履歷修改範本)
將 Web 語言轉換為 Infra 語言。

*   **Before (Too High Level):**
    *   "Led architecture/design for e-SAV (Sensor, Alert, Video) cloud platform..."
*   **After (Hardware/System Focused):**
    *   "Architected **IoT data ingestion pipeline** for e-SAV platform, processing real-time signals from **hardware sensors and video feeds**, ensuring reliability under unstable network conditions."
    *   （強調處理硬體訊號與不穩定環境）

*   **Before (General Cloud):**
    *   "Maintained a cloud-native medical imaging platform in GCP environment."
*   **After (Linux/Ops Focused):**
    *   "Managed **Linux-based containerized workloads** on GCP; optimized system performance by analyzing **OS-level metrics (CPU, Memory, I/O)** and automating diagnostic workflows for high-availability services."
    *   （強調 Linux 與 OS 指標分析）

### 2. Interview Q&A Templates (面試回答句型)

**Scenario: "Tell me about a time you debugged a difficult system issue."**

*   **Opening (Context):** "While working on the medical imaging platform, we faced intermittent latency issues that application logs couldn't explain. I had to dig into the **system level**."
*   **Action (Linux/System):** "I SSH'd into the Linux instances and used tools like `strace` to monitor system calls and `iostat` to check disk saturation. I discovered that a specific background process was exhausting file descriptors..."
*   **Result (Impact):** "I optimized the process to handle resources efficiently, which aligns with how I would approach **hardware diagnostics**—looking for bottlenecks at the OS layer."

**Scenario: "How do you handle software interacting with hardware?"**

*   **Template:** "Although my recent focus is Cloud, my background in **Civil/Structural Engineering** and my work at Chunghwa Telecom gave me a strong foundation in physical systems. I understand that hardware isn't infinite—it has thermal limits, I/O latency, and physical failures. I write software defensively, assuming the underlying hardware *will* eventually fail or behave unexpectedly."
    *   （善用你的非 CS 學位，這在硬體/資料中心領域是優勢！）

---

## Signals for interviewers｜要讓面試官看到的訊號

當你執行上述策略時，面試官（通常是 Systems Engineer 或 SRE 背景）會尋找以下訊號：

1.  **Curiosity beyond the API**: 你不只滿足於呼叫 API，你會想知道 API 背後發生了什麼（System Calls, Kernel interactions）。
2.  **Respect for Constraints**: 你理解 CPU、Memory、Network Bandwidth 是有限資源，且知道如何測量它們。
3.  **Automation Mindset**: 針對 JD 的 "Tools" 與 "Automation"，你展現出「不想手動修一台機器，而是寫程式修一萬台機器」的思維。
4.  **Versatility (Full-stack to Bottom-stack)**: 你能寫 React 前端（給 User 看報表），也能寫 Python/Bash 腳本（去抓底層 Log）。這對 "Diagnostics Tools" 團隊來說是完美的技能組合。

---

## Common pitfalls｜常見錯誤與避免方式

1.  **Don't fake C/C++ Kernel knowledge**:
    *   **錯誤**: 假裝自己是 Kernel Hacker。
    *   **修正**: 誠實展現你是「熟練的應用層工程師，具備良好的系統觀念」。強調你擅長用 Python/Go/Java 寫工具來與系統互動，而不是去寫 Device Driver（除非你真的會）。
2.  **Ignoring the "Scale" factor**:
    *   **錯誤**: 只談單機除錯。
    *   **修正**: Google 的 NPI 是針對「數萬台」伺服器。隨時要在答案中加入：「如果要平行處理 5000 台機器，我會怎麼設計...（例如使用 Queue, Batch processing）」。
3.  **Over-focusing on UI**:
    *   **錯誤**: 花太多時間講 React/UI 設計。
    *   **修正**: JD 雖然提到 UI，但那是為了 "Diagnostics Tools" 的 Dashboard。重點在於**後端的數據準確性與自動化**。UI 只是呈現結果。

---

## Checklist｜檢查清單

- [ ] **履歷重構**：已將 Chunghwa Telecom 的 Sensor/Video 經驗關鍵字（Hardware, IoT, Signal）加強。
- [ ] **履歷重構**：已將 GCP 經驗中加入 "Linux", "System Debugging", "Performance Tuning" 等字眼。
- [ ] **知識補強**：已複習 Linux 基礎指令與概念（Process, Thread, File Descriptor, Socket, Memory Management）。
- [ ] **故事準備**：準備好一個「深入底層（Low-level）除錯」的故事。
- [ ] **心態調整**：準備好在面試中強調你的土木/力學背景如何幫助你理解「物理世界的工程問題」（Data Center 就是物理世界）。