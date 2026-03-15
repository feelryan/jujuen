# Chapter 03: Shared Libraries and Modular Design
# 第 03 章：Shared Libraries 與模組化設計

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

In the previous chapters, we managed individual pipelines. However, as an organization scales to dozens or hundreds of microservices, copying and pasting `Jenkinsfile` content becomes unmaintainable. This chapter focuses on **Jenkins Shared Libraries**, the standard mechanism for abstracting CI/CD logic into reusable, version-controlled code.
在前面的章節中，我們管理了單一的 Pipeline。然而，當組織擴展到數十甚至數百個微服務時，複製貼上 `Jenkinsfile` 的內容將變得難以維護。本章專注於 **Jenkins Shared Libraries**，這是將 CI/CD 邏輯抽象化為可重複使用、受版本控制程式碼的標準機制。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Architect reusable pipelines**: Move complex logic from local `Jenkinsfiles` to a centralized Groovy library.
    **架構可重用的 Pipeline**：將複雜邏輯從本地 `Jenkinsfile` 遷移至集中管理的 Groovy 函式庫。
2.  **Distinguish between `vars` and `src`**: Understand when to use Global Variables (Custom Steps) versus standard Groovy Classes.
    **區分 `vars` 與 `src`**：理解何時使用全域變數（自定義步驟）與標準 Groovy 類別。
3.  **Implement Safe Versioning**: Apply version control strategies to libraries to prevent breaking changes across the organization.
    **實作安全版本控制**：對函式庫應用版本控制策略，以防止對整個組織造成破壞性變更。
4.  **Handle Jenkins Groovy quirks**: Navigate common issues like CPS (Continuation Passing Style) and Serialization errors.
    **處理 Jenkins Groovy 特性**：解決常見問題，如 CPS（Continuation Passing Style）與序列化錯誤。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The "Library" Analogy
### 「函式庫」類比

Think of your `Jenkinsfile` as the `main()` function of an application. Without Shared Libraries, you are writing monolithic scripts for every project. Shared Libraries act like `npm` packages or `Maven` dependencies. They allow you to import functions and classes to keep your `main()` (the `Jenkinsfile`) clean, declarative, and minimal.
將您的 `Jenkinsfile` 視為應用程式的 `main()` 函式。如果沒有 Shared Libraries，您等於是在為每個專案撰寫單體腳本。Shared Libraries 就像 `npm` 套件或 `Maven` 依賴項。它們允許您匯入函式與類別，讓您的 `main()`（即 `Jenkinsfile`）保持整潔、宣告式且極簡。

### Directory Structure: `vars` vs. `src`
### 目錄結構：`vars` vs. `src`

A standard Shared Library repository has a specific structure that dictates how code is loaded.
標準的 Shared Library 儲存庫具有特定的結構，決定了程式碼如何被載入。

```text
(root)
+- src/                     # Standard Groovy Classes (OOP)
|   +- org/
|       +- foo/
|           +- Utility.groovy
+- vars/                    # Global Variables / Custom Steps (Scripted)
|   +- deployApp.groovy
|   +- logInfo.groovy
+- resources/               # Non-Groovy files (JSON, XML, Shell scripts)
```

1.  **`vars/` (Global Variables)**:
    *   Files here become global functions in the pipeline.
    *   `deployApp.groovy` can be called directly as `deployApp()` in a `Jenkinsfile`.
    *   **Best for**: Defining high-level pipeline steps or wrappers (e.g., `standardPipeline`).
    *   **`vars/` (全域變數)**：
        *   此處的檔案會成為 Pipeline 中的全域函式。
        *   `deployApp.groovy` 可以在 `Jenkinsfile` 中直接以 `deployApp()` 呼叫。
        *   **適用於**：定義高階 Pipeline 步驟或包裝器（例如 `standardPipeline`）。

2.  **`src/` (Source Class Path)**:
    *   Standard Java/Groovy directory structure. Added to the classpath.
    *   Requires explicit `import` or full package names.
    *   **Best for**: Helper logic, complex data manipulation, or API clients that don't need direct access to pipeline steps.
    *   **`src/` (原始碼類別路徑)**：
        *   標準的 Java/Groovy 目錄結構。會被加入至 classpath。
        *   需要明確的 `import` 或完整套件名稱。
        *   **適用於**：輔助邏輯、複雜資料操作，或不需要直接存取 Pipeline 步驟的 API 客戶端。

### CPS (Continuation Passing Style)
### CPS (Continuation Passing Style)

Jenkins Pipelines do not run as a continuous script on a single thread. They are transformed into a "Continuation Passing Style" to allow the pipeline to survive Jenkins restarts (persistence).
Jenkins Pipelines 並非在單一執行緒上作為連續腳本執行。它們被轉換為「Continuation Passing Style」，以允許 Pipeline 在 Jenkins 重啟後存活（持久化）。

