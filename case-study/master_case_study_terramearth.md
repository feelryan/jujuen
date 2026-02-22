# TerramEarth

## Company overview
**公司概覽**

TerramEarth manufactures heavy equipment for the mining and agricultural industries. TerramEarth 製造用於採礦和農業的重型設備。
They currently have over 500 dealers and service centers in 100 countries. 他們目前在 100 個國家擁有超過 500 家經銷商和服務中心。
Their mission is to build products that make their customers more productive. 他們的使命是打造能讓客戶更具生產力的產品。

## Solution concept
**解決方案概念**

There are 2 million TerramEarth vehicles in operation currently, and we see 20% yearly growth. 目前有 200 萬輛 TerramEarth 車輛在運行中，且我們看到每年 20% 的增長。
Vehicles collect telemetry data from many sensors during operation. 車輛在運行期間會從許多感測器收集遙測數據。
A small subset of critical data is transmitted from the vehicles in real time to facilitate fleet management. 一小部分的關鍵數據會從車輛即時傳輸，以促進車隊管理。
The rest of the sensor data is collected, compressed, and uploaded daily when the vehicles return to home base. 其餘的感測器數據會被收集、壓縮，並在車輛返回基地時每天上傳。
Each vehicle usually generates 200 to 500 megabytes of data per day. 每輛車通常每天產生 200 到 500 MB 的數據。

## Existing technical environment
**現有技術環境**

TerramEarth’s vehicle data aggregation and analysis infrastructure resides in Google Cloud and serves clients from all around the world. TerramEarth 的車輛數據聚合與分析基礎架構位於 Google Cloud 中，並服務來自世界各地的客戶。
A growing amount of sensor data is captured from their two main manufacturing plants and sent to private data centers that contain their legacy inventory and logistics management systems. 從他們的兩個主要製造工廠捕獲的感測器數據量日益增加，並發送到包含其舊有庫存和物流管理系統的私有資料中心。
The private data centers have multiple network interconnects configured to Google Cloud. 這些私有資料中心配置了多條通往 Google Cloud 的網路互連 (Network Interconnects)。
The web frontend for dealers and customers is running in Google Cloud and allows access to stock management and analytics. 供經銷商和客戶使用的網頁前端運行在 Google Cloud 上，並允許存取庫存管理和分析功能。

## Business requirements
**商業需求**

*   Predict and detect vehicle malfunction and rapidly ship parts to dealerships for just-in-time repair where possible. 預測和檢測車輛故障，並在可能的情況下迅速將零件運送到經銷商處進行即時 (Just-in-time) 維修。
*   Decrease cloud operational costs and adapt to seasonality. 降低雲端營運成本並適應季節性變化。
*   Increase speed and reliability of development workflow. 提高開發工作流程的速度和可靠性。
*   Allow remote developers to be productive without compromising code or data security. 允許遠端開發人員在不犧牲程式碼或數據安全性的情況下保持生產力。
*   Create a flexible and scalable platform for developers to create custom API services for dealers and partners. 建立一個靈活且可擴展的平台，供開發人員為經銷商和合作夥伴創建自定義 API 服務。

## Technical requirements
**技術需求**

*   Create a new abstraction layer for HTTP API access to their legacy systems to enable a gradual move into the cloud without disrupting operations. 為存取其舊有系統的 HTTP API 創建一個新的抽象層，以便在不中斷營運的情況下逐步遷移到雲端。
*   Modernize all CI/CD pipelines to allow developers to deploy container-based workloads in highly scalable environments. 現代化所有 CI/CD 管道，允許開發人員在高度可擴展的環境中部署基於容器的工作負載。
*   Allow developers to run experiments without compromising security and governance requirements. 允許開發人員在不犧牲安全性和治理要求的情況下進行實驗。
*   Create a self-service portal for internal and partner developers to create new projects, request resources for data analytics jobs, and centrally manage access to the API endpoints. 為內部和合作夥伴開發人員建立一個自助服務門戶，以創建新專案、請求數據分析作業的資源，並集中管理對 API 端點的存取。
*   Use cloud-native solutions for keys and secrets management and optimize for identity-based access. 使用雲原生解決方案進行金鑰和機密管理，並針對基於身分的存取進行優化。
*   Improve and standardize tools necessary for application and network monitoring and troubleshooting. 改進並標準化應用程式和網路監控與故障排除所需的工具。

## Executive statement
**高層聲明**

Our competitive advantage has always been our focus on the customer, with our ability to provide excellent customer service and minimize vehicle downtimes. 我們的競爭優勢一直是我們對客戶的關注，以及我們提供卓越客戶服務和最大限度減少車輛停機時間的能力。
After moving multiple systems into Google Cloud, we are seeking new ways to provide best-in-class online fleet management services to our customers and improve operations of our dealerships. 在將多個系統遷移到 Google Cloud 後，我們正在尋求新方法，為客戶提供一流的線上車隊管理服務，並改善經銷商的營運。
Our 5-year strategic plan is to create a partner ecosystem of new products by enabling access to our data, increasing autonomous operation capabilities of our vehicles, and creating a path to move the remaining legacy systems to the cloud. 我們的 5 年戰略計劃是透過開放數據存取權、增強車輛的自動駕駛操作能力，以及建立將剩餘舊有系統遷移到雲端的路徑，來創建新產品的合作夥伴生態系統。