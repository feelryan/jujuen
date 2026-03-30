## add a new skill

1. Add it on menu-path.json
2. py.exe .\generate_skill_info.py
3. py.exe .\generate_content_json_from_info.py
4. py.exe .\generate_skill_materials.py
5. py.exe .\generate_skill_questions_from_materials.py

- for handbook menu

1. py.exe .\add_handbook_to_skill_content.py
2. py.exe .\generate_handbook_sections.py
3. py.exe .\generate_handbook_section_material.py
4. py.exe .\generate_questions_from_handbook_section_material.py

## skills 工具說明

這個目錄主要用來為各個開發技能（TypeScript、GCP、MongoDB、Cloud‑Native Architecture 等）建立「學習路線圖」的設定檔，透過 Vertex AI 自動產生 content.info。

### 前置準備

1. 安裝並設定 gcloud（需能使用 Application Default Credentials）：
	- 執行：`gcloud auth application-default login`
2. 在本目錄建立 / 編輯 [PROJECT_ID.txt](PROJECT_ID.txt)：
	- 檔案內容只需一行：你的 GCP Project ID，例如：`my-gcp-project-id`
3. 確認 [menu-path.json](menu-path.json) 已存在，且每個 skill 子項目（例如 `typescript`, `gcp`）的 `parent` 不是 `null`。
4. 確認 [prompt-chpaters.md](prompt-chpaters.md) 為最新版（描述如何依 {skill} 產生章節 JSON 陣列）。

### generate_skill_info.py：產生各 skill 的 content.info

腳本位置： [generate_skill_info.py](generate_skill_info.py)

功能：
- 讀取：
  - [PROJECT_ID.txt](PROJECT_ID.txt)：取得 `PROJECT_ID`
  - [menu-path.json](menu-path.json)：找出所有 `parent != null` 的 skill 子項目
  - [prompt-chpaters.md](prompt-chpaters.md)：作為對 Vertex AI 的提示詞
- 對每個 skill 呼叫 Vertex AI，產生「章節目錄（Category 清單）」的 JSON 陣列，並包成 content.info：
  - 輸出路徑：`output/{skill_id}/content.info`
  - 內容大致包含：
	 - `skillId`, `skillName`, `skillNameEnglish`, `categoryName`
	 - `totalChapterNumber`, `isChaptersCompleted`, `chapters`（模型產生的章節陣列）

### 使用方式

在本目錄（ai/workflow/skills）中執行：

1. 產生所有 skills 的 content.info（若檔案已存在會跳過）：
	- `python generate_skill_info.py`

2. 只產生 / 覆寫單一 skill（例如 `typescript`）：
	- `python generate_skill_info.py --force --skill-id typescript`

3. 強制覆寫所有既有的 content.info：
	- `python generate_skill_info.py --force`

說明：
- 沒有加 `--force` 時，若 `output/{skill_id}/content.info` 已存在，會顯示提示並略過該 skill。
- `--skill-id` 僅處理指定 id 的項目（id 來自 [menu-path.json](menu-path.json) 的 `items[].id`）。

### generate_skill_materials.py：依章節產生技能教材 Markdown

腳本位置： [generate_skill_materials.py](generate_skill_materials.py)

功能：
- 讀取：
	- [PROJECT_ID.txt](PROJECT_ID.txt)：取得 `PROJECT_ID`
	- [output](output) 底下各個 skill 目錄中的 `content.info`（先由 generate_skill_info.py 產生）
	- [prompt-materials.md](prompt-materials.md)：作為對 Vertex AI 的提示詞
- 對每個 skill 的每一個 chapter 產生一份 Markdown 教材：
	- 讀取 `content.info` 中的 `chapters` 陣列（每個元素代表一個章節）
	- 對每個章節呼叫 Vertex AI 生成內容
	- 輸出路徑：`output/{skill_id}/{chapterId}.md`（例如：`output/typescript/chapter01.md`）

使用方式（在本目錄 ai/workflow/skills 執行）：

1. 為所有 skills 的所有章節產生教材（若檔案已存在會跳過）：
	- `python generate_skill_materials.py`