*   **Implication**: All variables and states must be **Serializable**.
*   **Mental Model**: Imagine the code pauses at every `sh` or `input` step, saves its state to disk, and resumes later. If an object cannot be saved to disk (like a raw `java.net.Socket` or an open file handle), the pipeline crashes.
*   **影響**：所有變數與狀態必須是 **可序列化 (Serializable)** 的。
*   **心智模型**：想像程式碼在每個 `sh` 或 `input` 步驟都會暫停，將狀態儲存到硬碟，稍後再恢復。如果物件無法被儲存到硬碟（如原始的 `java.net.Socket` 或開啟的檔案控制代碼），Pipeline 就會崩潰。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### Scenario: The "100 Microservices" Problem
### 場景：「100 個微服務」問題

In a mature DevOps environment, you might have 100 microservices.
在成熟的 DevOps 環境中，您可能有 100 個微服務。

*   **Without Shared Libs**: If the security team mandates a new container scanning tool, you must send Pull Requests to 100 repositories to update their `Jenkinsfile`. This is operationally expensive and error-prone.
*   **With Shared Libs**: You update the `buildDockerImage` function in the Shared Library repository. All 100 pipelines automatically pick up the new scanning step on their next run.
*   **無 Shared Libs**：如果資安團隊強制要求使用新的容器掃描工具，您必須發送 Pull Request 到 100 個儲存庫來更新它們的 `Jenkinsfile`。這在維運上成本極高且容易出錯。
*   **有 Shared Libs**：您只需更新 Shared Library 儲存庫中的 `buildDockerImage` 函式。所有 100 個 Pipeline 在下次執行時會自動採用新的掃描步驟。

### Governance and Standardization
### 治理與標準化

Shared Libraries enforce governance. By providing a "Paved Road" (e.g., a `standardSpringPipeline` function), you ensure that every team implicitly adheres to:
Shared Libraries 強制執行治理。透過提供一條「鋪好的路」（例如 `standardSpringPipeline` 函式），您確保每個團隊隱性地遵守：

1.  **Logging standards** (Log rotation, formatting).
2.  **Security checks** (SAST/DAST integration).
3.  **Artifact naming conventions**.
4.  **Notification policies** (Slack/Email on failure).
1.  **日誌標準**（日誌輪替、格式化）。
2.  **安全檢查**（SAST/DAST 整合）。
3.  **Artifact 命名慣例**。
4.  **通知策略**（失敗時發送 Slack/Email）。

---

## 4. Walkthrough / Example
## 4. 逐步示例

We will create a modular library that defines a standardized CI pipeline.
我們將建立一個模組化的函式庫，定義標準化的 CI Pipeline。

### Step 1: Directory Structure
### 步驟 1：目錄結構

Assume a Git repo named `jenkins-shared-lib`:
假設有一個名為 `jenkins-shared-lib` 的 Git 儲存庫：

```text
vars/
  standardServicePipeline.groovy
src/
  com/company/jenkins/SlackNotifier.groovy
```

### Step 2: The Custom Step (`vars/`)
### 步驟 2：自定義步驟 (`vars/`)

This file defines a global function `standardServicePipeline` that accepts a Map of configuration.
此檔案定義了一個全域函式 `standardServicePipeline`，接受一個 Map 配置。

```groovy
// vars/standardServicePipeline.groovy

def call(Map config) {
    // Set default values
    // 設定預設值
    String serviceName = config.name ?: 'unknown-service'
    String registry = config.registry ?: 'docker.io/myorg'
    
    pipeline {
        agent any
        
        options {
            timestamps()
            buildDiscarder(logRotator(numToKeepStr: '10'))
        }
        
        stages {
            stage('Checkout') {
                steps {
                    checkout scm
                }
            }
            
            stage('Test') {
                steps {
                    echo "Testing ${serviceName}..."
                    // In real world: sh './gradlew test'
                    sh 'echo "Running unit tests"'
                }
            }
            
            stage('Build & Push') {
                steps {
                    script {
                        echo "Building Docker image for ${registry}/${serviceName}..."
                        // Logic to build and push
                    }
                }
            }
        }
        
        post {
            always {
                // Using a class from src/
                // 使用 src/ 中的類別
                script {
                    def notifier = new com.company.jenkins.SlackNotifier()
                    notifier.send(currentBuild, "#ci-channel")
                }
            }
        }
    }
}
```

### Step 3: The Utility Class (`src/`)
### 步驟 3：工具類別 (`src/`)

