## prompt 1

[Category-GoogleProductServiceConcept.txt]是一份為參加Professional Cloud Architect (PCA) Certification Exam準備的Google產品知識熟悉度要求清單.

代表知識熟悉度的數字定義如下:
```
1: basics	high-level functionality and use-cases	
2: medium	basics + prerequisites, limitations, common IAM roles, ability to integrate with other services, most common architectures	
3: advanced	medium + being able to deploy, troubleshoot and manage	
4: expert	advanced + know every detail about the service in complex configurations - huge scale, HA, DR etc	
```
[Category-GoogleProductServiceConcept.txt]的列表, 第一欄是Category, 第二欄是Google Product/Service/Concept, 第三欄是Recommended minimum knowldege level for PCA.

請將這XLSX檔案內容, 依據其Category, Concept / Product, 以及Recommended minimum knowldege level, 再參照[v6.1_pca_professional_cloud_architect_exam_guide_english.pdf]的說明來比對參考, 然後產出各項 Google Concept / Product的產品重要說明, 主要功能, 詳盡的應用情境, 以及詳盡的關鍵知識. (產出的內容必須與PCA Certification 考題有高度關聯, 例如Cloud Spanner就必須提到global high availability (99.999% SLA), 因為考題可能以此當作關鍵字來產生) 

產出的格式為Markdown

 **要求 (Requirements):**
 1. **保持結構**: 保持原文件的Category與Concept / Product的清單順序。
 2. **雙語對照 (Inline Translation)**: 提供逐句 (sentence-by-sentence) 的繁體中文翻譯。翻譯必須直接緊跟在原英文句後方，**無須斷行**（格式如：English sentence. 繁體中文翻譯。）。
 3. **準確性**: 確保專有名詞（如：Compute Engine, High Availability）在翻譯時保持專業。

 如果沒有辦法一次產生完成, 可依照Category分檔案產生.

 ## prompt 考題

 **Prompt 內容：**
 **Role:** 你是 Google Cloud 認證考試設計專家，專精於編寫 Professional Cloud Architect (PCA) 真實考題。
 **Task:** 根據[GCP Services Summary.txt] Knowledge Level的重要性與「v6.1_pca_professional_cloud_architect_exam_guide_english.pdf」的考試範圍說明，產生模擬考題涵蓋其考試範圍與可能重要內容。
 
 **考題設計準則 (High-Fidelity Guidelines):**
 1. **情境長度 (Scenario Depth):** 每題題幹需包含複雜的情境描述（建議 >400 字元），必須結合案例中的業務目標（如：減維運負擔、維持合規）與技術現狀。
 2. **選項結構 (Option Complexity):** 每個選項必須是完整的行動建議（建議 >100 字元），而非簡短名詞。
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
     { "t": "情境描述第一句...", "en": "scenario sentence 1...", "wg": [...] },
     { "t": "情境描述第二句...", "en": "scenario sentence 2...", "wg": [...] }
   ],
   "type": "單選題",
   "options": [
     { "t": "(A) 行動方案描述...", "en": "(A) Detailed action plan...", "wg": [...] },
     { "t": "(B) 高度相似但有微小錯誤的方案...", "en": "(B) Similar but slightly incorrect plan...", "wg": ...] }
   ],
   "answer": "(X)",
   "why": { "t": "深度解釋為何此項最優，並指出其他項的細微缺陷。", "en": "Deep dive into why this is the best and pecific flaws in others.", "wg": [...] }
 }
 
 ```
 
 
 [先產生第 1 到 10 題]