2. 只為指定 skill 產生 / 覆寫教材（例如 `typescript`）：
	- `python generate_skill_materials.py --force --skill-id typescript`

3. 強制覆寫所有 skills 的所有章節教材：
	- `python generate_skill_materials.py --force`

說明：
- 沒有加 `--force` 時，若 `output/{skill_id}/{chapterId}.md` 已存在，會顯示提示並略過該章節。
- `--skill-id` 僅處理指定 skill 目錄（名稱來自 output 底下的資料夾，例如 `typescript`, `gcp`）。

### generate_skill_questions_from_materials.py：依教材產生題目 JSON 與 meta

腳本位置： [generate_skill_questions_from_materials.py](generate_skill_questions_from_materials.py)

功能：
- 讀取：
	- [PROJECT_ID.txt](PROJECT_ID.txt)：取得 `PROJECT_ID`
	- [output](output) 底下各個 skill 目錄中的 `content.info`（章節清單）
	- 每個章節的教材 Markdown：`output/{skill_id}/{chapterId}.md`
	- 題目 meta：`output/{skill_id}/{chapterId}.questions-meta.json`（若不存在會自動建立）
	- [prompt-skill-questions.md](prompt-skill-questions.md)：作為對 Vertex AI 的出題提示詞
- 對每個 skill 的每一個 chapter：
	- 依 meta 中的目標題數 `totalQuestionsNum` 與既有題目數，計算尚需補齊的題數
	- 呼叫 Vertex AI 產生一批新的題目（避免與 meta 中既有題目重複）
	- 更新：
		- 題目檔：`output/{skill_id}/{chapterId}.json`
		- meta 檔：`output/{skill_id}/{chapterId}.questions-meta.json`

`{chapterId}.questions-meta.json` 主要結構：
- `totalQuestionsNum`：目標總題數（預設 15，可手動修改）
- `questions`：每題的摘要資訊（id、難度、題型、tags、題幹摘要等）
- `isAllCompleted`：是否已達到 `totalQuestionsNum`

使用方式（在本目錄 ai/workflow/skills 執行）：

1. 為所有 skills 的所有章節產生 / 補齊題目：
	- `python generate_skill_questions_from_materials.py`

2. 只為指定 skill 產生 / 補齊題目（例如 `typescript`）：
	- `python generate_skill_questions_from_materials.py --skill-id typescript`

3. 只為指定 skill 的指定章節（例如 `chapter01`）產生 / 補齊題目：
	- `python generate_skill_questions_from_materials.py --skill-id typescript --chapter-id chapter01`

4. 強制重跑（清空該章節既有題目與 meta 記錄，重新出題）：
	- `python generate_skill_questions_from_materials.py --force --skill-id typescript --chapter-id chapter01`

說明：
- 沒有加 `--force` 時，腳本會保留既有題目，只會「補齊」尚未達到 `totalQuestionsNum` 的部分。
- meta 檔中的 `totalQuestionsNum` 可手動調整，腳本會依新目標在後續執行中繼續補齊。
- `--skill-id`、`--chapter-id` 可以單獨或一起使用，控制出題範圍。

---

### Handbook pipeline：為每個 skill 建立技術手冊與題庫

在既有「章節教材 + 題庫」之外，你可以為每個 skill 再加上一組「技術手冊 / Handbook」，專注在實戰心智模型、patterns/anti‑patterns 與 troubleshooting。

Handbook 流程分成四個步驟：

1. 在 `content.json` 開頭插入 `handbook` entry
2. 為每個 skill 產生 `handbook.json`（Category）
3. 為每個 handbook topic 產生 Markdown 章節
4. 為每個 handbook topic 產生題庫 JSON + meta

#### 1) add_handbook_to_skill_content.py：在 content.json 中插入 handbook

腳本位置： [add_handbook_to_skill_content.py](add_handbook_to_skill_content.py)

