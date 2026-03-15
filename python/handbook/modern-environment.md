# 現代化環境建置與依賴管理 / Modern Environment & Dependency Management

## Mental model｜心智模型

在現代 Python 開發中，我們不再將環境視為「安裝了什麼套件的資料夾」，而是將其視為一個 **「可重現的狀態快照 (Reproducible State Snapshot)」**。

### 1. 宣告式 vs. 指令式 (Declarative vs. Imperative)
- **Old Mental Model (Imperative):** 我需要 NumPy，所以我執行 `pip install numpy`。環境的狀態是由我執行指令的順序決定的。
- **New Mental Model (Declarative):** 我在 `pyproject.toml` 中宣告「此專案依賴 NumPy」。工具（如 Poetry/uv）負責計算出符合條件的狀態，並透過 Lock file 凍結這個狀態。

### 2. 依賴層級 (The Dependency Hierarchy)
想像依賴管理是一個同心圓：
- **核心 (Abstract):** `pyproject.toml`。定義「我想要什麼」（例如 `pandas >= 2.0`）。
- **凍結 (Concrete):** `*.lock`。定義「實際安裝了什麼」（例如 `pandas==2.0.3` 以及它依賴的 `numpy==1.24.3`）。這是確保原本重現的關鍵。
- **隔離 (Isolation):** Virtual Environment (`.venv`)。這是上述定義的具體實例化，避免與系統 Python 或其他專案衝突。
- **封裝 (Containerization):** Docker。將 OS 層級的依賴（如 C libraries）也一併凍結，實現終極的一致性。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 擁抱 `pyproject.toml` 標準
`pyproject.toml` 是 Python 的單一信賴來源 (Single Source of Truth)。無論你開發的是 Library 還是 Application，都應以此檔案管理 metadata 與依賴，而非散落在 `setup.py` 或多個 `requirements.txt` 中。

### 2. 使用現代化管理工具 (Poetry vs. uv)
- **Poetry:** 成熟穩定，生態系完整。適合大多數標準專案。
- **uv (by Astral):** 極速（Rust 編寫），相容 `pip` 與 `pip-tools` 工作流，並支援 `pyproject.toml`。適合追求 CI/CD 速度與單一二進制檔便利性的團隊。
- **Pattern:** 在 CI/CD 中，永遠使用 `install --sync` 或 `install --frozen` 模式，確保安裝內容嚴格等於 Lock file。

### 3. 依賴分組 (Dependency Groups)
不要將測試工具帶入生產環境。利用分組功能區隔依賴：
- `main`: 生產環境必備 (e.g., FastAPI, SQLAlchemy)。
- `dev`: 開發工具 (e.g., Black, Ruff, MyPy)。
- `test`: 測試框架 (e.g., Pytest, Factory Boy)。

### 4. Docker 多階段建置 (Multi-stage Builds)
為了縮減 Image 大小並提高安全性，採用 "Builder" 與 "Runner" 分離模式。
- **Builder Stage:** 安裝編譯工具 (gcc, build-essential)，安裝 Python 套件到虛擬環境或特定路徑。
- **Runner Stage:** 僅複製編譯好的 Python 套件與程式碼，基於 `python:slim` 或 `distroless` 映像檔執行。

### 5. 鎖定檔案必須進版控 (Commit the Lock File)
**這是鐵律。** `poetry.lock` 或 `uv.lock` 必須 commit 到 git。沒有 Lock file，你的 CI/CD 每次跑都可能安裝到不同版本的子依賴 (Transitive Dependencies)，導致 "Works on my machine, breaks on prod"。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `pip freeze` Trap
- **Bad:** 使用 `pip freeze > requirements.txt`。這會將所有「頂層依賴」與「子依賴」混在一起，無法分辨哪些是你真正需要的，且升級困難。
- **Good:** 使用 `pyproject.toml` 紀錄頂層依賴，讓工具生成 Lock file 處理子依賴。

### 2. System Python Pollution
- **Bad:** 直接使用 `sudo pip install` 或在全域環境安裝專案依賴。這可能破壞 OS 的工具（如 `yum` 或 `apt` 的 Python 元件）。
- **Good:** 永遠在 Virtual Environment 或 Docker 內操作。

