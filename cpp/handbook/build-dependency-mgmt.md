# 建置系統與相依性管理：CMake 與套件管理實務 / Build Systems & Dependency Management: CMake & Package Managers

## Mental model｜心智模型

在現代 C++ 開發中，建置系統（Build System）不只是「編譯器指令的集合」，而是一個 **依賴關係圖（Dependency Graph）的描述語言**。

### 1. Target-Centric View (以目標為中心)
拋棄舊式 CMake 的「目錄思維」或「變數思維」。將每一個 Library 或 Executable 視為一個 **物件（Object）**，即 CMake 中的 **Target**。
- **Properties**: 每個 Target 都有自己的屬性（原始碼、Include路徑、編譯選項）。
- **Inheritance**: 當 Target A 依賴 Target B 時，A 會自動繼承 B 的公開屬性（Usage Requirements）。

### 2. The "Usage Requirement" Propagation (使用需求的傳遞)
想像你在組裝積木：
- **PRIVATE**: 我自己需要這個螺絲，但接在我上面的積木不需要知道。
- **INTERFACE**: 我自己不需要，但接在我上面的積木需要這個螺絲。
- **PUBLIC**: 我自己需要，接在我上面的積木也需要。

### 3. Package Manager as the Supply Chain (套件管理器即供應鏈)
不要再手動下載 `.zip` 或將第三方套件原始碼塞進你的 repo。套件管理器（如 Vcpkg, Conan）負責「採購」與「預處理」依賴，CMake 則負責「組裝」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Modern CMake: Always use Targets
永遠使用 `target_*` 系列指令，拒絕全域污染。

```cmake
# ✅ Good: Target-based
add_library(my_lib src/my_lib.cpp)
target_include_directories(my_lib PUBLIC include)
target_compile_features(my_lib PRIVATE cxx_std_20)

# ❌ Bad: Global state pollution
include_directories(include)
set(CMAKE_CXX_STANDARD 20)
```

### 2. Dependency Management with Vcpkg (Manifest Mode)
推薦使用 Vcpkg 的 **Manifest Mode** (`vcpkg.json`)，這讓依賴管理跟 `package.json` (npm) 或 `Cargo.toml` (Rust) 一樣直觀。

- **vcpkg.json**:
  ```json
  {
    "name": "my-project",
    "version": "1.0.0",
    "dependencies": [ "fmt", "nlohmann-json" ]
  }
  ```
- **CMakeLists.txt**:
  ```cmake
  find_package(fmt CONFIG REQUIRED)
  target_link_libraries(main PRIVATE fmt::fmt)
  ```

### 3. Visibility Keywords Strategy (可見性策略)
精確控制傳遞性（Transitivity）是大型專案編譯速度與架構乾淨的關鍵。

- **PRIVATE**: 實作細節（.cpp 內用到的 header/lib）。修改它不會導致下游重新編譯。
- **PUBLIC**: 公開介面（public .h 內用到的 header/lib）。
- **INTERFACE**: Header-only libraries 常見用法。

### 4. CMakePresets.json
使用 `CMakePresets.json` 來統一開發團隊與 CI 的建置參數。這解決了 "It works on my machine" 但 CI 失敗的問題，因為每個人都使用相同的 configure/build preset。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The `file(GLOB ...)` Trap
**不要使用 GLOB 來抓取原始碼檔案**。
- **Why?** 如果你新增一個檔案，CMake 不會自動偵測到需要重新執行 configure，導致建置錯誤。
- **Fix:** 明確列出所有原始碼檔案，雖然繁瑣，但保證正確性。

### 2. Hardcoded Paths (寫死路徑)
**絕對不要寫死路徑**，例如 `include_directories(/usr/local/include)`。
- **Consequence:** 破壞跨平台能力，且無法配合 Vcpkg/Conan 的虛擬環境。
- **Fix:** 使用 `find_package()` 與 `find_library()`。

