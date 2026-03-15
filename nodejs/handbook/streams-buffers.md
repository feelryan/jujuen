# 資料流處理：Streams 與 Buffers 實務 / Data Flow: Mastering Streams & Buffers

## Mental model｜心智模型

在 Node.js 中處理資料（特別是 I/O）時，你需要從「整塊處理」思維轉向「流動處理」思維。

### 1. The Assembly Line (生產線模型) vs. The Warehouse (倉庫模型)
- **Warehouse (Buffer/Whole Load):** 傳統做法像是一個倉庫。你必須等卡車把所有貨物（檔案）都卸下來，填滿整個倉庫（記憶體），才能開始清點或加工。如果貨物比倉庫大，系統就會崩潰（Out of Memory）。
- **Assembly Line (Streams):** Stream 就像一條輸送帶。貨物（Chunks）一件件送進來，經過加工站（Transform），然後立刻送出去。不管總貨量有 100GB 還是 1TB，你只需要足夠容納「當下這一件貨物」的空間。

### 2. The Water Tank & Backpressure (水箱與背壓)
這是 Stream 最關鍵但最常被忽略的機制。
- 想像一個漏斗（Writable Stream）。如果你倒水的速度（Reading）快過漏斗流出的速度（Writing），漏斗就會滿出來。
- **Backpressure** 就是漏斗告訴倒水的人：「停！我滿了，先別倒了。」
- 在 Node.js 中，如果忽略 Backpressure 機制，資料會持續堆積在記憶體中（Internal Buffer），直到 Process Crash。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Use `stream.pipeline` instead of `.pipe()`
雖然 `.pipe()` 是經典用法，但它在錯誤處理上有缺陷（例如：當 Destination 報錯時，Source 往往不會自動銷毀，導致 Memory Leak）。
- **Best Practice:** 使用 `stream.pipeline` (Callback style) 或 `stream/promises` 的 `pipeline`。它能確保當管線中任何一個環節出錯時，所有相關的 Streams 都會被正確關閉。

```javascript
const { pipeline } = require('stream/promises');
const fs = require('fs');
const zlib = require('zlib');

async function run() {
  // 自動處理錯誤與資源釋放
  await pipeline(
    fs.createReadStream('input.txt'),
    zlib.createGzip(),
    fs.createWriteStream('input.txt.gz')
  );
  console.log('Pipeline succeeded.');
}
```

### 2. Async Iterators over Event Emitters
現代 Node.js (v10+) 允許你將 Readable Stream 當作 Async Iterable 使用。這比傳統的 `.on('data')` 和 `.on('end')` 更易讀且邏輯更線性。

```javascript
const fs = require('fs');

async function processFile(filePath) {
  const readable = fs.createReadStream(filePath, { encoding: 'utf8' });

  for await (const chunk of readable) {
    // 這裡會自動處理 Backpressure，如果處理慢，讀取也會暫停
    await processChunk(chunk); 
  }
}
```

### 3. Generators as Transform Streams
不需要總是繼承 `Transform` 類別來寫轉換邏輯。你可以使用 Async Generators 搭配 `pipeline`，這是最現代且簡潔的寫法。

```javascript
const { pipeline } = require('stream/promises');
const fs = require('fs');

// 這就是一個 Transform Stream
async function* upperCaseMapper(source) {
  for await (const chunk of source) {
    yield chunk.toString().toUpperCase();
  }
}

await pipeline(
  fs.createReadStream('input.txt'),
  upperCaseMapper,
  fs.createWriteStream('output.txt')
);
```

### 4. Buffer Allocation Strategy
- **`Buffer.alloc(size)`**: 初始化並填滿 0。**安全**，但稍微慢一點。
- **`Buffer.allocUnsafe(size)`**: 分配記憶體但不清除舊資料。**快**，但可能包含敏感的舊數據（如密碼殘留）。
- **實務建議**: 除非你在做極致效能優化且完全掌控資料寫入覆蓋，否則一律使用 `Buffer.alloc` 或 `Buffer.from`。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Load Everything" Trap (讀取全量檔案)
最常見的新手錯誤是使用 `fs.readFile` 讀取可能很大的檔案（如 Log 檔、CSV 匯出檔）。
- **後果**: 當並發請求增加或檔案變大時，Server RAM 瞬間被吃光，導致 OOM Crash。
- **修正**: 只要檔案大小不固定，一律優先考慮 `createReadStream`。

### 2. Ignoring `write()` return value (忽略寫入回傳值)
當你手動呼叫 `writable.write(chunk)` 時，如果它回傳 `false`，代表內部 Buffer 已滿。
- **反模式**: 無視 `false` 繼續狂寫。
- **後果**: 記憶體暴增，Backpressure 機制失效。
- **修正**: 應等待 `drain` 事件觸發後再繼續寫入。

