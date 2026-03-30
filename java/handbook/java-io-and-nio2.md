# 現代 Java I/O 與 NIO.2 / Modern Java I/O and NIO.2

## Mental model｜心智模型

在現代 Java 開發中，處理 I/O 的心智模型已經從「位元組流（Byte Streams）」演進到「區塊與通道（Blocks and Channels）」，以及「路徑驅動的檔案系統（Path-driven File Systems）」。
In modern Java development, the mental model for handling I/O has evolved from "Byte Streams" to "Blocks and Channels," and "Path-driven File Systems."

1. **`java.io` (Blocking I/O) = 水管模型 / The Water Pipe Model**
   傳統 I/O 就像水管，資料像水流一樣依序流動（Streams）。當沒有水時，接水的人必須原地等待（Blocking）。適用於簡單、低併發的循序讀寫。
   Traditional I/O is like a water pipe where data flows sequentially (Streams). If there's no water, the receiver must wait (Blocking). It is suitable for simple, low-concurrency sequential read/writes.

2. **`java.nio` (Non-blocking I/O) = 貨櫃模型 / The Container Model**
   NIO 引入了 `Buffer`（貨櫃）與 `Channel`（鐵路）。資料被打包成區塊批次運送。配合 `Selector`，一個站長（Thread）可以同時監控多條鐵路（Multiplexing），實現非阻塞 I/O。適用於高併發網路通訊（如 Netty 底層）。
   NIO introduces `Buffer` (containers) and `Channel` (railways). Data is packed and transported in blocks. With a `Selector`, a single station master (Thread) can monitor multiple railways simultaneously (Multiplexing), achieving non-blocking I/O. Suitable for high-concurrency networking (e.g., Netty's foundation).

3. **`java.nio.file` (NIO.2) = 現代檔案系統 API / Modern File System API**
   NIO.2 徹底取代了老舊的 `java.io.File`。它將「路徑（`Path`）」與「操作（`Files`）」解耦，並提供了對符號連結（Symlinks）、檔案屬性（Metadata）與目錄走訪（Directory Walking）的原生支援。
   NIO.2 completely replaces the legacy `java.io.File`. It decouples the "Path" (`Path`) from "Operations" (`Files`), providing native support for Symlinks, Metadata, and Directory Walking.

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 永遠使用 `Path` 與 `Files` 取代 `File` / Always use `Path` and `Files` over `File`
在現代 Java 中，`java.io.File` 應被視為遺留 API。使用 `Paths.get()` 或 `Path.of()`（Java 11+），並透過 `Files` 類別進行操作。
In modern Java, `java.io.File` should be considered a legacy API. Use `Paths.get()` or `Path.of()` (Java 11+), and perform operations via the `Files` utility class.

```java
// Modern approach (Java 11+)
Path configPath = Path.of("/app/config", "settings.json");
boolean exists = Files.exists(configPath);
```

### 2. 針對小檔案使用便捷方法 / Use Convenience Methods for Small Files
對於 MB 級別以下的小檔案，直接使用 `Files.readString()` 與 `Files.writeString()`，程式碼最簡潔。
For small files (under a few MBs), use `Files.readString()` and `Files.writeString()` directly for the cleanest code.

```java
// 讀取與寫入小檔案 / Reading and writing small files
String content = Files.readString(path, StandardCharsets.UTF_8);
Files.writeString(path, newContent, StandardCharsets.UTF_8, StandardOpenOption.CREATE);
```

### 3. 使用 `FileChannel` 與記憶體映射檔案處理超大檔案 / Use `FileChannel` and Memory-Mapped Files for Huge Files
當需要頻繁隨機存取 GB 級別的大檔案時，使用 `MappedByteBuffer` 將檔案直接映射到 OS 的虛擬記憶體中，可大幅降低 JVM 記憶體消耗並提升效能。
When frequent random access to GB-sized files is required, use `MappedByteBuffer` to map the file directly into the OS's virtual memory. This drastically reduces JVM memory consumption and boosts performance.

### 4. 嚴格遵守 Try-With-Resources / Strictly Adhere to Try-With-Resources
任何實作了 `AutoCloseable` 的 I/O 資源（包含 `Stream`, `Channel`, 甚至 `Files.lines()` 回傳的 Stream）都必須放在 try-with-resources 區塊中。
Any I/O resource implementing `AutoCloseable` (including `Stream`, `Channel`, and even the Stream returned by `Files.lines()`) must be placed inside a try-with-resources block.

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### ❌ 踩雷點 1：將大檔案一次性讀入記憶體 / Pitfall 1: Reading Large Files into Memory All at Once
**反模式 (Anti-pattern):** 使用 `Files.readAllLines(path)` 或 `Files.readAllBytes(path)` 讀取數百 MB 或 GB 級別的日誌檔。
**Consequence:** 直接導致 `java.lang.OutOfMemoryError` (OOM) 或觸發頻繁的 Full GC。
**解決方案 (Solution):** 使用 `Files.lines()` 配合 Stream API 進行惰性處理（Lazy Evaluation）。

### ❌ 踩雷點 2：忘記關閉 `Files.lines()` 或 `Files.walk()` / Pitfall 2: Forgetting to Close `Files.lines()` or `Files.walk()`
**反模式 (Anti-pattern):** 以為 Stream 會自動回收，直接寫 `Files.lines(path).filter(...).findFirst();`。
**Consequence:** 這些方法底層持有作業系統的檔案描述符（File Descriptors）。如果不關閉，會導致 `Too many open files` 異常。
**解決方案 (Solution):** 必須使用 try-with-resources。

```java
// ❌ Bad
Files.lines(path).forEach(System.out::println); // Leaks file descriptor!

// ✅ Good
try (Stream<String> lines = Files.lines(path)) {
    lines.forEach(System.out::println);
}
```

### ❌ 踩雷點 3：依賴平台預設字元集 / Pitfall 3: Relying on Platform Default Charset
**反模式 (Anti-pattern):** 使用 `new FileReader(file)` 或 `String.getBytes()` 而不指定編碼。
**Consequence:** 在 Windows 開發測試正常，部署到 Linux 容器後出現中文亂碼。
**解決方案 (Solution):** 永遠明確指定 `StandardCharsets.UTF_8`。（註：Java 18 起預設字元集已改為 UTF-8，但為了向下相容與明確性，仍建議指定）。

---

## Checklists & workflows｜檢查清單與流程

### 💡 檔案讀取決策樹 / File Reading Decision Tree
- 檔案很小（< 10MB）？ / File is small (< 10MB)?
  👉 使用 `Files.readString()` 或 `Files.readAllLines()`。
- 檔案很大，需要逐行處理？ / File is large, need line-by-line processing?
  👉 使用 `try (Stream<String> lines = Files.lines(path))`。
- 檔案很大，需要二進位串流處理？ / File is large, need binary stream processing?
  👉 使用 `try (InputStream is = Files.newInputStream(path))`。
- 需要極致效能的隨機讀寫？ / Need extreme performance random read/write?
  👉 使用 `FileChannel.open()` 與 `MappedByteBuffer`。

### ✅ I/O Code Review Checklist
- [ ] **API 現代化 (Modern API):** 是否已將 `java.io.File` 替換為 `java.nio.file.Path`？
- [ ] **資源釋放 (Resource Release):** 所有 `InputStream`, `OutputStream`, `Reader`, `Writer`, `Channel` 以及 NIO.2 回傳的 `Stream` 是否都在 `try-with-resources` 中？
- [ ] **編碼安全 (Encoding Safety):** 所有字串與位元組轉換是否都明確指定了 `StandardCharsets.UTF_8`？
- [ ] **記憶體安全 (Memory Safety):** 是否確認過目標檔案的大小？避免對未知大小的檔案使用 `readAllBytes` 或 `readAllLines`。
- [ ] **原子性操作 (Atomicity):** 寫入重要檔案時，是否使用了先寫入暫存檔，再使用 `StandardCopyOption.ATOMIC_MOVE` 覆蓋原檔的模式？

---

## Real-world examples｜實戰案例

### 案例 1：安全且高效地處理巨型日誌檔 / Example 1: Safely and Efficiently Processing Huge Log Files
在真實專案中，我們常需要從數 GB 的日誌中篩選出特定錯誤。
In real projects, we often need to filter specific errors from multi-GB log files.

```java
import java.nio.file.*;
import java.util.stream.Stream;
import java.io.IOException;

public class LogProcessor {
    public void findErrors(Path logPath) {
        // 使用 try-with-resources 確保 File Descriptor 被釋放
        // Use try-with-resources to ensure File Descriptor is released
        try (Stream<String> lines = Files.lines(logPath)) {
            lines.filter(line -> line.contains("ERROR") || line.contains("Exception"))
                 .limit(100) // 找到前 100 筆就停止 (Short-circuiting)
                 .forEach(this::processErrorLine);
        } catch (IOException e) {
            // 處理 I/O 異常 / Handle I/O exception
            throw new UncheckedIOException("Failed to process log file: " + logPath, e);
        }
    }
    
    private void processErrorLine(String line) { /* ... */ }
}
```

### 案例 2：原子性檔案寫入（防崩潰）/ Example 2: Atomic File Writing (Crash-safe)
當更新設定檔時，如果寫入到一半斷電或當機，檔案會損壞。最佳實務是先寫入暫存檔，再進行原子性搬移。
When updating config files, if a crash occurs mid-write, the file gets corrupted. The best practice is to write to a temp file first, then perform an atomic move.

```java
import java.nio.file.*;
import java.io.IOException;

public class ConfigWriter {
    public void updateConfig(Path targetPath, String newConfig) throws IOException {
        Path tempPath = targetPath.resolveSibling(targetPath.getFileName() + ".tmp");
        
        // 1. 寫入暫存檔 / Write to temp file
        Files.writeString(tempPath, newConfig, StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
        
        // 2. 原子性替換目標檔案 / Atomically replace the target file
        // 如果 OS 支援，此操作不會有中間狀態 / If supported by OS, this has no intermediate state
        Files.move(tempPath, targetPath, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
    }
}
```

### 案例 3：使用 WatchService 監控目錄變更 / Example 3: Monitoring Directory Changes with WatchService
實作熱載入（Hot-reload）設定檔的常見模式。
A common pattern for implementing hot-reloading of configuration files.

```java
import java.nio.file.*;

public class ConfigWatcher {
    public void watchDirectory(Path dirToWatch) throws Exception {
        try (WatchService watchService = FileSystems.getDefault().newWatchService()) {
            // 註冊監聽修改事件 / Register for modify events
            dirToWatch.register(watchService, StandardWatchEventKinds.ENTRY_MODIFY);

            while (true) {
                WatchKey key = watchService.take(); // 阻塞等待事件 / Block until event
                for (WatchEvent<?> event : key.pollEvents()) {
                    Path changedFile = (Path) event.context();
                    if (changedFile.toString().endsWith(".json")) {
                        System.out.println("Config changed, reloading: " + changedFile);
                        // 觸發重新載入邏輯 / Trigger reload logic
                    }
                }
                boolean valid = key.reset();
                if (!valid) break; // 目錄變得不可存取 / Directory became inaccessible
            }
        }
    }
}
```