### 3. In-Source Builds (原始碼內建置)
**不要在原始碼目錄中直接執行 `cmake .`**。
- **Consequence:** 產生的暫存檔會污染 git repo，且難以清理（沒有 `make distclean`）。
- **Fix:** 始終使用 Out-of-source build (`mkdir build && cd build && cmake ..`)。

### 4. Abusing Variables over Targets
過度依賴 `${SOME_LIB_INCLUDE_DIRS}` 變數，而不是直接 Link Target。
- **Anti-pattern:**
  ```cmake
  target_include_directories(app PRIVATE ${FOO_INCLUDE_DIRS})
  target_link_libraries(app PRIVATE ${FOO_LIBRARIES})
  ```
- **Best Practice:**
  ```cmake
  target_link_libraries(app PRIVATE Foo::Foo) # Includes and libs handled automatically
  ```

---

## Checklists & workflows｜檢查清單與流程

### Project Setup Checklist (專案設定檢核)
- [ ] **Minimum Version**: `cmake_minimum_required(VERSION 3.20)` 或更高（為了更好的 Preset 與 Toolchain 支援）。
- [ ] **Project Structure**: 遵循標準佈局：
    - `src/` (Private sources)
    - `include/` (Public headers)
    - `tests/` (Unit tests)
    - `vcpkg.json` / `conanfile.txt`
- [ ] **Compiler Warnings**: 是否已啟用高層級警告（`-Wall -Wextra -Wpedantic` / `/W4`）並視為錯誤（Werror）？
- [ ] **Testing**: 是否包含 `enable_testing()` 並整合了 GoogleTest 或 Catch2？

### Dependency Integration Workflow (依賴整合流程)
1. **Search**: 在 Vcpkg/Conan hub 搜尋套件名稱。
2. **Declare**: 將套件加入 `vcpkg.json` 或 `conanfile.txt`。
3. **Find**: 在 `CMakeLists.txt` 中加入 `find_package(PackageName CONFIG REQUIRED)`。
4. **Link**: 使用 `target_link_libraries(MyTarget PRIVATE Package::Target)`。
5. **Verify**: 檢查是否能正確 include header 並編譯。

---

## Real-world examples｜實戰案例

### Scenario: A Modern Application with JSON and Logging
這是一個標準的應用程式結構，展示如何整合 Vcpkg 與 Modern CMake。

#### File Structure
```text
my_app/
├── CMakeLists.txt
├── CMakePresets.json
├── vcpkg.json
├── src/
│   └── main.cpp
└── include/
    └── my_app/
        └── utils.hpp
```

#### vcpkg.json
```json
{
  "name": "my-app",
  "version-string": "0.1.0",
  "dependencies": [
    "fmt",
    "nlohmann-json"
  ]
}
```

#### CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.25)

# 初始化專案
project(my_app LANGUAGES CXX)

# 設定 C++ 標準
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 尋找依賴 (由 Vcpkg Toolchain 提供路徑)
find_package(fmt CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

# 定義 Executable Target
add_executable(my_app_exe src/main.cpp)

# 設定 Include Path (將 include/ 目錄設為公開介面)
target_include_directories(my_app_exe PUBLIC include)

# 連結依賴 (fmt 與 json 只在內部實作使用，故為 PRIVATE)
target_link_libraries(my_app_exe PRIVATE 
    fmt::fmt 
    nlohmann_json::nlohmann_json
)

# 編譯選項 (GCC/Clang/MSVC 兼容寫法)
if(MSVC)
    target_compile_options(my_app_exe PRIVATE /W4 /WX)
else()
    target_compile_options(my_app_exe PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
```

#### src/main.cpp
```cpp
#include <fmt/core.h>
#include <nlohmann/json.hpp>

int main() {
    nlohmann::json j;
    j["message"] = "Hello from Modern CMake!";
    
    // 使用 fmt 函式庫列印
    fmt::print("{}\n", j.dump(4));
    return 0;
}
```

### Build Command (Using Presets)
假設你已經設定好 `CMakePresets.json`，開發者的日常指令將簡化為：

```bash
# Configure (自動下載 vcpkg 依賴)
cmake --preset default

# Build
cmake --build --preset default
```