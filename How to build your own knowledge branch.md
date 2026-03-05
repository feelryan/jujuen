# How to build your own knowledge branch / 如何建立自己的知識分支

This document describes, at a high level, how to use Python scripts and AI to build a complete "knowledge branch" – including navigation (MenuPath / Category / Document) and learning content (Markdown, Words, Question JSON).  
本文件以概略方式說明，如何透過 Python 腳本與 AI，自動建立完整的「知識分支」──包含導覽結構（MenuPath / Category / Document）以及學習內容（Markdown、Words、Question JSON）。

---

## 1. Create your GitHub branch / 建立你的 GitHub 分支

1. Sign in to GitHub and go to the main repository.  
	 登入 GitHub，進入主專案倉庫。  
2. Create a new branch for your topic (for example: `ancient-classics`, `junior-high`, `basic-pronunciation`).  
	 為你的主題建立一個新的分支（例如：`ancient-classics`、`junior-high`、`basic-pronunciation`）或者從頭開始 or from the scratch 則挑選主支來複製 then braching out from `main` master brach (`main`)。  
3. All files for this knowledge branch will live under this branch.  
	 此知識分支相關的所有檔案，都會放在這個分支底下。

---

## 2. Design top-level navigation with MenuPath / 用 MenuPath 設計頂層導覽

The entry point of each knowledge branch is a `menu-path.json` file at the branch root.  
每一個知識分支的入口是一個放在分支根目錄的 `menu-path.json` 檔案。  

- **MenuPath** describes the top-level navigation tree (categories and leaf items).  
	**MenuPath** 用來描述頂層導覽樹（大類與底下的項目）。  
- Each item can either be a pure category, or point to a detail page via `pointTo`.  
	每個項目可以只是分類節點，也可以透過 `pointTo` 連到詳細內容頁。  
- Typical pattern:  
	典型的設計模式：  
	- Top-level: major themes or domains (e.g. Ancient Chinese Classics, Cloud Architect, Junior High Subjects).  
		頂層：主要主題或領域（例如：中國古書、雲端架構師、國中科目）。  
	- Under each theme: concrete books, courses, or modules, each linked to its own Category JSON.  
		每個主題底下：具體的書籍、課程或模組，每一個會連到自己的 Category JSON。

Examples / 範例：  
- `google-generative-ai-leader/menu-path.json`  
- `basic-pronunciation/menu-path.json`  
- `google-professional-cloud-architect/menu-path.json`

---

## 3. Create per-book (or per-course) Category skeletons / 為每本書（或每個課程）建立 Category 骨架

For each leaf item in MenuPath (for example, a specific book or course), you create a Category JSON file that will hold the chapter or unit list.  
對於 MenuPath 中的每個葉節點（例如：某一本書或某一門課），需要建立一個 Category JSON 檔，裡面會放章節或單元清單。  

Typical structure / 典型結構：  
- File location: `/{branch}/{book_id}/content.json` (or under a local `output/{book_id}` folder during generation).  
	檔案位置：`/{branch}/{book_id}/content.json`（或在產生過程中先放在本機 `output/{book_id}` 資料夾）。  
- Fields:  
	欄位大致包含：  
	- `id`: book or course id / 書或課程的 id。  
	- `title`: display title / 顯示用標題。  
	- `items`: initially an empty array, later filled with chapter items.  
		`items`：一開始是空陣列，之後由腳本填入各章節項目。

At this stage, you only decide which "books / modules" exist; detailed chapters are filled later by scripts and AI.  
在這個階段，你只需要決定有哪些「書 / 模組」；後續由腳本與 AI 自動補上章節細節。

---

## 4. Use AI to discover chapter names / 先用 AI 蒐集章節名稱

Once your books (or modules) are defined, you run a Python script (for example `generate_chapter_names.py`) to ask the AI to:  
當書目或課程模組設定好之後，可以執行一支 Python 腳本（例如 `generate_chapter_names.py`），讓 AI 來完成：  

- Estimate how many chapters or sections each book has.  
	估計每本書大約有多少章節或段落。  
- Produce an ordered list of chapter titles for each book.  
	產生每本書的章節標題清單（有順序）。  
