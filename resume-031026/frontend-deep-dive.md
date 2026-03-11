# 前端技術深究 / Front-end Deep Dive | Front-end Deep Dive

## 1. 目標與範圍 | Goal & Scope
- **展示 React 與 TypeScript 實戰能力**：證明你不僅會寫程式碼，還能架構可維護的大型前端應用。
  - **Demonstrate React & TypeScript proficiency**: Prove you don't just write code, but architect maintainable, large-scale front-end applications.
- **強調醫療領域的 UI 複雜度**：利用 Innova Solutions 的經驗，說明如何處理複雜的狀態管理（如影像分享、上傳流程）。
  - **Highlight UI complexity in Healthcare**: Use your Innova Solutions experience to explain handling complex state management (e.g., image sharing, upload workflows).
- **突顯國際化（i18n）經驗**：具體說明為英國/愛爾蘭與加拿大市場進行 UI 在地化的技術細節。
  - **Showcase Internationalization (i18n) experience**: Detail the technical aspects of UI localization for UK/Ireland and Canadian markets.

## 2. 簡短開場稿 | Opening Script

**適用於技術面試開場 (1-2 分鐘) | For Technical Interview Opening (1-2 mins)**

「雖然我有超過 15 年的全端與雲端開發經驗，但在最近於 Innova Solutions 的職位中，我深度參與了前端工程。我主要使用 **React** 和 **TypeScript** 來維護與開發雲原生醫療影像平台。
"While I have over 15 years of full-stack and cloud experience, in my recent role at Innova Solutions, I was deeply involved in front-end engineering. I primarily used **React** and **TypeScript** to maintain and develop a cloud-native medical imaging platform.

具體來說，我負責了兩個關鍵領域：
Specifically, I was responsible for two key areas:

第一，**複雜互動元件的開發**，例如『檢查報告上傳器（Exam Uploader）』與『影像分享功能（Request Share）』，這需要嚴謹的狀態管理與 API 整合。
First, **developing complex interactive components**, such as the 'Exam Uploader' and 'Request Share' features, which required rigorous state management and API integration.

第二，**UI 在地化（Localization）**。我主導了將美版介面調整為符合英國、愛爾蘭與加拿大市場需求的專案，這不僅是翻譯文字，更涉及日期格式、醫療合規顯示與動態內容的處理。
Second, **UI Localization**. I led the initiative to adapt the US-centric UI for UK, Ireland, and Canadian markets, which involved not just text translation but handling date formats, medical compliance displays, and dynamic content.

我習慣利用我的後端背景（Java/Spring Boot）來優化前端與 API 的資料合約，確保前端效能與資料一致性。」
I leverage my backend background (Java/Spring Boot) to optimize the data contract between the front-end and APIs, ensuring front-end performance and data consistency."

## 3. 關鍵故事與成就 | Key Stories & Achievements

### 故事一：醫療平台的 UI 在地化 (Innova Solutions)
**Story 1: UI Localization for Medical Platform (Innova Solutions)**

- **情境 (Situation)**：
  - 既有的醫療影像平台是針對美國市場設計，需擴展至英國、愛爾蘭與加拿大，需符合當地法規與使用者習慣。
  - The existing medical imaging platform was designed for the US market and needed to expand to the UK, Ireland, and Canada, complying with local regulations and user habits.
- **任務 (Task)**：
  - 重構前端程式碼以支援多語系與區域設定（Locale），且不能影響現有美國用戶的功能。
  - Refactor front-end code to support multiple languages and locales without breaking functionality for existing US users.
- **行動 (Action)**：
  - 抽離寫死（Hard-coded）的文字串，建立資源檔管理機制。
  - Extracted hard-coded strings and established a resource file management mechanism.
  - 針對日期格式（MM/DD/YYYY vs DD/MM/YYYY）與醫療術語進行動態渲染處理。
  - Implemented dynamic rendering for date formats (MM/DD/YYYY vs DD/MM/YYYY) and medical terminology.
  - 與產品經理合作，確保 UI 佈局在不同文字長度下仍保持響應式（Responsive）。
  - Collaborated with PMs to ensure the UI layout remained responsive with varying text lengths.
- **結果 (Result)**：
  - 成功上線並支援多國市場，擴大了產品的全球市佔率，並建立了可重複使用的 i18n 模式。
  - Successfully launched support for multiple international markets, expanding the product's global footprint and establishing a reusable i18n pattern.

### 故事二：複雜表單與狀態管理 - 影像分享功能
**Story 2: Complex Forms & State Management - Image Sharing Feature**

- **情境 (Situation)**：
  - 醫生與醫療機構需要透過「Request Share」功能來請求或分享病患的影像資料，涉及多步驟驗證與權限控管。
  - Doctors and facilities needed a "Request Share" feature to request or share patient imaging data, involving multi-step validation and permission controls.
- **行動 (Action)**：
  - 使用 **React** 開發互動式模態視窗（Modals）與表單。
  - Developed interactive modals and forms using **React**.
  - 利用 **TypeScript** 定義嚴格的介面（Interfaces）來對接後端 API，減少資料型別錯誤。
  - Used **TypeScript** to define strict interfaces for backend API integration, reducing data type errors.
  - 實作前端驗證邏輯，即時回饋使用者輸入錯誤，減少無效的 API 請求。
  - Implemented front-end validation logic to provide real-time feedback on user input, reducing invalid API requests.
- **結果 (Result)**：
  - 提升了醫療人員的操作效率，並透過更清晰的錯誤處理減少了客服工單（Support Tickets）。
  - Improved operational efficiency for medical staff and reduced support tickets through clearer error handling.

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

