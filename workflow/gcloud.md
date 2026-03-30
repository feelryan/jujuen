## ds-algo

cd ds-alog

./Scripts/activate

gcloud auth application-default login 

gcloud auth login

gcloud config set project qwiklabs-gcp-02-6deaa64ae3d1

[modify-generate_materials.py] PROJECT_ID = "qwiklabs-gcp-00-2200bc248a74" 

py.exe generate_materials.py

## junior-high
（在 junior-high 目錄下執行：`cd workflow/junior-high`）

### 1. 建立路徑與檔案結構：generate_path.py

1. 用來依照學科 / 年級 / 學期，產生對應的資料夾與路徑設定。  
2. Run：

	py.exe generate_path.py

### 2. 整理原始 PDF 教材：organize_pdfs.py

1. 將原始 PDF 教材搬移或重新命名到正確的結構（例如依科目與年級分類）。  
2. Run：

	py.exe organize_pdfs.py

### 3. 從 PDF 產生教材 Markdown：generate_materials_from_pdfs.py

1. 設定專案給教材解析腳本：

	gcloud config set project qwiklabs-gcp-03-cba49d2607da

2. 確認 `generate_materials_from_pdfs.py` 內的 `PROJECT_ID` 一致。  
3. Run：

	py.exe generate_materials_from_pdfs.py

4. 腳本會呼叫 AI，將各科 PDF 教材轉成對應的 Markdown 教材檔案。  

### 4. 從教材產生題目 JSON：generate_questions_from_materials.py

1. 切換專案給出題腳本：

	gcloud config set project qwiklabs-gcp-00-77090f1a05c2

2. 確認 `generate_questions_from_materials.py` 內的 `PROJECT_ID` 一致。  
3. Run：

	py.exe generate_questions_from_materials.py

4. 會根據各科教材的 Markdown，產生批次的考題 JSON（Question 格式）。  

### 5. 從教材產生 Words JSON：generate_words_from_materials.py

1. 同樣使用專案 `qwiklabs-gcp-00-77090f1a05c2`：

	gcloud config set project qwiklabs-gcp-00-77090f1a05c2

2. 確認 `generate_words_from_materials.py` 內的 `PROJECT_ID` 一致。  
3. Run：

	py.exe generate_words_from_materials.py

4. 會將教材 Markdown 轉成 Words JSON（含 t/c/p/z/en 與字詞群組），供前端顯示多語內容使用。

## ancient-classics

（在 ancient-classics 目錄下執行：`cd workflow/ancient-classics`）

### 1. 產生章節名稱與 content.info

1. 設定專案給章節名稱腳本（與 junior-high 共用）：
   
	gcloud config set project qwiklabs-gcp-00-77090f1a05c2

2. 確認 `generate_chapter_names.py` 內的 `PROJECT_ID` 一致。  
	Run：

	py.exe generate_chapter_names.py

3. 重複執行直到每本書的 `output/{book_id}/content.info` 顯示章節已完成（`isChatpersCompleted = true`）。

### 2. 依章節名稱建立 Category 章節項目

1. 同樣使用專案 `qwiklabs-gcp-00-77090f1a05c2`。  
	確認 `generate_chapters.py` 內的 `PROJECT_ID` 一致。  
2. Run：

	py.exe generate_chapters.py

3. 會依據各書的 `content.info`，把章節與對應 quiz 項目寫入 `output/{book_id}/content.json`。

### 3. 蒐集每章原文：generate_chapter_original_content.py

1. 切換專案給原文蒐集腳本：

	gcloud config set project qwiklabs-gcp-00-4b2022ed24f8

2. 確認 `generate_chapter_original_content.py` 內的 `PROJECT_ID` 一致。  
3. 使用方式示例：

	只處理《孫子兵法》：

	py.exe generate_chapter_original_content.py --book-id "The Art of War"

	py.exe generate_chapter_original_content.py --book-id "Three Hundred Tang Poems"

	或處理全部書：

	py.exe generate_chapter_original_content.py

4. 重複執行上述指令多次，直到每個章節的  
	`output/{book_id}/{chapter_id}_original.info` 裡的 `isAllCompleted` 為 true。

### 4. 將原文轉成 Words：generate_chapter_content.py

1. 切換專案給 Words 轉換腳本：

	gcloud config set project qwiklabs-gcp-01-87da5d8f4a6d

2. 確認 `generate_chapter_content.py` 內的 `PROJECT_ID` 一致。  
3. 使用方式示例：

	py.exe generate_chapter_content.py --book-id "The Art of War"

4. 會根據 `{chapter}_original.info`，為每個 section 產生 `{chapter_id}_sec_{section}.json`，
	全部完成後自動合併成 `{chapter}.json`。  
	若中途失敗，下次再跑會跳過已完成的 section，只補缺的再嘗試合併。

### 5. 產生生活化測驗題：generate_chapter_quiz.py

1. 切回原文與題目共用專案：

	gcloud config set project qwiklabs-gcp-00-4b2022ed24f8

2. 確認 `generate_chapter_quiz.py` 內的 `PROJECT_ID` 一致。  
3. 使用方式示例：

	py.exe generate_chapter_quiz.py --book-id "The Art of War"

4. 會讀取 `{chapter}_original.info` 與章節資訊，為每章產生約 5–8 題生活情境選擇題，
	存成 `output/{book_id}/{chapter_id}-quiz.json`。  已存在的 quiz 檔會被略過，要重生可先刪除再跑。