- Save the result into a per-book info file, such as `output/{book_id}/content.info`.  
	結果存成每本書專用的資訊檔，例如 `output/{book_id}/content.info`。  

The script is incremental and resumable: if a book has many chapters, it can call the AI multiple times, each time extending the chapter list until complete.  
這個腳本支援「增量、可續跑」：若一本書章節眾多，可以分次詢問 AI，每次都在原有清單後面繼續補齊，直到完成為止。

---

## 5. Build chapter-level navigation (Category items) / 產生章節層級的 Category 項目

After chapter names are ready, another script (for example `generate_chapters.py`) reads each book's `content.info` and populates its `content.json` with chapter items.  
當章節名稱準備好之後，另一支腳本（例如 `generate_chapters.py`）會讀取每本書的 `content.info`，並把章節項目寫入該書的 `content.json` 中。  

What this script does / 腳本會做的事：  
- For each chapter name, create a Category item representing that chapter.  
	針對每一個章節名稱，建立一個代表該章節的 Category 項目。  
- For each chapter, also create a linked quiz entry that points to `{chapter}-quiz.json`.  
	同時為每章建立一個對應的小測驗項目，指向 `{chapter}-quiz.json`。  
- Each chapter item typically points to a Words JSON document (e.g. `{chapter}.json`) that holds the chapter's learning content.  
	每個章節項目通常會 `pointTo` 一個 Words JSON 文件（例如 `{chapter}.json`），裡面放該章的學習內容。  

At this point, your navigation tree is complete down to the chapter level, but actual content pages and quizzes are still to be generated.  
到這個步驟為止，你的導覽樹已經細到「章節等級」，但實際的內容頁與題目還需要再由後續流程產生。

---

## 6. Collect original text for each chapter / 為每章蒐集原文內容

To keep long texts manageable and resumable, you use another Python script (for example `generate_chapter_original_content.py`) to iteratively collect the original text for each chapter.  
為了處理篇幅很長的內容並且可中斷續跑，可以透過另一支 Python 腳本（例如 `generate_chapter_original_content.py`）來「逐步蒐集每一章的原文」。  

High-level behavior / 高層次行為：  
- For each chapter, the script maintains a `{chapter}_original.info` file under that book's folder.  
	對每一章，腳本會在對應書目錄底下維護一個 `{chapter}_original.info` 檔。  
- This file records how many sections the chapter is split into, and the original sentences for each section.  
	檔案中紀錄本章被切成多少段（sections），以及每段的原文句子陣列。  
- The script can be run multiple times; each run asks the AI to add new sections until the chapter is fully collected.  
	腳本可以重複執行；每次執行都會請 AI 補上一些尚未完成的段落，直到整章原文收集完畢。  

This gives you a structured, machine-readable representation of the original text, which later scripts can transform into learning formats.  
這樣就能得到一份結構化、可機器處理的原文表示，供後續腳本轉換成各種學習格式。

---

## 7. Generate Words JSON (per chapter) / 產生每章的 Words JSON

With `{chapter}_original.info` ready, a dedicated script (for example `generate_chapter_content.py`) uses AI to convert the original sentences into a Words array for each chapter.  
當 `{chapter}_original.info` 準備好後，一支專門的腳本（例如 `generate_chapter_content.py`）會利用 AI，將原文句子轉換成每章專屬的 Words 陣列。  

Conceptually / 概念上它會：  
- Read all original sections of a chapter and group them into logical segments.  
	讀入某章所有的原文段落，依結構整理成合適的區塊。  
- Ask the AI to output a `Words[]` JSON, where each element contains:  
	請 AI 產生 `Words[]` JSON，每個元素包含：  
	- `tag`: display hint (e.g. paragraph, list item, heading).  
		`tag`：顯示提示（例如段落、列表項、標題）。  
	- `t` / `c`: traditional / simplified Chinese.  
		`t` / `c`：繁體 / 簡體中文。  
	- `p` / `z`: pinyin and zhuyin for the Chinese text.  
		`p` / `z`：對應中文字的拼音與注音。  
	- `en`: English translation or explanation.  
		`en`：英文翻譯或說明。  
	- `wg`: word-groups (vocabulary chunks with part-of-speech tags).  
		`wg`：字詞群組（包含詞性標註的重點字詞）。  