Classes in `src` are useful for logic that doesn't need pipeline DSL steps directly, or to encapsulate complex data processing. **Note**: Classes must implement `Serializable`.
`src` 中的類別適用於不需要直接使用 Pipeline DSL 步驟的邏輯，或用於封裝複雜的資料處理。**注意**：類別必須實作 `Serializable`。

```groovy
// src/com/company/jenkins/SlackNotifier.groovy
package com.company.jenkins

class SlackNotifier implements Serializable {
    
    void send(def build, String channel) {
        String status = build.currentResult
        String msg = "Build ${build.fullDisplayName} finished with status: ${status}"
        
        // In a real scenario, you might use the slackSend step here.
        // However, accessing steps from src/ requires passing the 'script' context (advanced pattern)
        // or strictly using Groovy logic.
        // 在真實場景中，您可能會在此使用 slackSend 步驟。
        // 然而，從 src/ 存取步驟需要傳遞 'script' 上下文（進階模式），或嚴格使用 Groovy 邏輯。
        
        // For demonstration, we just return a formatted string or print
        println "[SlackNotifier] Sending to ${channel}: ${msg}"
    }
}
```

### Step 4: Usage in Client `Jenkinsfile`
### 步驟 4：在客戶端 `Jenkinsfile` 中使用

In the microservice repository, the `Jenkinsfile` becomes incredibly simple.
在微服務儲存庫中，`Jenkinsfile` 變得極其簡單。

```groovy
// Jenkinsfile in a microservice repo

// Load the library (assuming configured in Global Configuration or via @Library)
// 載入函式庫（假設已在全域配置中設定，或透過 @Library）
@Library('jenkins-shared-lib@v1.0.0') _

standardServicePipeline(
    name: 'user-service',
    registry: 'aws_account_id.dkr.ecr.us-east-1.amazonaws.com'
)
```

**Why this works**: The complex logic of stages, error handling, and notifications is abstracted away. The developer only provides configuration.
**為何有效**：Stage、錯誤處理與通知的複雜邏輯被抽象化了。開發者只需提供配置。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. The `NotSerializableException` Trap
### 1. `NotSerializableException` 陷阱

*   **Error**: `java.io.NotSerializableException: java.util.regex.Matcher` (or similar).
*   **Cause**: You defined a variable (like a Regex Matcher or an Iterator) outside of a `@NonCPS` method, and the pipeline paused (persisted) while that variable was in scope.
*   **Solution**:
    *   Put complex non-serializable logic inside a method annotated with `@NonCPS`.
    *   Clear the variable (set to null) before a blocking step.
    *   Use `steps.sh` for complex text processing instead of Groovy code.
*   **錯誤**：`java.io.NotSerializableException`。
*   **原因**：您在 `@NonCPS` 方法之外定義了一個變數（如 Regex Matcher 或 Iterator），而 Pipeline 在該變數處於作用域內時暫停（持久化）。
*   **解法**：
    *   將複雜且不可序列化的邏輯放入標註 `@NonCPS` 的方法中。
    *   在阻塞步驟之前清除該變數（設為 null）。
    *   使用 `steps.sh` 進行複雜文字處理，而非使用 Groovy 程式碼。

### 2. Using `master` Branch for Production
### 2. 在生產環境使用 `master` 分支

*   **Anti-pattern**: Configuring the library to implicitly use the `master` branch.
*   **Risk**: If you push a bug to `master` in the library repo, you instantly break builds for *every* team using that library.
*   **Solution**: Always use tagged versions (e.g., `@Library('mylib@v2.1')`) in production pipelines. Use branches only for testing library changes.
*   **反模式**：將函式庫配置為隱性使用 `master` 分支。
*   **風險**：如果您將 Bug 推送到函式庫儲存庫的 `master`，您會立即破壞所有使用該函式庫團隊的建置。
*   **解法**：在生產環境 Pipeline 中始終使用標籤版本（例如 `@Library('mylib@v2.1')`）。僅在測試函式庫變更時使用分支。

### 3. Over-Engineering (The "God Library")
### 3. 過度設計（「上帝函式庫」）

*   **Anti-pattern**: Creating a single `vars/pipeline.groovy` that handles Java, Node, Python, Docker, K8s, and Terraform logic with 50 `if/else` statements.
*   **Solution**: Modularize. Create `vars/javaPipeline.groovy`, `vars/nodePipeline.groovy`, or use Strategy Pattern in `src/`.
*   **反模式**：建立單一的 `vars/pipeline.groovy`，透過 50 個 `if/else` 語句處理 Java、Node、Python、Docker、K8s 和 Terraform 邏輯。
*   **解法**：模組化。建立 `vars/javaPipeline.groovy`、`vars/nodePipeline.groovy`，或在 `src/` 中使用策略模式。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you test Jenkins Shared Libraries before merging?
### Q1: 您如何在合併前測試 Jenkins Shared Libraries？

