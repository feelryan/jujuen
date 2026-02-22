
# Mountkirk Games

## Company overview

Mountkirk Games makes online, session-based, multiplayer games for mobile platforms. Mountkirk Games 製作針對行動平台的線上、基於連線階段 (session-based) 的多人遊戲。 They have recently started expanding to other platforms after successfully migrating their on-premises environments to Google Cloud. 在成功將其地端環境遷移至 Google Cloud 後，他們最近開始擴展至其他平台。

Their most recent endeavor is to create a retro-style first-person shooter (FPS) game that allows hundreds of simultaneous players to join a geo-specific digital arena from multiple platforms and locations. 他們最近的嘗試是創建一款復古風格的第一人稱射擊 (FPS) 遊戲，允許數百名同時在線的玩家從多個平台和地點加入特定地理位置的數位競技場。 A real-time digital banner will display a global leaderboard of all the top players across every active arena. 即時數位橫幅將顯示所有活躍競技場中頂尖玩家的全球排行榜。

## Solution concept

Mountkirk Games is building a new multiplayer game that they expect to be very popular. Mountkirk Games 正在構建一款他們預期會非常受歡迎的新多人遊戲。 They plan to deploy the game’s backend on Google Kubernetes Engine so they can scale rapidly and use Google’s global load balancer to route players to the closest regional game arenas. 他們計畫將遊戲後端部署在 Google Kubernetes Engine 上，以便能快速擴展，並使用 Google 的全球負載平衡器 (global load balancer) 將玩家引導至最近的區域遊戲競技場。 In order to keep the global leader board in sync, they plan to use a multi-region Spanner cluster. 為了保持全球排行榜同步，他們計畫使用多區域 (multi-region) Spanner 叢集。

## Existing technical environment

The existing environment was recently migrated to Google Cloud, and five games came across using lift-and-shift virtual machine migrations, with a few minor exceptions. 現有環境最近已遷移至 Google Cloud，其中五款遊戲是透過隨轉隨用 (lift-and-shift) 的虛擬機器遷移方式轉移過來的，僅有少數例外。

Each new game exists in an isolated Google Cloud project nested below a folder that maintains most of the permissions and network policies. 每款新遊戲都存在於一個獨立的 Google Cloud 專案中，該專案位於維護大部分權限和網路政策的資料夾 (folder) 下層。 Legacy games with low traffic have been consolidated into a single project. 低流量的舊款遊戲已被整併到單一專案中。 There are also separate environments for development and testing. 此外還有用於開發和測試的獨立環境。

## Business requirements

*   Support multiple gaming platforms. 支援多種遊戲平台。
*   Support multiple regions. 支援多個區域。
*   Support rapid iteration of game features. 支援遊戲功能的快速疊代。
*   Minimize latency. 最小化延遲。
*   Optimize for dynamic scaling. 針對動態擴展進行最佳化。
*   Use managed services and pooled resources. 使用託管服務 (managed services) 和資源池。
*   Minimize costs. 最小化成本。

## Technical requirements

*   Dynamically scale based on game activity. 根據遊戲活動進行動態擴展。
*   Publish scoring data on a near real–time global leaderboard. 在近乎即時的全球排行榜上發布得分數據。
*   Store game activity logs in structured files for future analysis. 將遊戲活動日誌儲存在結構化檔案中以供日後分析。
*   Use GPU processing to render graphics server-side for multi-platform support. 使用 GPU 處理在伺服器端渲染圖形，以支援多平台。
*   Support eventual migration of legacy games to this new platform. 支援將舊款遊戲最終遷移至此新平台。

## Executive statement

Our last game was the first time we used Google Cloud, and it was a tremendous success. 我們的上一款遊戲是我們首次使用 Google Cloud，並取得了巨大的成功。 We were able to analyze player behavior and game telemetry in ways that we never could before. 我們能夠以前所未有的方式分析玩家行為和遊戲遙測數據 (telemetry)。 This success allowed us to bet on a full migration to the cloud and to start building all-new games using cloud-native design principles. 這次成功讓我們決定將全部業務遷移至雲端，並開始使用雲端原生 (cloud-native) 設計原則來構建所有新遊戲。 Our new game is our most ambitious to date and will open up doors for us to support more gaming platforms beyond mobile. 我們的新遊戲是迄今為止最具野心的作品，將為我們開啟支援行動裝置以外更多遊戲平台的大門。 Latency is our top priority, although cost management is the next most important challenge. 延遲是我們的首要考量，儘管成本管理是其次重要的挑戰。 As with our first cloud-based game, we have grown to expect the cloud to enable advanced analytics capabilities so we can rapidly iterate on our deployments of bug fixes and new functionality. 正如我們的第一款雲端遊戲一樣，我們已逐漸期望雲端能提供進階分析功能，以便我們能夠快速疊代錯誤修復和新功能的部署。