- Save the result as `{chapter}.json` under the appropriate folder.  
	將結果存成 `{chapter}.json`，放在對應的目錄中。  

The front-end can then render these Words arrays as rich, multi-lingual content pages.  
前端系統就可以根據這些 Words 陣列，呈現出多語、可閱讀又易於學習的內容頁。

---

## 8. Generate life-scenario quiz questions / 產生生活化的章節測驗題

To reinforce learning, another script (for example `generate_chapter_quiz.py`) uses the collected original text to create a small set of multiple-choice questions for each chapter.  
為了加強學習效果，還可以透過另一支腳本（例如 `generate_chapter_quiz.py`），利用已收集的原文內容，為每一章產生少量的選擇題。  

High-level idea / 高層次概念：  
- For each chapter, gather a representative subset of its original sentences.  
	每一章先收集一小部分具有代表性的原文句子。  
- Ask the AI to design about 5–8 life-based scenarios where the chapter's ideas can be applied (school, family, work, social media, etc.).  
	請 AI 根據這些原文，設計約 5–8 題生活情境題（學校、家庭、工作、社群媒體等）。  
- Each question follows the same JSON structure as your junior-high question format (including `question[]`, `options[]`, `answer`, `why`).  
	每一題沿用國中題目的 JSON 結構（含 `question[]`、`options[]`、`answer`、`why`）。  
- Save per-chapter quizzes as `{chapter}-quiz.json`.  
	每章的題目存成 `{chapter}-quiz.json`。  

These quiz files are then linked from the chapter items in Category, allowing the front-end to show a "Practice" or "Quiz" entry under each chapter.  
這些測驗檔會從 Category 的章節項目連結出去，讓前端在每一章底下提供「練習 / 測驗」的入口。

---

## 9. Optional: Markdown source and other formats / 選用：Markdown 原始稿與其他格式

In some branches (for example junior-high textbooks), you may also keep the source teaching material as Markdown files, and use Python scripts + AI to convert them into Words or Question JSON.  
在某些知識分支，你也可以保留 Markdown 形式的教學原稿，再透過 Python 腳本與 AI 轉換成 Words 或 Question JSON。  

Key idea / 核心概念：  
- Markdown is the human-writable source.  
	Markdown 是人類可讀易寫的來源格式。  
- Words / Question JSON are the machine-friendly, front-end-ready formats.  
	Words 與 Question JSON 則是機器友善、前端可直接使用的內容格式。  

You can mix both approaches in the same knowledge branch, as long as the navigation (MenuPath + Category + Document) remains consistent.  
只要導覽結構（MenuPath + Category + Document）保持一致，同一個知識分支中可以同時使用「Markdown 來源」與「直接由原文 / AI 產生 JSON」這兩種模式。

---

## 10. Iterate, review, and refine / 反覆產生、檢查與微調

All of the above Python scripts are designed to be **idempotent and resumable**: you can run them multiple times, fix prompts, or adjust branch structure without starting from zero.  
上述所有 Python 腳本都設計成「可重複執行、可中斷續跑」：你可以多次執行、修改 prompt、調整分支結構，而不必每次都從頭來過。  

Suggested workflow / 建議工作流程：  
1. Design MenuPath and Category skeletons.  
	 先設計 MenuPath 與各書的 Category 骨架。  
2. Run chapter-name discovery, then chapter-item generation.  
	 執行章節名稱蒐集，再生成章節導覽項目。  
3. Collect original text per chapter.  
	 為每章逐步收集原文。  
4. Generate Words content and quizzes.  
	 產生 Words 內容與生活化測驗題。  
5. Manually review a few samples; if needed, tweak prompts or thresholds, then re-run.  
	 手動檢查部分章節與題目，若有需要就微調 prompt 或參數，再重新執行腳本。  

By combining a clear navigation model with Python scripts and AI, you can quickly build rich, consistent knowledge branches for very different domains – from classic literature to modern technology courses.  
透過清楚的導覽模型，加上 Python 腳本與 AI，你可以快速為各種不同領域（從古典文學到現代科技課程）建立內容豐富、結構一致的知識分支。