### 3. The "Latest" Gambling
- **Bad:** 在 `requirements.txt` 中寫 `pandas` (不指定版本) 或 `pandas==latest`。
- **Consequence:** 某天早上你的專案會因為套件發布了 Breaking Change 而突然掛掉。
- **Good:** 使用語意化版本控制 (Semantic Versioning)，如 `^2.0.0` (Poetry) 或 `~=2.0`。

### 4. Copying venv across OS
- **Bad:** 在 macOS 開發，將 `.venv` 資料夾直接 COPY 到 Linux Docker image 中。
- **Consequence:** Binary 檔案（如 compiled C extensions）不相容，程式無法執行。
- **Good:** 在 Docker build 過程中重新安裝依賴 (`RUN poetry install ...`)。

---

## Checklists & workflows｜檢查清單與流程

### Project Initialization Checklist
- [ ] **Tool Selection:** 決定使用 Poetry, uv, 或 PDM。
- [ ] **Python Version:** 在 `pyproject.toml` 明確指定 Python 版本限制 (e.g., `requires-python = ">=3.10"`).
- [ ] **Git Ignore:** 確保 `.venv`, `__pycache__`, `.pytest_cache` 已加入 `.gitignore`。
- [ ] **Lock File:** 初始化後立即生成 Lock file 並 commit。

### Dependency Update Workflow
1. **Check:** 執行 `poetry show --outdated` 或 `uv pip list --outdated` 查看可更新套件。
2. **Update:** 執行 `poetry update <package_name>` 更新特定套件（避免一次更新全部導致除錯困難）。
3. **Test:** 執行完整測試套件 (`pytest`)。
4. **Commit:** 同時 commit `pyproject.toml` (若有變更) 與 `*.lock` 檔案。

### Docker Optimization Checklist
- [ ] **Base Image:** 使用明確版本 tag (e.g., `python:3.11-slim-bookworm`) 而非 `python:3.11` 或 `latest`。
- [ ] **Caching:** 將 `COPY pyproject.toml ...` 與 `RUN install dependencies` 放在 `COPY . .` (程式碼) 之前，以利用 Docker Layer Caching。
- [ ] **User:** 建立非 root 使用者執行應用程式 (`USER appuser`)。
- [ ] **Cleanup:** 確保最終 Image 不包含 poetry/uv 本身（僅需安裝好的套件）或編譯快照。

---

## Real-world examples｜實戰案例

### 1. Modern `pyproject.toml` Structure (Poetry Example)
這是一個典型的 Web Service 設定，區分了生產與開發依賴。

```toml
[tool.poetry]
name = "my-awesome-service"
version = "0.1.0"
description = "A production-ready service"
authors = ["Engineering Team <dev@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
pydantic = "^2.6.0"
# 生產環境不需要測試庫

[tool.poetry.group.dev.dependencies]
ruff = "^0.2.0"
mypy = "^1.8.0"
pytest = "^8.0.0"
pytest-cov = "^4.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 2. High-Performance Dockerfile with `uv`
使用 `uv` 進行極速構建，並採用 Multi-stage build 確保 Image 輕量化。

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim-bookworm as builder

# 安裝 uv (比 pip 快 10-100 倍)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 設定環境變數
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 1. 先複製依賴定義檔 (利用 Docker Cache)
COPY pyproject.toml uv.lock ./

# 2. 安裝依賴到系統 site-packages (因為是在隔離的 builder stage)
# --no-dev: 不安裝開發依賴
# --frozen: 嚴格依照 lock file
RUN uv pip install --system --no-dev --frozen -r pyproject.toml

# Stage 2: Runner
FROM python:3.11-slim-bookworm as runner

WORKDIR /app

# 建立非 root 使用者
RUN useradd -m appuser && chown appuser /app
USER appuser

# 從 Builder 複製安裝好的套件
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 複製應用程式碼
COPY . .

# 啟動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Decision Tree: Which tool to use?
當你開始一個新專案時，如何選擇工具？

```text
Start
|
+--- Is it a simple script or data analysis notebook?
|    |
|    +-> YES: Use `uv` (script support) or standard `venv` + `pip`.
|
+--- Is it a Python Library (to be published on PyPI)?
|    |
|    +-> YES: Use `Hatch` or `Flit` (Standard compliant, less opinionated).
|
+--- Is it an Application / Web Service (Django, FastAPI)?
     |
     +-> YES: Use `Poetry` (Rich ecosystem) or `uv` (Speed).
         |
         +-> Need extreme CI speed? -> `uv`
         +-> Need strict dependency resolution & plugins? -> `Poetry`
```