# 映像檔建置最佳實踐：多階段構建與快取 / Image Building Best Practices: Multi-stage Builds & Caching

## Mental model｜心智模型

要掌握 Docker 映像檔優化，必須建立兩個核心的心智模型：**「千層蛋糕效應 (The Layer Cake Effect)」** 與 **「建築工地與樣品屋 (Construction Site vs. Showroom)」**。

### 1. 千層蛋糕效應 (The Layer Cake Effect)
Docker 映像檔是由唯讀層（Read-only Layers）堆疊而成的。
- **不可變性 (Immutability)**：一旦某一層被建立，它就是唯讀的。
- **累加性 (Additivity)**：如果你在 Layer 1 下載了一個 100MB 的檔案，並在 Layer 2 刪除它，最終的映像檔大小**不會減少**。因為 Layer 1 依然存在於歷史中，Layer 2 只是標記該檔案為「不可見」。
- **快取失效 (Cache Invalidation)**：Docker 構建時會由上而下檢查。一旦某一層發生變化（例如程式碼修改），該層**及其之後的所有層**都會被迫重新構建。

### 2. 建築工地與樣品屋 (Construction Site vs. Showroom)
這是 **Multi-stage Builds** 的核心概念。
- **建築工地 (Build Stage)**：這裡充滿了鷹架、水泥攪拌機、藍圖（編譯器、Header files、原始碼、建置工具）。這些東西對於「蓋房子」是必須的，但對於「住進去」是多餘的。
- **樣品屋 (Runtime Stage)**：這是最終交付給用戶的產品。它應該只包含傢俱和裝潢（編譯好的 Binary、必要的 Config、最小化的 Runtime 環境）。
- **目標**：不要把起重機（GCC/Maven/Node-gyp）留在客廳裡。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 依賴優先策略 (Dependency First Pattern)
為了最大化 Layer Caching 的效益，永遠將「變動頻率低」的步驟放在前面，「變動頻率高」的步驟放在後面。

- **Bad**: 先複製所有程式碼，再安裝依賴。
- **Good**: 先複製依賴描述檔（`package.json`, `go.mod`, `pom.xml`），安裝依賴，最後才複製原始碼。

```dockerfile
# Pattern: Cache Dependencies
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile  # 這一層會被 Cache 住，除非依賴有變動
COPY . .                            # 原始碼變動只會影響這一層之後
RUN yarn build
```

### 2. 多階段構建 (Multi-stage Builds)
將建置環境與執行環境分離，大幅縮減映像檔體積並提升安全性（減少攻擊面）。

```dockerfile
# Stage 1: Builder
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runner
FROM node:18-alpine
WORKDIR /app
# 只從 Builder 階段複製必要的產出物
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/main.js"]
```

### 3. 選擇正確的 Base Image (Distroless / Alpine / Slim)
- **`alpine`**：極小（~5MB），但使用 musl libc，可能導致某些 C 依賴庫的兼容性問題（DNS 解析、效能差異）。適合 Go, Node.js 等。
- **`debian-slim`**：比標準版小，相容性比 Alpine 好（glibc）。適合 Python, Java。
- **`distroless`**：Google 推出的極簡映像檔，不包含 Shell，安全性最高，但除錯較困難。適合對安全要求極高的生產環境。

### 4. 最小化層數與清理 (Minimize Layers & Cleanup)
雖然現代 Docker 引擎對層數限制較寬鬆，但為了減少體積，相關的操作應合併在同一個 `RUN` 指令中，並在同一層內清理快取。

```dockerfile
# Good Pattern: Install & Clean in one layer
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*  # 關鍵：在同一層刪除 apt cache
```

### 5. 使用 `.dockerignore`
這不是選用功能，是必須功能。避免將 `.git` 目錄、本地的 `node_modules`、敏感文件或暫存檔發送到 Docker Daemon，這能顯著加快 Build Context 的傳輸速度並避免快取意外失效。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Late Clean" Trap (延遲清理陷阱)
在 Layer A 下載檔案，在 Layer B 刪除它。
- **後果**：映像檔體積沒有變小，且下載的檔案仍可透過檢視 Image History 找回（潛在資安風險）。
- **修正**：必須在同一個 `RUN` 指令中完成 `下載 -> 使用 -> 刪除`。

