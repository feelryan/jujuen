# Steps

> gcloud auth application-default login

> gcloud auth login

> gcloud config set project project-eb8a9e28-ffd0-498a-b09

> modify PROJECT_ID.txt


1. Run strategy with JD

- strategy sections

```bash
py.exe generate_strategy_sections.py --resume "Ryan Hsiao 03202026.pdf" --jd "JD(Synthesis Health_Sr. Platform Engineer).pdf" --dir-name "Ryan Hsiao 03202026_JD(Synthesis Health_Sr. Platform Engineer)"
```

- sections content

```bash
py.exe generate_strategy_section_material.py --resume "Ryan Hsiao 03202026.pdf" --jd "JD(Synthesis Health_Sr. Platform Engineer).pdf" --dir-name "Ryan Hsiao 03202026_JD(Synthesis Health_Sr. Platform Engineer)"
```

- sections questions

```bash
py.exe generate_questions_from_strategy_section_material.py --resume "Ryan Hsiao 03202026.pdf" --jd "JD(Synthesis Health_Sr. Platform Engineer).pdf" --dir-name "Ryan Hsiao 03202026_JD(Synthesis Health_Sr. Platform Engineer)"
```

2. Adjust resume

3. Run interview sections, materials

# Job Interview Topics Pipeline

這個目錄底下有一套兩階段的流程，用 **履歷 PDF** 和 **可選的 JD PDF** 自動產生：

1. 一份符合 site Category 規格的 `content.json`（章節 / 面試節點清單）。
2. 每個章節對應的一份 Markdown 筆記（{sectionId}.md），可直接用來準備面試。

---

## 0. 前置準備

1. **Python 與套件**
   - 建議使用 Python 3.10+。
   - 安裝 Google GenAI Python SDK（若尚未安裝）：

     ```bash
     pip install google-genai
     ```

2. **GCP 專案與權限**
   - 確保已在本機完成：

     ```bash
     gcloud auth application-default login
     ```

   - 在 `workflow/job/PROJECT_ID.txt` 中填入有效的 GCP Project ID（只需要 ID，不是專案名稱）。

3. **準備履歷與 JD PDF 檔**
   - 履歷 PDF：例如 `Ryan Hsiao (2026-03).pdf`，放在 `workflow/job/` 或任一方便的位置。
   - JD PDF（可選）：例如 `JD-SWE.pdf`。

> 兩個階段的腳本都會直接把 **PDF 檔本身** 傳給 Vertex AI，由模型解析內容，不需要先轉成純文字。

---

## 1. 產生章節清單：`generate_interview_sections.py`

這支腳本會根據履歷 PDF（與可選的 JD PDF），請 AI 設計一份 **面試章節 / 面試節點清單**，並寫成 Category JSON：

- 輸入：
  - `--resume`：履歷 PDF 檔路徑（必填）。
  - `--jd`：JD PDF 檔路徑（選填）。
  - `--force`：如目標目錄已有 `content.json`，是否強制覆寫（選填）。

- 輸出：
  - 目錄：`workflow/job/output/{resume_base}` 或 `workflow/job/output/{resume_base}_{jd_base}`
    - `resume_base` = 履歷檔名去掉副檔名
    - `jd_base` = JD 檔名去掉副檔名
  - 檔案：`content.json`，結構為 Category：

    ```jsonc
    {
      "id": "{dir_name}",
      "title": "Interview Topics for {resume_base}",
      "items": [
        {
          "id": "section-id",
          "t": "中文標題 / Chinese title",
          "en": "English title",
          "description": "中英混合的簡短說明",
          "pointTo": {
            "type": "document",
            "data": "github/md",
            "dataLocation": "https://github.com/feelryan/jujuen/blob/ryan/{resume_base}/{section-id}.md"
          }
        }
      ]
    }
    ```

### 1.1 執行範例

在 `workflow/job` 目錄中執行：

- 僅使用履歷 PDF：

  ```bash
  python generate_interview_sections.py \
    --resume "resume-031026.pdf"
  ```

  會產出：

  - `workflow/job/output/Ryan Hsiao (2026-03)/content.json`

- 使用履歷 + JD PDF：

  ```bash
  py.exe generate_interview_sections.py --resume "resume-031026.pdf" --jd "JD(Google-SSE-4370706338).pdf"
  ```

  會產出：

  - `workflow/job/output/Ryan Hsiao (2026-03)_JD-SWE/content.json`

- 如需覆寫既有 `content.json`：

  ```bash
  python generate_interview_sections.py \
    --resume "Ryan Hsiao (2026-03).pdf" \
    --jd "JD-SWE.pdf" \
    --force
  ```

---

## 2. 產生各章節 Markdown：`generate_interview_section_materials.py`