功能：
- 讀取 [menu-path.json](menu-path.json)，找出所有 `parent != null` 的 skill。
- 對每個 `output/{skill}/content.json`：
	- 若 `items` 中已有 `id == "foundamental"`，不做任何變更。
	- 若沒有 `foundamental`，且也沒有 `handbook`，則在 `items` 最前面插入：

		```jsonc
		{
			"id": "handbook",
			"t": "技術手冊",
			"en": "Handbook",
			"pointTo": {
				"type": "category",
				"data": "github/json",
				"dataLocation": "https://github.com/feelryan/jujuen/blob/skills/{skill}/handbook.json"
			}
		}
		```

使用方式（在本目錄 ai/workflow/skills 執行）：

- 處理所有 skills：

	```bash
	python add_handbook_to_skill_content.py
	```

- 只處理單一 skill（例如 `typescript`）：

	```bash
	python add_handbook_to_skill_content.py --skill-id typescript
	```

#### 2) generate_handbook_sections.py：產生 handbook.json 章節清單

腳本位置： [generate_handbook_sections.py](generate_handbook_sections.py)

功能：
- 讀取：
	- [PROJECT_ID.txt](PROJECT_ID.txt)：取得 `PROJECT_ID`
	- [menu-path.json](menu-path.json)：取得 skill 名稱與所屬大類別
	- `output/{skill}/content.info`（若存在，會用其 `chapters` 作為 overview）
	- [prompt-handbook-category.md](prompt-handbook-category.md)：handbook 章節設計提示詞
- 對每個 skill 呼叫 Vertex AI 產生 handbook 章節 Category，寫入：
	- `output/{skill}/handbook.json`
- `handbook.json` 結構：
	- `id: "handbook"`, `title: "Handbook for {skill}"`
	- `items` 內每個主題會自動帶上：
		- 主章節：指向 `github/md: .../{skill}/handbook/{topic_id}.md`
		- 對應 quiz 子節點：指向 `github/json: .../{skill}/handbook/{topic_id}.json`，並加上 `renderObject: "Question"`

使用方式：

- 為所有 skills 產生 handbook.json（若已存在則略過）：

	```bash
	python generate_handbook_sections.py
	```

- 只為指定 skill 產生 / 覆寫 handbook.json：

	```bash
	python generate_handbook_sections.py --force --skill-id typescript
	```

#### 3) generate_handbook_section_material.py：產生 handbook 章節 Markdown

腳本位置： [generate_handbook_section_material.py](generate_handbook_section_material.py)

功能：
- 讀取：
	- [PROJECT_ID.txt](PROJECT_ID.txt)
	- `output/{skill}/handbook.json`
	- [prompt-handbook-section-material.md](prompt-handbook-section-material.md)
- 僅針對 handbook.json 中 **非 `-quiz` 結尾** 的 items：
	- 呼叫 Vertex AI，產生對應 Markdown 章節：
		- `output/{skill}/handbook/{topic_id}.md`

使用方式：

- 為所有已產生 handbook.json 的 skills 產生（尚未存在的）handbook 章節 Markdown：

	```bash
	python generate_handbook_section_material.py
	```

- 只為某個 skill 的所有 handbook 章節產生 Markdown（例如 `typescript`）：

	```bash
	python generate_handbook_section_material.py --skill-id typescript
	```

- 只產生 / 覆寫單一 handbook 主題（例如 `core-concepts`）：

	```bash
	python generate_handbook_section_material.py \
		--skill-id typescript \
		--topic-id core-concepts \
		--force
	```

#### 4) generate_questions_from_handbook_section_material.py：為每個 handbook 章節產生題庫

腳本位置： [generate_questions_from_handbook_section_material.py](generate_questions_from_handbook_section_material.py)

功能：
- 讀取：
	- [PROJECT_ID.txt](PROJECT_ID.txt)
	- `output/{skill}/handbook.json`
	- 各 handbook 章節 Markdown：`output/{skill}/handbook/{topic_id}.md`
	- 題目 meta：`output/{skill}/handbook/{topic_id}.questions-meta.json`（若不存在會自動建立）
	- [prompt-handbook-questions.md](prompt-handbook-questions.md)