### 2. The "Volatile Top" (頂層易變)
將 `COPY . .` 放在 Dockerfile 的最前面。
- **後果**：只要你改了一個字元的程式碼，後續所有的 `apt-get install` 或 `npm install` 都會重新執行，浪費大量時間與頻寬。

### 3. Secrets in Build Args (構建參數洩漏)
使用 `ARG` 或 `ENV` 傳遞私鑰或 API Key。
- **後果**：`docker history` 可以直接看到這些值。
- **修正**：使用 Docker BuildKit 的 `--secret` 功能，或是在 Runtime 時才掛載 Secrets。

### 4. Running as Root (預設 Root 權限)
沒有指定 `USER` 指令。
- **後果**：容器內的 Process 預設以 Root 執行，若容器被逃逸（Container Breakout），攻擊者將獲得宿主機的高權限。
- **修正**：建立並切換到非特權使用者（如 `USER node` 或 `USER appuser`）。

---

## Checklists & workflows｜檢查清單與流程

在提交 Dockerfile 或設定 CI Pipeline 前，請執行以下檢查：

### 🚀 Optimization Checklist
- [ ] **Context Check**: 是否已設定 `.dockerignore` 排除 `.git`, `node_modules`, `tmp`, secrets？
- [ ] **Cache Order**: 是否已將依賴安裝（Dependency Install）放在原始碼複製（Source Copy）之前？
- [ ] **Base Image**: 是否使用了具體的版本標籤（如 `node:18.16.0-alpine`）而非 `latest`？
- [ ] **Multi-stage**: 生產環境映像檔是否排除了編譯工具（GCC, Maven, TS compiler）？
- [ ] **Layer Cleanup**: 套件管理器（apt, apk, yum）的快取是否在同一層被清理了？

### 🛡️ Security & Stability Checklist
- [ ] **User**: 是否切換到了非 Root 使用者 (`USER <name>`)？
- [ ] **Secrets**: 確認沒有將密碼或 Key 寫死在 `ENV` 或 `Dockerfile` 中。
- [ ] **Reproducibility**: 安裝套件時是否盡量鎖定版本（Pin versions）？

---

## Real-world examples｜實戰案例

### 案例：優化 Golang Web Service

#### ❌ Before: The Bloated Monolith (臃腫的單體)
```dockerfile
FROM golang:1.21
# 錯誤：將所有檔案一次複製，破壞快取機制
COPY . /app 
WORKDIR /app
# 錯誤：沒有清理，且映像檔包含完整的 Go Toolchain (數百 MB)
RUN go build -o myapp main.go
CMD ["/app/myapp"]
```
- **結果**：Image 大小約 800MB+，每次改 code 都要重新下載依賴。

#### ✅ After: Lean & Fast (精實且快速)
```dockerfile
# Stage 1: Builder
FROM golang:1.21-alpine AS builder
WORKDIR /app

# 最佳實踐：先複製依賴描述檔
COPY go.mod go.sum ./
# 最佳實踐：下載依賴 (這一層會被 Cache)
RUN go mod download

# 接著才複製原始碼
COPY . .
# 編譯靜態連結的 Binary (Scratch image 需要)
RUN CGO_ENABLED=0 GOOS=linux go build -o myapp main.go

# Stage 2: Runtime
# 最佳實踐：使用 Scratch (空映像檔) 或 Distroless
FROM scratch

# 複製 CA Certificates (否則無法發送 HTTPS 請求)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# 只複製 Binary
COPY --from=builder /app/myapp /myapp

# 最佳實踐：以非 Root 執行 (Scratch 預設無使用者，但概念上應避免依賴 Root)
# 註：在 Scratch 中通常直接執行 Binary，若需 User 隔離需額外處理 /etc/passwd

CMD ["/myapp"]
```
- **結果**：Image 大小約 10-20MB，依賴層被快取，構建速度極快，且不含任何 OS 工具，極難被滲透。