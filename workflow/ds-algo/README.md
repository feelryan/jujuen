# DS-ALGO 題庫與教材產生腳本

這個目錄用來為「資料結構與演算法（DS & Algo）」主題，自動產生教學教材與題庫 JSON，並搭配前端知識地圖（menu-path.json）一起使用。

## 檔案與結構總覽

- `menu-path.json`：列出所有 DS-ALGO 主題（topics），每個 `items[].id` 會對應一個主題目錄。
- `topics.json`：要產生教材與題庫的 topic 清單（字串陣列，對應 menu-path.json 裡的 id）。
- `difficulties.json`：要支援的難度清單，例如 `["beginner", "intermediate", "advanced"]`。
- `codeLangs.json`：要產生教材的程式語言清單，例如 `["Python", "TypeScript"]`。
- `prompt-concepts.md`：產生「觀念教材」的提示詞模板。
- `prompt-questions.md`：產生「題庫問題 JSON」的提示詞模板（已內建 options/answer 標準格式規則）。
- `output/`：腳本執行後輸出的結果，結構為：
  - `output/{topic_id}/`
    - `{topic_id}_{difficulty}_{codeLang}.md`：該 topic / 難度 / 語言的教材 Markdown。
    - `questions.json`：該 topic 的完整題庫 JSON。
    - `questions-meta.json`：該 topic 題庫的摘要與進度資訊（目標題數、每題簡要標題等）。
    - `questions({codeLang}).json`：每種程式語言對應的題庫檔名（內容目前與 `questions.json` 相同，方便前端依語言掛載）。
- `generate_materials.py`：只負責依 `topics.json` × `difficulties.json` × `codeLangs.json` 產生教材 Markdown。
- `generate_questions_from_materials.py`：依 `topics.json`（與 `questions-meta.json` 狀態）產生 / 補齊題庫 JSON，並同步輸出 `questions({codeLang}).json`。
- `generate_config_files.py`：根據 menu-path.json 與三個清單檔產生前端使用的 config JSON（指到 GitHub 上的教材與題庫路徑）。

---

## 前置準備

在執行任何會呼叫 Vertex AI 的腳本前，請先完成：

1. 安裝並設定 gcloud Application Default Credentials：
   - 在終端機執行：
     - `gcloud auth application-default login`
2. 安裝最新版 `google-genai` 套件（若尚未安裝）：
   - `pip install google-genai`
3. 設定 `generate_materials.py` 裡的專案資訊：
   - 在檔案開頭確認：
     - `PROJECT_ID = "<你的 GCP Project ID>"`
     - `LOCATION = "global"`（可依需求調整）
4. 準備輸入檔：
  - [menu-path.json](menu-path.json)：整體主題清單與前端用的導航結構。
  - [topics.json](topics.json)：要實際生成教材與題庫的 topic id 陣列（通常是 menu-path.json 中的子集或相同集合）。
  - [difficulties.json](difficulties.json)：要支援的所有難度（以字串陣列表示）。
  - [codeLangs.json](codeLangs.json)：要支援的所有程式語言（以字串陣列表示）。
   - [prompt-concepts.md](prompt-concepts.md)、[prompt-questions.md](prompt-questions.md)：若有修改題型規則，請先在這裡更新提示詞。

---

## generate_materials.py：只產生教材 Markdown

腳本位置： [generate_materials.py](generate_materials.py)

### 功能說明

對 `topics.json` 中列出的每個 topic，搭配 `difficulties.json` 與 `codeLangs.json` 的所有組合產生 **教材 Markdown**（觀念 + 範例 + 練習）：

- 路徑：`output/{topic_id}/{topic_id}_{difficulty}_{codeLang}.md`
- 內容格式由 [prompt-concepts.md](prompt-concepts.md) 定義。

此腳本**不再產生題庫 JSON**，題庫改由獨立腳本 `generate_questions_from_materials.py` 負責。

### 執行方式

在本目錄（workflow/ds-algo）中執行：

```bash
python generate_materials.py
```

腳本流程概要：