### 3. Mixing Streams and Async/Await improperly
在 `.on('data', async (chunk) => { ... })` callback 中使用 `await` 是無效的，因為 Event Emitter 不會等待你的 Promise 完成就發送下一個 chunk。
- **後果**: 你以為你在依序處理，實際上你瞬間啟動了成千上萬個 Promise，導致系統過載。
- **修正**: 使用 Async Iterator (`for await...of`) 或 `Transform` stream 來確保處理順序與 Backpressure。

### 4. JSON Parsing Large Files
試圖將一個巨大的 JSON 檔讀入並 `JSON.parse()`。
- **後果**: V8 引擎對字串長度與物件大小有限制，且解析極慢。
- **修正**: 使用 Streaming JSON Parser（如 `bfj` 或 `stream-json`），逐個物件解析與處理。

---

## Checklists & workflows｜檢查清單與流程

在處理 I/O 密集任務或檔案上傳/下載功能時，請執行以下檢查：

### Decision Tree: Stream vs. Buffer
- [ ] **資料大小是否大於 10MB？** (是 -> Stream)
- [ ] **並發請求量是否很高？** (是 -> Stream 以降低 RAM footprint)
- [ ] **是否需要讀取完整內容才能處理？** (例如驗證圖片完整雜湊值 -> Stream 搭配 Hash 計算；若是解析複雜結構 -> 考慮 Buffer 但需限制大小)

### Implementation Checklist
- [ ] **Pipeline 安全性**: 是否使用了 `stream.pipeline` 而非 `.pipe` 來確保錯誤處理？
- [ ] **Backpressure**: 如果是手動寫入，是否檢查了 `.write()` 的回傳值並處理 `drain` 事件？
- [ ] **Chunk Size**: 是否設定了合理的 `highWaterMark`？(預設 16KB/64KB 通常足夠，但在高吞吐網路傳輸下可適度調大)。
- [ ] **Encoding**: 處理文字資料時，是否明確指定了 `utf8`，還是錯誤地在操作 Binary Buffer？
- [ ] **Cleanup**: 確保在 Request 結束或斷線時，相關的 File Descriptor 或 Socket 有被銷毀。

---

## Real-world examples｜實戰案例

### Scenario 1: High-Performance HTTP File Server (高效檔案下載)
不要將檔案讀入記憶體再回傳，而是直接對接 Stream。

```javascript
const http = require('http');
const fs = require('fs');
const { pipeline } = require('stream');

http.createServer((req, res) => {
  const fileStream = fs.createReadStream('big-video.mp4');
  
  // 設定 Headers
  res.writeHead(200, { 'Content-Type': 'video/mp4' });

  // 實戰模式：使用 pipeline 串接
  // 這樣做的好處：
  // 1. 記憶體佔用極低 (只佔用 chunk size)
  // 2. 客戶端下載慢時，Server 讀取檔案也會自動變慢 (Backpressure)
  // 3. 錯誤會被最後一個 callback 捕獲
  pipeline(
    fileStream,
    res,
    (err) => {
      if (err) {
        console.error('Stream error:', err);
        // 只有在 header 尚未發送時才能回傳 500，否則只能斷開連線
        if (!res.headersSent) res.statusCode = 500; 
        res.end(); 
      }
    }
  );
}).listen(3000);
```

### Scenario 2: ETL Process (CSV to Database)
讀取巨大的 CSV，轉換資料格式，批次寫入資料庫。

```javascript
const fs = require('fs');
const { pipeline } = require('stream/promises');
const csvParse = require('csv-parser'); // 假設使用第三方 streaming parser

// 1. Source: 讀取大檔案
const source = fs.createReadStream('users_dump.csv');

// 2. Transform: Async Generator 處理商業邏輯
async function* transformAndBatch(sourceStream) {
  let batch = [];
  for await (const row of sourceStream) {
    // 簡單的資料清洗
    const cleanUser = {
      name: row.Name.trim(),
      email: row.Email.toLowerCase(),
      isActive: row.Status === 'Active'
    };
    
    batch.push(cleanUser);
    
    // 累積 1000 筆再一次送出 (Batch Processing)
    if (batch.length >= 1000) {
      yield batch;
      batch = [];
    }
  }
  if (batch.length > 0) yield batch;
}

// 3. Sink: 寫入資料庫 (模擬 Writable)
const dbWriter = new Writable({
  objectMode: true,
  async write(batch, encoding, callback) {
    try {
      await db.users.insertMany(batch);
      callback();
    } catch (err) {
      callback(err);
    }
  }
});

// 執行 Pipeline
await pipeline(
  source.pipe(csvParse()), // 先轉成 Object stream
  transformAndBatch,       // 再進行清洗與分批
  dbWriter                 // 最後寫入 DB
);
```