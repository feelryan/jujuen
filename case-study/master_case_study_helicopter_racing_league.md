## Helicopter Racing League 直升機競賽聯盟

### Company overview 公司概覽

Helicopter Racing League (HRL) is a global sports league for competitive helicopter racing. Helicopter Racing League (HRL) 是一個競爭性直升機競賽的全球體育聯盟 。
Each year HRL holds the world championship and several regional league competitions where teams compete to earn a spot in the world championship. 每年 HRL 都會舉辦世界錦標賽和多項區域聯盟競賽，各隊在此競爭以獲得參加世界錦標賽的資格 。
HRL offers a paid service to stream the races all over the world with live telemetry and predictions throughout each race. HRL 提供付費服務來串流世界各地的比賽，並在每場比賽中提供即時遙測和預測 。

### Solution concept 解決方案概念

HRL wants to migrate their existing service to a new platform to expand their use of managed Al and ML services to facilitate race predictions. HRL 希望將其現有服務遷移到新平台，以擴展對代管 AI 和機器學習 (ML) 服務的使用，從而促進賽事預測 。
Additionally, as new fans engage with the sport, particularly in emerging regions, they want to move the serving of their content, both real-time and recorded, closer to their users. 此外，隨著新粉絲參與這項運動（特別是在新興地區），他們希望將即時和錄製內容的提供移至更靠近用戶的地方 。

### Existing technical environment 現有技術環境

HRL is a public cloud-first company; the core of their mission-critical applications runs on their current public cloud provider. HRL 是一家具備公有雲優先策略的公司；其關鍵任務應用程式的核心運行在目前的公有雲供應商上 。
Video recording and editing is performed at the race tracks, and the content is encoded and transcoded, where needed, in the cloud. 影片錄製和剪輯是在賽道現場進行的，內容會根據需要在雲端進行編碼和轉碼 。
Enterprise-grade connectivity and local compute is provided by truck-mounted mobile data centers. 企業級連線和在地端運算由車載移動數據中心提供 。
Their race prediction services are hosted exclusively on their existing public cloud provider. Their existing technical environment is as follows: 他們的賽事預測服務專門代管在現有的公有雲供應商上。其現有的技術環境如下 ：

* Existing content is stored in an object storage service on their existing public cloud provider. 現有內容儲存在現有公有雲供應商的物件儲存服務中 。


* Video encoding and transcoding is performed on VMs created for each job. 影片編碼和轉碼是在為每個作業建立的虛擬機 (VM) 上進行的 。


* Race predictions are performed using TensorFlow running on VMs in the current public cloud provider. 賽事預測是使用運行在目前公有雲供應商虛擬機上的 TensorFlow 進行的 。



### Business requirements 業務需求

HRL's owners want to expand their predictive capabilities and reduce latency for their viewers in emerging markets. HRL 的所有者希望擴大他們的預測能力，並降低新興市場觀眾的延遲 。
Their requirements are: 他們的要求是 ：

* Support ability to expose the predictive models to partners. 支援向合作夥伴開放預測模型的能力 。


* Increase predictive capabilities during and before races: 在賽事期間和賽前增加預測能力 ：


* Race results 賽事結果 


* Mechanical failures 機械故障 


* Crowd sentiment 群眾情緒 




* Increase telemetry and create additional insights. 增加遙測數據並創造額外的洞察 。


* Measure fan engagement with new predictions. 衡量粉絲對新預測的參與度 。


* Enhance global availability and quality of the broadcasts. 增強廣播的全球可用性和品質 。


* Increase the number of concurrent viewers. 增加同時觀看的觀眾人數 。


* Minimize operational complexity. 極小化運作複雜性 。


* Ensure compliance with regulations. 確保符合法規規範 。


* Create a merchandising revenue stream. 建立商品銷售收入流 。



### Technical requirements 技術需求

* Maintain or increase prediction throughput and accuracy. 維持或提高預測吞吐量與準確度 。


* Reduce viewer latency. 降低觀眾延遲 。


* Increase transcoding performance. 提高轉碼效能 。


* Create real-time analytics of viewer consumption patterns and engagement. 建立觀眾消費模式和參與度的即時分析 。


* Create a data mart to enable processing of large volumes of race data. 建立一個資料集市，以處理大量的賽事數據 。



### Executive statement 執行長聲明

Our CEO, S. Hawke, wants to bring high-adrenaline racing to fans all around the world. 我們的執行長 S. Hawke 希望為全世界的粉絲帶來腎上腺素飆升的賽事 。
We listen to our fans, and they want enhanced video streams that include predictions of events within the race (e.g., overtaking). 我們傾聽粉絲的心聲，他們希望增強影片串流，包含賽事中事件的預測（例如：超車）。
Our current platform allows us to predict race outcomes but lacks the facility to support real-time predictions during races and the capacity to process season-long results. 我們目前的平台允許我們預測比賽結果，但缺乏支援賽事期間即時預測的功能，以及處理整個賽季結果的能力 。