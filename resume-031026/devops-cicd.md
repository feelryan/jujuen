# DevOps 與 CI/CD / DevOps & CI/CD | DevOps & CI/CD

## 1. 目標與範圍 | Goal & Scope
- **Demonstrate Lifecycle Ownership**: Show that you understand the software lifecycle beyond just writing code—from commit to deployment.
  - **展現生命週期所有權**：證明你理解軟體開發不僅是寫程式，還包含從提交程式碼到部署上線的完整流程。
- **Highlight Automation & Quality**: Emphasize how you use tools (Jenkins, GitLab, Docker) to automate testing and ensure code quality.
  - **強調自動化與品質**：強調你如何運用工具（Jenkins, GitLab, Docker）來自動化測試並確保程式碼品質。
- **Leverage Cloud Expertise**: Connect your Google Professional Cloud Architect certification with practical DevOps implementation.
  - **運用雲端專業**：將你的 Google 雲端架構師認證與實際的 DevOps 實作經驗連結起來。

## 2. 簡短開場稿 | Opening Script

### 30-Second "Elevator Pitch" | 30 秒電梯簡報
"As a Senior Software Engineer and Google Certified Cloud Architect, I view DevOps not just as a role but as a culture. At Innova Solutions, I maintained a cloud-native medical platform on GCP, where I actively drove CI/CD improvements using Jenkins and GitLab. My focus is always on reducing manual toil—such as automating GCP storage bucket creation—and increasing delivery velocity through automated testing and AI-assisted code reviews."

「身為資深軟體工程師與 Google 認證雲端架構師，我視 DevOps 為一種文化而非僅是一個職位。在 Innova Solutions，我維護基於 GCP 的雲原生醫療平台，並主動利用 Jenkins 與 GitLab 推動 CI/CD 流程改善。我的重心始終在於減少手動繁瑣工作——例如自動化建立 GCP 儲存桶——並透過自動化測試與 AI 輔助代碼審查來提升交付速度。」

## 3. 關鍵故事與成就 | Key Stories & Achievements

### Story 1: Driving CI/CD & Code Quality Improvements (Innova Solutions)
- **Situation**: The team needed faster feedback loops and higher code quality for a critical medical imaging platform.
  - **情境**：團隊在開發關鍵醫療影像平台時，需要更快的反饋循環與更高的程式碼品質。
- **Task**: Optimize the development pipeline to reduce review time and deployment friction.
  - **任務**：優化開發流程，以減少審查時間並降低部署摩擦。
- **Action**: I leveraged AI-assisted development tools for refactoring and enforced stricter CI checks (using Jenkins/GitLab) to catch issues early. I also promoted a culture of smaller, more frequent commits.
  - **行動**：我利用 AI 輔助開發工具進行重構，並實施更嚴格的 CI 檢查（使用 Jenkins/GitLab）以儘早發現問題。我也推動了更小、更頻繁提交程式碼的文化。
- **Result**: This increased delivery velocity and reduced the time spent on manual code reviews, allowing the team to focus on feature development.
  - **結果**：這提升了交付速度，並減少了手動代碼審查的時間，讓團隊能專注於功能開發。

### Story 2: Infrastructure Automation on GCP (Innova Solutions)
- **Situation**: Onboarding new customers required manual setup of storage resources, which was error-prone and slow.
  - **情境**：新客戶的導入需要手動設定儲存資源，這既容易出錯又緩慢。
- **Task**: Automate the provisioning of GCP Storage Buckets for new tenants.
  - **任務**：自動化新租戶的 GCP Storage Buckets 配置流程。
- **Action**: I designed a backend mechanism to automatically create and configure GCP Storage Buckets upon customer registration, ensuring correct permissions and security settings.
  - **行動**：我設計了一套後端機制，在客戶註冊時自動建立並配置 GCP 儲存桶，確保權限與資安設定正確。
- **Result**: Eliminated manual operational toil and ensured consistent security compliance for all new customers.
  - **結果**：消除了手動維運的繁瑣工作，並確保所有新客戶皆符合一致的資安合規標準。

### Story 3: Test-Driven Development & Reliability (Hiveel)
- **Situation**: The vehicle search engine backend needed high reliability to handle advanced queries without regression.
  - **情境**：車輛搜尋引擎後端需要高可靠性，以處理進階查詢且不發生回歸錯誤。
- **Task**: Establish a robust testing strategy to support continuous integration.
  - **任務**：建立穩健的測試策略以支援持續整合。
- **Action**: I adopted TDD using JUnit5 and H2 (in-memory DB), ensuring that every API change was verified by automated tests before merging.
  - **行動**：我採用 TDD（測試驅動開發），使用 JUnit5 與 H2（記憶體資料庫），確保每次 API 變更在合併前都經過自動化測試驗證。
- **Result**: Significantly improved backend performance and stability, serving as a solid foundation for the CI pipeline.
  - **結果**：顯著提升了後端效能與穩定性，成為 CI 流程的堅實基礎。

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

### Q1: How do you handle a broken build in the CI pipeline?
- **Concept**: "Stop the line" mentality.
  - **概念**：「產線暫停」的心態。
