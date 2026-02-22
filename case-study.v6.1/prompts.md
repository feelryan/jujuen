對不起，我疏忽了！這是架構師最關鍵的「資料梳理」步驟。為了讓你未來的流程更完整，我將提示詞重新組合為 **「三階段大師級提示詞系列」**。

這套 Prompts 會引導 AI 從**數位化（翻譯與結構化）**、**專業分析（設計解決方案）**、到**驗證學習（產出題目）**。

---

### 第一階段：數位化與雙語結構化 (Phase 1: Digitization & Bilingual Structuring)

**使用時機：** 當你剛上傳新的 PDF 檔案（案例研究或考試指南）時，請先發送此指令。

 **Prompt 內容：**
 Task: 請將我上傳的 PDF 檔案內容轉換為 Markdown 格式。
 **要求 (Requirements):**
 1. **保持結構**: 嚴格保持原文件的章節、段落與條列式清單。
 2. **雙語對照 (Inline Translation)**: 提供逐句 (sentence-by-sentence) 的繁體中文翻譯。翻譯必須直接緊跟在原英文句後方，**無須斷行**（格式如：English sentence. 繁體中文翻譯。）。
 3. **準確性**: 確保專有名詞（如：Compute Engine, High Availability）在翻譯時保持專業。
 
 
 [請開始轉換並翻譯]

---

### 第二階段：架構分析與解決方案設計 (Phase 2: Architecture Analysis & Solution Design)

**使用時機：** 在 AI 完成第一階段的翻譯後，發送此指令進行深度剖析。

 **Prompt 內容：**
 Role: 你是一位 Google 資深專業架構師 (Senior Google Professional Architect)。
 Task: 請根據剛才轉換的案例內容，進行深度架構分析並設計解決方案。
 **內容要求 (Requirements):**
 1. **深度剖析**: 分別針對「業務驅動因素」、「技術限制」以及「未來增長目標」進行分析。
 2. **產品應用**: 指導我如何應用 Google Cloud 產品（運算、數據、網路、維運與安全）來解決該案例的痛點。
 3. **語言要求**: 所有分析與建議必須以「英文與中文 inline (雙語並列)」提供。
 4. **最佳實務**: 必須引用 Google Cloud Well-Architected Framework 的原則。
 
 
 [請開始分析並提供架構建議]

---

這是一個非常關鍵的觀察。Google Professional Cloud Architect (PCA) 的考題確實不是考單純的產品定義，而是考**「複雜情境下的最佳決策」**。官方樣題（Sample Questions）的特點是：

1. **情境鋪陳長**：包含背景、目標、限制（如：不可停機、成本優先、現有技術棧）。
2. **選項高度相似**：選項通常會採用相同的動詞或架構，只在關鍵技術細節上做微調（例如：同樣是遷移，方案 A 是 Rehost，方案 B 是 Replatform），強迫考員區分細微差別。
3. **最優解邏輯**：四個選項可能技術上都可行，但只有一個最符合「Google 推薦的最佳實務」或「題目給出的特定限制」。

為了達到這種專業度，我調整了第三階段的 Prompt。這個新版本加入了**「干擾項設計指南」**與**「長格式情境要求」**。

---

### 調整後的第三階段：高保真考題產生器 (Phase 3: High-Fidelity MCQ JSON Generator)

**使用時機：** 當你想要產出極度接近真實考場難度的題目時使用。

 **Prompt 內容：**
 **Role:** 你是 Google Cloud 認證考試設計專家，專精於編寫 Professional Cloud Architect (PCA) 真實考題。
 **Task:** 根據上傳的案例研究與「Professional Cloud Architect Sample Questions.pdf」中的風格，產生 5 題模擬考題。
 **考題設計準則 (High-Fidelity Guidelines):**
 1. **情境長度 (Scenario Depth):** 每題題幹需包含複雜的情境描述（建議 >600 字元），必須結合案例中的業務目標（如：減維運負擔、維持合規）與技術現狀。
 2. **選項結構 (Option Complexity):** 每個選項必須是完整的行動建議（建議 >150 字元），而非簡短名詞。
 3. **擬真干擾項 (Professional Distractors):** >    - 選項之間必須具備高度相似性，使用相似的語法結構。
 * 必須設計「看似正確但略遜一籌」的選項（例如：技術可行但成本較高，或是不符合題目要求的「最小化維運」）。
 * 區分關鍵細節（如：Managed vs Unmanaged, Regional vs Multi-regional, Synchronous vs Asynchronous）。
 
 4. **選項隨機分佈** ：禁止將正確答案固定放在第一個選項 (A)。正確答案必須在 (A), (B), (C), (D), ... 之間隨機分佈。例如在每一批次的 5 題中，答案的分佈應盡可能平衡（例如：A, C, B, D, A），避免出現連續兩題答案相同或過度集中於某一字母的情況。

 5. **複選題比例** : 複選題比例應佔每批次產出的20%, 

 6. **禁止符號:** **嚴格禁止**產出任何引用標記如 `[cite]` 或 ``。

 7. **考題難度** : 偏難
 
 
 **JSON 格式規則：**
 1. **多語支援**: 題目 (`question`)、選項 (`options`)、解釋 (`why`) 的每一句話都必須包含繁體中文 (t) 與英文 (en)。
 2. **字詞分組 (wg)**: 針對每句內容，識別出具備特別意義的字詞（如專有名詞、動作動詞）提供繁體中文 (t)、英文 (en) 及性 (ps)。
 3. **結構**: 嚴格遵守下列 JSON 結構：
 
 
 ```json
 {
   "no": "1",
   "level": "hard",
   "keywords": "Hybrid, Connectivity, Dedicated Interconnect",
   "question": [
     { "t": "長篇情境描述第一句...", "en": "Long scenario sentence 1...", "wg": [...] },
     { "t": "長篇情境描述第二句...", "en": "Long scenario sentence 2...", "wg": [...] }
   ],
   "type": "單選題",
   "options": [
     { "t": "(A) 長篇行動方案描述...", "en": "(A) Detailed action plan...", "wg": [...] },
     { "t": "(B) 高度相似但有微小錯誤的方案...", "en": "(B) Similar but slightly incorrect plan...", "wg": ...] }
   ],
   "answer": "(X)",
   "why": { "t": "深度解釋為何此項最優，並指出其他項的細微缺陷。", "en": "Deep dive into why this is the best and pecific flaws in others.", "wg": [...] }
 }
 
 ```
 
 
 [請先產生第 1 到 5 題]


---

### 專業使用技巧 (Expert Tips)

1. **連鎖反應 (Chaining)**: 你可以一次性將這三個 Prompt 存成一個記事本。拿到新案例時，**不要一次貼三個**，而是等 AI 跑完第一個動作（翻譯）後，再貼下一個。這樣可以確保 AI 的 Context（對話上下文）是專注在當前的任務上，產出的品質最高。
2. **修正翻譯**: 如果第一階段的某些專業術語翻譯不符合你的習慣，你可以在第二階段開始前告訴他：「請在後續分析中，將 $Term 翻譯為 $Your_Term」。
3. **JSON 驗證**: 因為 JSON 格式很長，如果 AI 在產出過程中斷了，你可以直接輸入「繼續 (Continue)」或「從第 X 題開始繼續」。

這套工作流現在包含了從**閱讀文件**到**架構設計**再到**考試衝刺**的所有環節。祝你未來的案例分析無往不利！