- 對每個 handbook 主題：
	- 依 meta 中 `totalQuestionsNum` 與既有題目數，計算尚需補齊題數（預設 12 題，可手動調整）。
	- 呼叫 Vertex AI 產生新題目，更新：
		- 題目檔：`output/{skill}/handbook/{topic_id}.json`
		- meta 檔：`output/{skill}/handbook/{topic_id}.questions-meta.json`

使用方式：

- 為所有已產生 handbook.json 的 skills 的所有 handbook 主題產生 / 補齊題目：

	```bash
	python generate_questions_from_handbook_section_material.py
	```

- 只為某個 skill 的所有 handbook 主題產生 / 補齊題目（例如 `typescript`）：

	```bash
	python generate_questions_from_handbook_section_material.py --skill-id typescript
	```

- 只針對單一 handbook 主題重跑題目：

	```bash
	python generate_questions_from_handbook_section_material.py \
		--skill-id typescript \
		--topic-id core-concepts \
		--force
	```

完成以上四步後，只要把 `handbook.json` 與 `handbook/{topic_id}.md`、`handbook/{topic_id}.json` 上傳到 GitHub 上對應的 skills repo（例如 `skills/typescript/handbook/...`），前端就能透過在 `content.json` 中的 `handbook` entry 載入整套技術手冊與練習題。

### verify_question_answers.py：修正題目 JSON 的 options / answer 格式並標記 verified

腳本位置： [verify_question_answers.py](verify_question_answers.py)

功能：
- 掃描 [output](output) 目錄（或指定 skill / 指定檔案）下的所有 `*.json`。
- 對於「內容為 JSON 陣列，且陣列元素中包含 `answer` 欄位」的檔案，視為題目題庫 JSON（Question 格式）。
- 只處理尚未有 `verified` 欄位的題目（陣列元素）：
  - 將這些題目分批送給 Vertex AI，根據 `question`、`options`、`type` 判斷正確答案。
  - 統一 `options` 與 `answer` 的格式：
    - `options`：依順序在每個選項的 `t` / `en` 開頭加上 `(A) `、`(B) `、`(C) `⋯，若原本已有 `A.`、`(1)` 等標號會先移除再改為標準格式。
    - `answer`：
      - 單選題：必須是單一大寫英文字母，例如 `"A"`、`"B"`。
      - 複選題：必須是大寫英文字母、以半形逗號分隔且不含空白，例如 `"A,B"`。
  - 其他欄位（例如 `no`、`level`、`question`、`why`、`wg`）會盡量保持原樣，不會被改動。
- 每題修正後，腳本會在該題目物件上新增 `verified` 欄位，其值為 ISO 格式時間字串（例如 `"2026-03-17T10:23:45"`）。
- 若腳本中途中斷，下次重新執行時會自動略過已有 `verified` 的題目，只處理尚未驗證的部分。

使用方式（在本目錄 ai/workflow/skills 執行）：

1. 掃描 output 底下所有 skills 的所有題目 JSON，批次修正 options / answer 格式：

	```bash
	python verify_question_answers.py
	```

2. 調整每次送給模型的題數上限（預設 8 題一批）：

	```bash
	python verify_question_answers.py --max-per-request 4
	```

3. 只處理指定 skill 目錄（例如只修正 `output/typescript` 底下的題目檔）：

	```bash
	python verify_question_answers.py --skill-id typescript
	```

4. 只處理單一 JSON 檔案：

	- 給絕對路徑：

		```bash
		python verify_question_answers.py --file "c:/Data_Sets/ai/workflow/skills/output/typescript/handbook/anti-patterns.json"
		```

	- 或使用相對於 `output/` 的路徑：

		```bash
		python verify_question_answers.py --file "typescript/handbook/anti-patterns.json"
		```

說明：
- `--file` 與 `--skill-id` 可擇一使用；當同時提供時，以 `--file` 為主，只處理該單一檔案。
- `--max-per-request` 用來控制單次送給 Vertex AI 的題目數量，若單題內容較長（ex: 很多程式碼、說明）可以調小以避免超過模型限制。
- 腳本不會修改 `verified` 以外的新欄位結構；所有與題意有關的欄位（如 `question`、`why`）都會儘量保持不變。