### Q1: 你如何處理 React 應用程式的效能優化？
**Q1: How do you handle performance optimization in React applications?**

- **回答角度 (Answer Angle)**：
  - 針對醫療列表資料（如病患清單、Audit Reports），提及 **Virtualization (Windowing)** 技術。
  - Mention **Virtualization (Windowing)** for large medical data lists (e.g., patient lists, audit reports).
  - 提及使用 `useMemo` 和 `useCallback` 避免不必要的重新渲染（Re-renders）。
  - Mention using `useMemo` and `useCallback` to avoid unnecessary re-renders.
  - **範例 (Example)**：「在處理大量 Audit Reports 時，我確保只有資料變動的 Row 才會重新渲染，並對 API 回傳的大型 JSON 進行分頁處理。」
  - "When handling large Audit Reports, I ensured only rows with data changes re-rendered and implemented pagination for large JSON responses from the API."

### Q2: 你為什麼在專案中選擇 TypeScript？它解決了什麼問題？
**Q2: Why did you choose TypeScript for your projects? What problems did it solve?**

- **回答角度 (Answer Angle)**：
  - 強調 **可維護性 (Maintainability)** 與 **開發者體驗 (DX)**。
  - Emphasize **Maintainability** and **Developer Experience (DX)**.
  - **範例 (Example)**：「在醫療領域，資料結構（如 FDA 510K 報告）非常複雜。TypeScript 的介面定義幫助我們在編譯階段就抓出屬性拼寫錯誤或型別不符的問題，而不是等到 Runtime 才報錯，這對於團隊協作至關重要。」
  - "In the healthcare domain, data structures (like FDA 510K reports) are complex. TypeScript interfaces helped us catch property typos or type mismatches at compile time rather than runtime, which was crucial for team collaboration."

### Q3: 你如何管理全域狀態（Global State）與區域狀態（Local State）？
**Q3: How do you manage Global State vs. Local State?**

- **回答角度 (Answer Angle)**：
  - 區分 UI 狀態（如 Modal 開關）與伺服器快取狀態（Server State）。
  - Distinguish between UI state (e.g., modal toggles) and Server State.
  - **範例 (Example)**：「對於表單輸入，我傾向使用 Local State (useState)；對於跨元件的用戶設定或權限，我會使用 Context API 或狀態管理庫。重點是避免 Props Drilling。」
  - "For form inputs, I prefer Local State (useState); for cross-component user settings or permissions, I use Context API or state management libraries. The key is to avoid Prop Drilling."

## 5. 技術深挖提示 | Technical Deep‑Dive Prompts

若面試官深入技術細節，請準備以下主題的「骨架」：
If the interviewer digs deep into technical details, prepare skeletons for these topics:

1.  **React Hooks 原理**：
    - 解釋 `useEffect` 的依賴陣列（Dependency Array）陷阱。
    - Explain the pitfalls of the `useEffect` dependency array.
    - 說明何時該自定義 Hook（Custom Hooks）來封裝邏輯（例如：封裝 API 呼叫邏輯）。
    - Explain when to create Custom Hooks to encapsulate logic (e.g., wrapping API call logic).
2.  **前端安全性 (Security)**：
    - 醫療專案特別重視資安。提及如何防範 XSS（React 預設會跳脫字元）與 CSRF（Token 處理）。
    - Healthcare projects prioritize security. Mention preventing XSS (React escapes by default) and CSRF (Token handling).
3.  **元件設計模式 (Component Design Patterns)**：
    - **Container vs. Presentational Components**：邏輯與顯示分離。
    - **Container vs. Presentational Components**: Separation of logic and view.
    - **Composition (組合)**：利用 `children` prop 來增加元件重用性。
    - **Composition**: Using the `children` prop to increase component reusability.

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

- **陷阱 (Pitfall)**：過度強調 CSS/樣式細節，忽略架構。
  - **Over-emphasizing CSS/styling details while ignoring architecture.**
- **糾正 (Correction)**：作為資深工程師，應著重於**資料流（Data Flow）**、**元件拆分策略**以及**如何降低技術債**。
  - As a Senior Engineer, focus on **Data Flow**, **Component Decomposition Strategy**, and **Technical Debt Reduction**.

- **陷阱 (Pitfall)**：忘記提及後端背景對前端的幫助。
  - **Forgetting to mention how your backend background aids frontend work.**
- **糾正 (Correction)**：主動提及因為懂 DB Schema 和 API 設計，所以能寫出更高效的前端資料接取邏輯（Data Fetching Logic）。
  - Proactively mention that understanding DB Schema and API design allows you to write more efficient frontend Data Fetching Logic.

## 7. 收尾與反問 | Closing & Questions for Interviewer

**總結句 (Closing Recap)**：
「總結來說，我將嚴謹的後端架構思維帶入了前端開發，利用 React 與 TypeScript 構建了高可靠性、符合國際標準的醫療應用介面。」
"In summary, I bring a rigorous backend architectural mindset to frontend development, utilizing React and TypeScript to build highly reliable, internationally compliant medical application interfaces."

**建議提問 (Questions to Ask)**：
1. 「目前的團隊在前端主要面臨的最大技術債或效能瓶頸是什麼？」
   - "What is the biggest technical debt or performance bottleneck the frontend team is currently facing?"
2. 「團隊如何決定何時引入新的前端函式庫或重構現有元件？」
   - "How does the team decide when to introduce new frontend libraries or refactor existing components?"
3. 「前端與後端團隊在 API 定義階段的協作模式是怎樣的？」
   - "What is the collaboration model between frontend and backend teams during the API definition phase?"