這支腳本會讀取前一階段產生的 `content.json`，對其中每個 `items[i]`（section）呼叫 AI，生成對應的 Markdown 筆記 `{sectionId}.md`。

- 輸入：
  - `--resume`：同第一階段的履歷 PDF（必填）。
  - `--jd`：同第一階段的 JD PDF（若第一階段有用，建議第二階段也一樣帶入）。
  - `--dir-name`：目標子目錄名稱（必填），需與第一階段 output 目錄相同，例如：
    - `"Ryan Hsiao (2026-03)"`
    - `"Ryan Hsiao (2026-03)_JD-SWE"`
  - `--section-id`：只生成特定章節的 Markdown（選填）。
  - `--force`：如已存在 `{sectionId}.md`，是否強制覆寫（選填）。

- 依據 `content.json.items` 中的每個 item：
  - 使用其中的：`id` / `t` / `en` / `description`。
  - 組成 prompt（加上整體章節 overview）。
  - 對每一個 section 產生：
    - `workflow/job/output/{dir_name}/{sectionId}.md`

### 2.1 執行範例

假設第一階段已產生：

- `workflow/job/output/Ryan Hsiao (2026-03)_JD-SWE/content.json`

在 `workflow/job` 目錄中執行：

- 產生所有章節的 Markdown：

  ```bash
  py.exe generate_interview_section_materials.py --resume "resume-031026.pdf" --jd "JD(Google-SSE-4370706338).pdf" --dir-name "resume-031026_JD(Google-SSE-4370706338)"
  ```

  會在該目錄底下依章節 id 產生多個檔案，例如：

  - `workflow/job/output/Ryan Hsiao (2026-03)_JD-SWE/recruiter-screen.md`
  - `workflow/job/output/Ryan Hsiao (2026-03)_JD-SWE/system-design.md`
  - `...`

- 僅產生單一章節（例如 `system-design`）：

  ```bash
  python generate_interview_section_materials.py \
    --resume "Ryan Hsiao (2026-03).pdf" \
    --jd "JD-SWE.pdf" \
    --dir-name "Ryan Hsiao (2026-03)_JD-SWE" \
    --section-id "system-design"
  ```

- 覆寫既有 Markdown：

  ```bash
  python generate_interview_section_materials.py \
    --resume "Ryan Hsiao (2026-03).pdf" \
    --jd "JD-SWE.pdf" \
    --dir-name "Ryan Hsiao (2026-03)_JD-SWE" \
    --force
  ```

---

## 3. 與 GitHub / JuJuEn 的整合

- `content.json` 中每個 item 的 `pointTo.dataLocation`，已預先指向：

  ```text
  https://github.com/feelryan/jujuen/blob/ryan/{resume_base}/{sectionId}.md
  ```

- 也就是說：
  - 你可以在 JuJuEn 的 `ryan` 分支底下建立 `{resume_base}/` 目錄，
  - 把本地產生的 `{sectionId}.md` 上傳到該目錄，
  - 前端就能透過 Category / MenuPath 結構載入這些章節筆記。

---

## 4. 常見問題

- **Q: 為什麼兩個階段都需要傳入 PDF？**
  - A: 第一階段用來設計整體章節清單；第二階段在寫每個章節細節時，仍需從履歷/JD 抽取具體案例與細節，所以也需要同樣的 PDF。

- **Q: 可以只用履歷、沒有 JD 嗎？**
  - A: 可以。只要省略 `--jd` 參數，系統會依一般高階全端工程師面試流程做合理假設。

- **Q: 如果想重新調整章節結構？**
  - A: 可以先刪除對應 `output/{dir_name}/content.json`，或使用 `--force` 重新產生，必要時也可手動編輯 `content.json` 再跑第二階段。

---

## 5. 「最佳策略 / Best Strategy」Pipeline

當你在第 1 階段呼叫 `generate_interview_sections.py` 並 **有提供 JD PDF** 時，產生的 `content.json` 會自動在 `items` 末端加入一個：

- `id: "strategy"`
- `t: "最佳策略 / Best Strategy"`, `en: "Best Strategy"`
- `pointTo` 指向：`{GITHUB_BASE}/{resume_base}/strategy.json`（`type: "category"`, `data: "github/json"`）

接下來可以用以下三支腳本，建立完整的「最佳攻略」章節、內容與題庫。

### 5.1 產生策略章節：`generate_strategy_sections.py`

這支腳本會根據履歷 PDF + JD PDF，請 AI 設計一份「最佳策略」的章節清單，並寫成 `strategy.json`（Category 格式）：