1. 初始化 Vertex AI Client（使用 `PROJECT_ID` / `LOCATION`）。
2. 讀取 `topics.json`、`difficulties.json`、`codeLangs.json`。
3. 對每個 `(topic_id, difficulty, codeLang)`：
   - 建立 `output/{topic_id}` 目錄。
   - 若對應的 Markdown 不存在，依 `prompt-concepts.md` 產生；若已存在則略過。
4. 最後做一次 Completeness Check，列出哪些教材 `.md` 尚未產生。

---

## generate_questions_from_materials.py：為每個 topic 產生題庫 JSON

腳本位置： [generate_questions_from_materials.py](generate_questions_from_materials.py)

### 功能說明

- 讀取 [topics.json](topics.json)（以及 [codeLangs.json](codeLangs.json) 以輸出每種語言對應的題庫檔名）。
- 根據 [prompt-questions.md](prompt-questions.md) 以及目前主題的 `questions-meta.json` 狀態，呼叫 Vertex AI 產生題目：
  - 每個主題有一個目標總題數 `totalQuestionsNum`（預設 20，可用 CLI 覆寫）。
  - 每次執行只會為「尚未達標」的主題補齊缺少的題目數量，並避免與既有題目重複。
- 輸出檔案：
  - 最終題庫：`output/{topic_id}/questions.json`
  - 對應 meta：`output/{topic_id}/questions-meta.json`（摘要每一題的 id / 標題與總題數設定）。
  - 並將相同內容複製為每種語言專用檔案：`output/{topic_id}/questions({codeLang}).json`（配合 `generate_config_files.py`）。

### 執行方式

在本目錄（workflow/ds-algo）中執行：

```bash
# 為所有主題產生（或補齊）題庫，每個主題目標 20 題
python generate_questions_from_materials.py

# 只處理單一主題，並指定目標總題數 30 題
python generate_questions_from_materials.py --topic-id "Arrays & Hashing" --total-questions 30
```

你可以多次重複執行這支腳本：

- 若某主題已經達到或超過目標題數，該主題會被略過。
- 若尚未達標，則會依據 `questions.json` / `questions-meta.json` 的現況，告訴模型「已經有哪些題目」，只補齊不足的部分。

---

## generate_config_files.py：為每個 topic 產生 config JSON

腳本位置： [generate_config_files.py](generate_config_files.py)

### 功能說明

- 讀取 [topics.json](topics.json)、[difficulties.json](difficulties.json)、[codeLangs.json](codeLangs.json)：
  - `topics.json`：每個元素是一個 topic_id，對應一個輸出的 config 檔。
  - `difficulties.json`：用來產生 basic / intermediate / advanced 等知識層級節點（會依順序串成 parent chain）。
  - `codeLangs.json`：用來產生每種程式語言版本的教材與題庫節點。
- 對每個 topic 產生一個 config JSON（存在目前目錄）。
- config 會描述：
  - 對於每個 `codeLang`，依 `difficulties` 產生一條「知識層級」節點鏈，指向不同難度與語言的教材 Markdown（GitHub 連結）。
  - 對於每個 `codeLang`，產生一個 `Questions ({codeLang})` 節點，指向對應語言的題庫 JSON（例如 `questions(Python).json`、`questions(TypeScript).json`）。
  - 一個共用的 `coding-problems` 節點，指向 coding problems 類別 JSON（仍維持一個即可）。

輸出檔：

- `{topic_id}.json`（以 topic id 為檔名，做適度的字元清洗）。

### 執行方式

在本目錄（workflow/ds-algo）中執行：

```bash
python generate_config_files.py
```

產生後可以把這些 `{topic_id}.json` 上傳到前端配置使用，讓前端從 GitHub 載入教材 Markdown 與題庫 JSON。

---

## 題庫後處理建議

若之後你想統一 DS-ALGO 題庫的 `options` / `answer` 格式（例如和 skills/handbook 題庫規則保持一致），可以複用 skills 目錄下的工具流程：

1. 先在 `prompt-questions.md` 明確規定題目輸出的 options / answer 規則（目前已完成）。
2. 如有歷史題庫可以寫一個類似 `verify_question_answers.py` 的腳本，在 DS-ALGO `output/` 底下掃描所有 `questions*.json`，批次修正格式並加上 `verified` 標記。

目前本目錄尚未提供通用 verify 腳本，如有需要可以再另外新增。