*   **Key Points**:
    *   **Unit Testing**: Use frameworks like **JenkinsSpock** or **JenkinsPipelineUnit**. This allows mocking pipeline steps (`sh`, `git`) and asserting logic without a running Jenkins instance.
    *   **Integration Testing**: Have a "playground" Jenkins job or folder configured to load the library from a specific feature branch (`@Library('mylib@feature/test')`).
    *   **Replay**: Mention the "Replay" feature in Jenkins UI for quick ad-hoc testing of modified library code.
*   **關鍵要點**：
    *   **單元測試**：使用 **JenkinsSpock** 或 **JenkinsPipelineUnit** 等框架。這允許在沒有執行 Jenkins 實例的情況下模擬 Pipeline 步驟（`sh`、`git`）並斷言邏輯。
    *   **整合測試**：設定一個「遊樂場」Jenkins Job 或資料夾，配置為從特定功能分支載入函式庫（`@Library('mylib@feature/test')`）。
    *   **重播 (Replay)**：提及 Jenkins UI 中的「Replay」功能，用於快速臨時測試修改後的函式庫程式碼。

### Q2: Explain the difference between `scripted` and `declarative` syntax within a Shared Library.
### Q2: 請解釋 Shared Library 中 `scripted` 與 `declarative` 語法的差異。

*   **Key Points**:
    *   Shared Libraries often use Scripted Pipeline syntax under the hood because it offers more flexibility (loops, try/catch, complex logic) than Declarative.
    *   However, you can wrap Declarative Pipeline code inside a `call()` method (as seen in the example) to provide a clean interface to users.
    *   **Advanced**: Mention that Declarative directives (like `libraries`, `options`) are processed before the Groovy script execution begins, which can sometimes limit dynamic library loading.
*   **關鍵要點**：
    *   Shared Libraries 在底層通常使用 Scripted Pipeline 語法，因為它比 Declarative 提供更多彈性（迴圈、try/catch、複雜邏輯）。
    *   然而，您可以將 Declarative Pipeline 程式碼包裝在 `call()` 方法中（如範例所示），以為使用者提供簡潔的介面。
    *   **進階**：提及 Declarative 指令（如 `libraries`、`options`）是在 Groovy 腳本執行開始前處理的，這有時會限制動態函式庫的載入。

### Q3: How do you handle secrets securely in a Shared Library?
### Q3: 您如何在 Shared Library 中安全地處理機密？

*   **Key Points**:
    *   Never hardcode secrets.
    *   Use the `withCredentials` block (binding credentials to environment variables).
    *   Encapsulate the `withCredentials` logic inside the library so individual `Jenkinsfiles` don't need to know the Credential ID. This centralizes security management.
*   **關鍵要點**：
    *   絕不硬編碼機密。
    *   使用 `withCredentials` 區塊（將憑證綁定到環境變數）。
    *   將 `withCredentials` 邏輯封裝在函式庫內，這樣個別的 `Jenkinsfile` 就不需要知道 Credential ID。這能集中安全管理。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **DRY Principle**: Shared Libraries prevent code duplication across microservices.
    **DRY 原則**：Shared Libraries 防止微服務之間的程式碼重複。
2.  **`vars` vs `src`**: Use `vars` for pipeline steps (DSLs), `src` for heavy logic and OOP.
    **`vars` vs `src`**：使用 `vars` 處理 Pipeline 步驟 (DSL)，`src` 處理重邏輯與 OOP。
3.  **Versioning**: Always pin library versions in production (`@v1.0`) to avoid outages.
    **版本控制**：在生產環境中始終鎖定函式庫版本（`@v1.0`）以避免中斷。
4.  **Serialization**: Be aware of CPS limitations; ensure objects are Serializable or use `@NonCPS`.
    **序列化**：注意 CPS 限制；確保物件可序列化或使用 `@NonCPS`。
5.  **Testing**: Treat pipeline code like app code—write unit tests (JenkinsSpock).
    **測試**：將 Pipeline 程式碼視為應用程式碼——撰寫單元測試 (JenkinsSpock)。

### Next Steps
### 後續延伸

*   **Configuration as Code (JCasC)**: Learn how to configure the Global Shared Library settings automatically using YAML.
    **Configuration as Code (JCasC)**：學習如何使用 YAML 自動配置全域 Shared Library 設定。
*   **Dynamic Agents**: In the next chapter, we will explore running these libraries on ephemeral agents (Kubernetes/Docker) to scale infrastructure.
    **動態代理 (Dynamic Agents)**：在下一章中，我們將探討如何在臨時代理（Kubernetes/Docker）上執行這些函式庫，以擴展基礎設施。