- **Response**: "First, we notify the team immediately. The priority is to fix the build before adding new features. I investigate the logs, reproduce it locally if possible (using Docker), and either revert the change or push a hotfix. A broken build blocks everyone, so it’s P0."
  - **回答**：「首先，立即通知團隊。首要任務是在新增功能前修復構建。我會查看日誌，盡可能在本地（使用 Docker）重現，然後選擇回滾變更或推送修復補丁。構建失敗會阻礙所有人，所以是最高優先級（P0）。」

### Q2: You mentioned Jenkins and GitLab. Which do you prefer and why?
- **Concept**: Declarative (GitLab CI) vs. Imperative/Plugin-heavy (Jenkins).
  - **概念**：宣告式（GitLab CI）與 指令式/插件導向（Jenkins）。
- **Response**: "I have experience with both. Jenkins is powerful and highly customizable with plugins, but can become complex to maintain. GitLab CI feels more modern with its YAML-based declarative pipelines and tight integration with the repository. For new projects, I prefer GitLab for its simplicity and 'Pipeline as Code' philosophy."
  - **回答**：「我兩者都有經驗。Jenkins 功能強大且透過插件高度可客製化，但維護起來可能變得很複雜。GitLab CI 感覺更現代，擁有基於 YAML 的宣告式流程且與程式碼庫緊密整合。對於新專案，我傾向使用 GitLab，因為它簡潔且符合『流程即代碼』的理念。」

### Q3: How do you ensure security in your CI/CD pipeline? (DevSecOps)
- **Concept**: Shift left.
  - **概念**：左移（Shift Left）。
- **Response**: "I integrate security checks early. This includes static analysis (SAST) during the build, dependency scanning for vulnerabilities (e.g., Maven/npm audit), and ensuring container images (Docker) are scanned before deployment. As a Cloud Architect, I also ensure IAM roles for the pipeline are least-privilege."
  - **回答**：「我會儘早整合資安檢查。這包含構建時的靜態分析（SAST）、相依套件弱點掃描（如 Maven/npm audit），並確保 Docker 映像檔在部署前經過掃描。身為雲端架構師，我也會確保流程使用的 IAM 角色符合最小權限原則。」

## 5. 技術深挖提示 | Technical Deep‑Dive Prompts
*若面試官針對技術細節深挖，請準備以下架構：*

- **Containerization (Docker)**:
  - Be ready to explain `Dockerfile` optimization (multi-stage builds to reduce image size).
  - 準備解釋 `Dockerfile` 優化（如多階段構建以縮減映像檔大小）。
- **Deployment Strategies**:
  - Explain the difference between **Blue/Green** (zero downtime, instant switch) vs. **Canary** (gradual rollout). Given your cloud background, mention how GCP handles this.
  - 解釋 **藍/綠部署**（零停機、瞬間切換）與 **金絲雀部署**（漸進式推廣）的差異。考量你的雲端背景，可提及 GCP 如何處理這些。
- **Infrastructure as Code (IaC)**:
  - Even if you used scripts for the "Bucket Auto-Creation," mention the concept of IaC (like Terraform) as the industry standard you aim for.
  - 即使你在「自動建立儲存桶」時是使用腳本，也要提及 IaC（如 Terraform）作為你認同的業界標準概念。

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

- **Trap**: Thinking DevOps is only for the "Ops" team.
  - **陷阱**：認為 DevOps 只是「維運團隊」的工作。
- **Correction**: "As a Senior Engineer, I believe quality and deployment are shared responsibilities. I don't just throw code over the wall; I own the service reliability."
  - **糾正**：「身為資深工程師，我相信品質與部署是共同責任。我不會寫完程式就丟給別人，我對服務的可靠性負責。」

- **Trap**: Over-complicating the pipeline description.
  - **陷阱**：過度複雜化流程的描述。
- **Correction**: Keep it simple: Build -> Test -> Scan -> Deploy. Focus on the *value* (speed, safety) rather than listing 50 tools.
  - **糾正**：保持簡單：構建 -> 測試 -> 掃描 -> 部署。專注於*價值*（速度、安全性），而非列舉 50 種工具。

## 7. 收尾與反問 | Closing & Questions for Interviewer

### Closing Statement | 總結
"My experience combines hands-on application development with a strong architectural perspective on infrastructure. Whether it's optimizing a Jenkins pipeline or designing cloud-native resources on GCP, my goal is always to enable the team to ship faster and more safely."
「我的經驗結合了實務應用程式開發與強大的基礎架構架構觀點。無論是優化 Jenkins 流程或是在 GCP 上設計雲原生資源，我的目標始終是協助團隊更快、更安全地交付產品。」

### Questions to Ask | 可提問的問題
1. "Could you describe the current maturity of your CI/CD pipeline? Is it fully automated from commit to production?"
   - 「能否請您描述目前貴團隊 CI/CD 流程的成熟度？從提交到生產環境是否已完全自動化？」
2. "How does the team handle infrastructure changes? Is it managed via Terraform or similar IaC tools?"
   - 「團隊如何處理基礎架構的變更？是透過 Terraform 或類似的 IaC 工具管理嗎？」
3. "What is the biggest bottleneck currently slowing down the team's deployment velocity?"
   - 「目前拖慢團隊部署速度的最大瓶頸是什麼？」