- 輸入：
  - `--resume`：履歷 PDF 檔路徑（必填）。
  - `--jd`：JD PDF 檔路徑（必填）。
  - `--dir-name`：output 子目錄名稱（選填，不填則預設為 `{resume_base}_{jd_base}`）。
  - `--force`：如已有 `strategy.json`，是否強制覆寫（選填）。

- 輸出：
  - 目錄：`workflow/job/output/{dir_name}`
  - 檔案：`strategy.json`，結構為 Category：

    ```jsonc
    {
      "id": "strategy",
      "title": "Best Strategy for {resume_base} vs {jd_base}",
      "items": [
        {
          "id": "topic-id",
          "t": "策略主題中文標題",
          "en": "Strategy topic English title",
          "description": "中英簡短說明",
          "pointTo": {
            "type": "document",
            "data": "github/md",
            "dataLocation": "{GITHUB_BASE}/{resume_base}/strategy/topic-id.md"
          }
        },
        {
          "id": "topic-id-quiz",
          "parent": "topic-id",
          "t": "... - 測驗 / Quiz",
          "en": "... - Quiz",
          "pointTo": {
            "type": "document",
            "data": "github/json",
            "dataLocation": "{GITHUB_BASE}/{resume_base}/strategy/topic-id.json"
          }
        }
      ]
    }
    ```

#### 執行範例

```bash
py.exe generate_strategy_sections.py --resume "Ryan Hsiao 03202026.pdf" --jd "JD(Synthesis Health_Sr. Platform Engineer).pdf" --dir-name "Ryan Hsiao 03202026_JD(Synthesis Health_Sr. Platform Engineer)"
```

---

### 5.2 產生策略 Markdown：`generate_strategy_section_material.py`

這支腳本會讀取 `output/{dir_name}/strategy.json`，對其中每個 **主策略主題**（id 不以 `-quiz` 結尾）產生一份 Markdown 策略說明 `{topic_id}.md`。

- 輸入：
  - `--resume`：履歷 PDF 檔路徑（必填）。
  - `--jd`：JD PDF 檔路徑（必填）。
  - `--dir-name`：與 `strategy.json` 所在的 output 子目錄名稱（必填）。
  - `--topic-id`：只產生特定策略主題的 Markdown（選填）。
  - `--force`：如已存在 `{topic_id}.md`，是否強制覆寫（選填）。

- 輸出：
  - 目錄：`workflow/job/output/{dir_name}/strategy/`
  - 檔案：`{topic_id}.md`（每個策略主題一份）。

#### 執行範例

```bash
py.exe generate_strategy_section_material.py --resume "resume-031026.pdf" --jd "JD(Taskify_Software Engineer).pdf" --dir-name "resume-031026_JD(Taskify_Software Engineer)"
```

只針對單一主題（例如 `resume-tailoring`）：

```bash
python generate_strategy_section_material.py \
  --resume "resume-031026.pdf" \
  --jd "JD-SWE.pdf" \
  --dir-name "resume-031026_JD-SWE" \
  --topic-id "resume-tailoring" \
  --force
```

---

### 5.3 產生策略題庫：`generate_questions_from_strategy_section_material.py`

這支腳本會根據每個策略主題的 Markdown（`strategy/{topic_id}.md`）以及履歷 / JD PDF，產生對應的題庫 JSON 與 meta 檔。

- 輸入：
  - `--resume`：履歷 PDF 檔路徑（必填）。
  - `--jd`：JD PDF 檔路徑（必填）。
  - `--dir-name`：與 `strategy.json` 和 `strategy/*.md` 所在的 output 子目錄名稱（必填）。
  - `--topic-id`：只產生特定策略主題的題目（選填）。
  - `--force`：重新產生題目並覆寫既有檔案（選填）。

- 輸出（每個主題）：
  - `workflow/job/output/{dir_name}/strategy/{topic_id}.json`：實際題目陣列（Question JSON）。
  - `workflow/job/output/{dir_name}/strategy/{topic_id}.questions-meta.json`：題數統計與摘要（meta 資料）。

#### 執行範例

```bash
py.exe generate_questions_from_strategy_section_material.py --resume "resume-031026.pdf" --jd "JD(Taskify_Software Engineer).pdf" --dir-name "resume-031026_JD(Taskify_Software Engineer)"
```

或只針對單一主題：

```bash
python generate_questions_from_strategy_section_material.py \
  --resume "resume-031026.pdf" \
  --jd "JD-SWE.pdf" \
  --dir-name "resume-031026_JD-SWE" \
  --topic-id "resume-tailoring" \
  --force
```

完成後，只要把 `strategy.json` 與 `strategy/{topic_id}.md`、`strategy/{topic_id}.json` 上傳到對應 GitHub 路徑，前端就能透過 `Best Strategy` 節點載入整套最佳攻略內容與練習題。
