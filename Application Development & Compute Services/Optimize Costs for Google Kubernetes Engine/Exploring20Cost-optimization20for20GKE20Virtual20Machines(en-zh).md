
# Exploring Cost-optimization for GKE Virtual Machines（探索 GKE 虛擬機成本最佳化）
https://www.skills.google/course_templates/655/labs/598638

## Task 1. Understanding Node machine types（任務 1：理解節點機器類型）
### General overview（總覽）
A machine type is a set of virtualized hardware resources available to a virtual machine (VM) instance, including the system memory size, virtual CPU (vCPU) count, and persistent disk limits. Machine types are grouped and curated by families for different workloads.（機器類型是供虛擬機（VM）使用的一組虛擬化硬體資源，包含系統記憶體大小、虛擬 CPU（vCPU）數量與持久性磁碟上限；機器類型依工作負載分成不同家族並加以規劃。）
When choosing a machine type for your node pool, the general purpose machine type family typically offers the best price-performance ratio for a variety of workloads. The general purpose machine types consist of the N-series and E2-series:（為節點池選擇機器類型時，通用型家族通常在多種工作負載下提供最佳的價格/效能；通用型包含 N 系列與 E2 系列：）
![alt text](image-5.png)
The differences between the machine types might help your app and they might not. In general, E2s have similar performance to N1s but are optimized for cost. Usually, utilizing the E2 machine type alone can help save on costs.（不同機器類型的差異未必都能改善你的應用；一般而言，E2 與 N1 的效能相近但更著重成本最佳化，僅使用 E2 機器類型常能降低支出。）
However, with a cluster, it's most important that the resources utilized are optimized based on your application’s needs. For bigger applications or deployments that need to scale heavily, it can be cheaper to stack your workloads on a few optimized machines rather than spreading them across many general purpose ones.（然而在叢集環境中，最重要的是依應用需求最佳化資源使用；對大型或需大量擴展的部署，把工作負載集中在少數經過最佳化的機器上，往往比分散於眾多通用型機器更省成本。）
Understanding the details of your app is important for this decision making progress. If your app has specific requirements, you can make sure the machine type is shaped to fit the app.（了解應用細節對決策至關重要；若你的應用有特定需求，可選擇更貼合該需求的機器型態。）
In the following section, you will take a look at a demo app and migrate it to a node pool with a well-shaped machine type.（下節將觀察一個示範應用，並遷移到機器型態更貼合需求的節點池。）

## Task 2. Choosing the right machine type for the Hello app（任務 2：為 Hello 應用選擇合適的機器類型）
### Inspect the Hello demo cluster's requirements（檢視 Hello 示範叢集的需求）
On startup, your lab generated a [Hello Demo Cluster] with two E2 medium (2vCPU, 4GB memory) nodes. This cluster is deploying one replica of a simple web application called [Hello App], a web server written in Go that responds to all requests with the message "Hello, World!".（啟動時，本實作建立一個含兩個 E2 medium（2vCPU、4GB 記憶體）節點的 Hello 示範叢集；叢集中部署一個以 Go 撰寫的簡單 Web 應用 Hello App，會以「Hello, World!」回應所有請求。）
1. Once your lab has finished provisioning, in the Cloud Console, click on your Navigation Menu and then click on `Kubernetes Engine`.（佈建完成後，於 Cloud Console 點選導覽選單並進入 `Kubernetes Engine`。）
2. In the Kubernetes Clusters window, select your `hello-demo-cluster`.（在 Kubernetes Clusters 視窗選擇 `hello-demo-cluster`。）
3. In the following window, select the `Nodes` tab:（在後續視窗選擇 `Nodes` 分頁：）
![alt text](image-6.png)
You should now see a list of your cluster's nodes:（你現在應可看到叢集節點清單：）
![alt text](image-7.png)
Observe how GKE has utilized the resources of your cluster. You can see how much cpu and memory is being requested by each node as well as how much your nodes could potentially allocate.（觀察 GKE 如何使用叢集資源；你可以看到每個節點的 CPU/記憶體需求與可配置的上限。）
4. Click on the first node of your cluster.（點選叢集的第一個節點。）
Look at the `Pods` section. You should see your `hello-server` pod in the `default` namespace. If you don't see a hello-server pod, go back and select the second node of your cluster instead.（查看 `Pods` 區段；應可在 `default` 命名空間中看到 `hello-server` pod；若未看到，請返回並改選第二個節點。）
You'll notice the `hello-server` pod is requesting 400 mcpu. You should also see a handful of other `kube-system` pods running. These are loaded to help enable GKE's cluster services, like monitoring.（你會注意到 `hello-server` pod 需求為 400m CPU；也會看到多個 `kube-system` pod 正在運行，這些用於提供叢集服務（如監控）。）
5. Press the Back button to return to the previous Nodes page.（按返回回到上一個 Nodes 頁面。）
Already, you'll notice that it takes two E2-medium nodes to run one replica of your `Hello-App` along with the essential kube-system services. Also, while you're using most of the cluster's cpu resources, you're only using about 1/3rd of its allocatable memory.（此時可觀察到：要同時運行一個 `Hello-App` 副本與必要的 kube-system 服務，需兩個 E2‑medium 節點；此外，CPU 幾乎被用滿，但可配置記憶體僅使用約三分之一。）
If the workload for this app were completely static, you could create a machine type with a custom fitted shape that has the exact amount of cpu and memory needed. By doing this, you would consequently save costs on your overall cluster infrastructure.（若此應用的工作負載完全固定，你可選擇自訂形狀的機器類型，使 CPU 與記憶體精準匹配，進而節省整體叢集基礎成本。）
However, GKE clusters often run multiple workloads and those workloads will typically need to be scaled up and down.（然而 GKE 叢集常同時執行多個工作負載，且通常需要彈性擴縮。）
What would happen if the Hello App were to be scaled up?（若將 Hello App 擴展，會發生什麼情況？）

## Activate Cloud Shell（啟用 Cloud Shell）
When you are connected, you are already authenticated, and the project is set to your Project_ID, `qwiklabs-gcp-02-04757421c5e7`.（連線後已完成驗證，專案已設定為 `qwiklabs-gcp-02-04757421c5e7`。）

## Scale up Hello app（擴展 Hello 應用）
1. Access your cluster's credentials:（取得叢集憑證：）
> gcloud container clusters get-credentials hello-demo-cluster --zone us-central1-a
2. Scale up your Hello-Server:（擴展 Hello‑Server：）
> kubectl scale deployment hello-server --replicas=2
3. Back in the *Console*, select *Workloads* from the Kubernetes Engine menu on the left.（回到主控台，在左側 Kubernetes Engine 選單中選擇 *Workloads*。）
You might see your hello-server with the *Does not have minimum availability* error status.（可能會看到 hello‑server 顯示 *Does not have minimum availability* 錯誤狀態。）
4. Click on the error message to get status details. You will see that the reason is `Insufficient cpu`.（點選錯誤訊息以查看詳細狀態；原因為 `Insufficient cpu`（CPU 不足）。）
This is to be expected. If you remember, the cluster barely had any more cpu resources and you requested another 400m with another replica of the `hello-server`.（這屬預期行為；叢集幾乎沒有多餘 CPU，你又因第二個 `hello-server` 副本而再需求 400m CPU。）
5. Increase your node pool to handle your new request:（增加節點池以承載新需求：）
```
gcloud container clusters resize hello-demo-cluster --node-pool my-node-pool \
  --num-nodes 3 --zone us-central1-a
```
6. When asked to continue, type `y` and press enter.（詢問是否繼續時輸入 `y` 並按 Enter。）
7. In the Console, refresh the Workloads page until you see the status of your hello-server workload turn to OK:（在主控台重新整理 Workloads 頁面，直到 hello‑server 顯示 OK 狀態：）
![alt text](image-8.png)

## Examine your cluster（檢視叢集）
With the workload successfully scaled up, navigate back to the nodes tab of your cluster.（工作負載擴展成功後，返回叢集的 Nodes 分頁。）
1. Click on *hello-demo-cluster*:（點選 *hello-demo-cluster*：）
![alt text](image-9.png)
2. Then, click on the `Nodes` tab.（接著點選 `Nodes` 分頁。）
The larger node pool is able to handle the heavier workload, but look at how your infrastructure's resources are being utilized.（較大的節點池可承載更重的工作負載，但請留意基礎資源的使用情況。）
![alt text](image-10.png)
Although GKE uses a cluster's resources to the best of its ability, there is room for some optimization here. You can see that one of your nodes is using most of its memory, but two of your nodes have a considerable amount of unused memory.（儘管 GKE 盡可能善用叢集資源，仍有優化空間；可看到其中一個節點使用了大多數記憶體，但另外兩個節點仍保有相當多未用記憶體。）
At this point, if you continued to scale up the app, you would start to see a similar pattern. Kubernetes would attempt to find a node for each new replica of the `hello-server` deployment, fail, and then create a new node with roughly 600m of cpu.（此時若持續擴展應用，會出現類似模式：Kubernetes 嘗試為每個新副本尋找節點、失敗、然後建立一個約具 600m CPU 的新節點。）

## A binpacking problem（裝箱問題）
A binpacking problem is one in which you must fit items of various volumes/shapes into a finite number of regularly shaped “bins” or containers. Essentially, the challenge is to fit the items into the fewest number of bins, “packing” them as efficiently as possible.（所謂裝箱問題，是要把不同體積/形狀的物品放入有限數量且形狀固定的箱子中；挑戰在於以最少箱數且最高效率完成裝填。）
This is similar to the challenge faced when trying to optimize Kubernetes clusters for the applications they run. You have a number of applications, likely with various resource requirements (i.e. memory and cpu). You must try to fit these applications into the infrastructure resources Kubernetes manages for you (where most of your cluster’s cost likely lies) as efficiently as possible.（這與為 Kubernetes 叢集上的各應用進行最佳化的挑戰相似：你有多個應用，且資源需求（記憶體與 CPU）各異；需盡可能有效率地將它們安置於 Kubernetes 所管理的基礎資源（亦是叢集成本主要來源）之中。）
Your *Hello Demo Cluster* does not employ very efficient binpacking. It would be more cost-efficient to configure Kubernetes to use a machine type more fitted to this workload.（你的 *Hello 示範叢集* 的裝箱效率並不高；改用更貼合此工作負載的機器類型能提高成本效益。）
> Note: For simplicity, this lab focuses on optimizing one application. In reality, your Kubernetes cluster will likely be running many applications with varying requirements. Kubernetes has tools to help you match your application workloads to various machines Kubernetes has access to. You can use multiple GKE Node Pools to have one Kubernetes cluster manage multiple machine types.（注意：為求簡化，本實作聚焦於優化一個應用；實務上叢集通常運行多個需求各異的應用。Kubernetes 提供工具協助將工作負載對映至不同機器；你可使用多個 GKE 節點池讓單一叢集管理多種機器類型。）

## Migrate to optimized node pool（遷移到最佳化的節點池）
- Create a new node pool with a larger machine type:（建立含較大型機器類型的新節點池：）
```
gcloud container node-pools create larger-pool \
  --cluster=hello-demo-cluster \
  --machine-type=e2-standard-2 \
  --num-nodes=1 \
  --zone=us-central1-a
```
Now, you can migrate pods to the new node pool by following these steps:（現在依下列步驟將 pods 遷移至新節點池：）
1. *Cordon the existing node pool*: This operation marks the nodes in the existing node pool (node) as unschedulable. Kubernetes stops scheduling new Pods to these nodes once you mark them as unschedulable.（**封鎖（cordon）既有節點池**：將節點標記為不可排程；Kubernetes 將不再把新 Pods 排程到這些節點。）
2. *Drain the existing node pool*: This operation evicts the workloads running on the nodes of the existing node pool (node) gracefully.（**排空（drain）既有節點池**：優雅地逐出在節點上運行的工作負載。）
- First, cordon the original node pool:（首先封鎖原節點池：）
```
for node in $(kubectl get nodes -l cloud.google.com/gke-nodepool=my-node-pool -o=name); do
  kubectl cordon "$node";
done
```
- Next, drain the pool:（接著排空該池：）
```
for node in $(kubectl get nodes -l cloud.google.com/gke-nodepool=my-node-pool -o=name); do
  kubectl drain --force --ignore-daemonsets --delete-emptydir-data --grace-period=10 "$node";
done
```
At this point, you should see that your pods are running on the new, `larger-pool`, node pool:（此時可看到 pods 已運行於新的 `larger-pool` 節點池：）
> kubectl get pods -o=wide
3. With the pods migrated, it's safe to delete the old node pool:（完成遷移後即可安全刪除舊節點池：）
> gcloud container node-pools delete my-node-pool --cluster hello-demo-cluster --zone us-central1-a
4. When asked to continue, type y and enter.（詢問是否繼續時輸入 y 並按 Enter。）
Deletion can take about 2 minutes. Read the next section while you wait.（刪除約需 2 分鐘；等待期間可先閱讀下一節。）

## Cost analysis（成本分析）
You're now running the same workload which required three e2-medium machines on one e2-standard-2 machine.（你現在以一台 e2‑standard‑2 機器承載原需三台 e2‑medium 的相同工作負載。）
Take a look at the hourly cost for having an e2 standard and shared core machine types up:（比較 e2 standard 與 shared core 機器類型的每小時成本：）
Standard:（標準型：）
![alt text](image-11.png)
Shared Core:（共用核心：）
![alt text](image-12.png)
The cost of three e2-medium machines would be about $0.1 an hour while one e2-standard-2 is listed at about $0.067 an hour.（三台 e2‑medium 約 $0.1/小時；一台 e2‑standard‑2 約 $0.067/小時。）
Saving $.04 an hour may seem small, but this cost can add up over the lifetime of a running application. It would be even more noticeable at a larger scale too. Because the e2-standard-2 machine can pack your workload more efficiently and there's less unused space, the cost of scaling up would grow less quickly.（每小時省 $0.04 看似不多，但長期累積將相當可觀；在更大規模時節省更明顯。由於 e2‑standard‑2 能更有效裝載你的工作負載、未用空間較少，擴展時成本成長較慢。）
This is interesting because E2-medium is a shared cored machine type which is designed to be cost effective for small, non resource intensive applications. But, for the Hello-App's current workload, you see that using a node pool with a larger machine type ends up being a more cost effective strategy.（值得注意的是，E2‑medium 屬共用核心、設計給小型且資源需求不高的應用以降低成本；但以 Hello‑App 目前的負載來看，改用較大型機器類型的節點池反而更具成本效益。）
In the Cloud Console, you should still be on the Nodes tab of your hello-demo cluster. Refresh this tab and examine the CPU Requested and CPU Allocatable fields for your larger-pool node.（在主控台的 hello‑demo 叢集 Nodes 分頁，重新整理並檢視 larger‑pool 節點的 CPU Requested 與 CPU Allocatable 欄位。）
Notice there's room for further optimization. The new node could fit another replica of your workload without needing to provision another node. Or again, you could potentially choose a custom sized machine type that fits the CPU and memory needs of the application saving even more resources.（你會發現仍有可進一步優化的空間：新節點可再容納一個副本而不需另建節點；也可選擇自訂大小機器型態，讓 CPU/記憶體更貼合應用需求，進一步節省資源。）
It should be noted that these prices will vary depending on the location of your cluster. The next part of this lab will deal with selecting the best region and managing a regional cluster.（需注意價格會因叢集位置而異；下一節將說明如何選擇最佳區域並管理區域型叢集。）

## Selecting the appropriate location for a cluster（選擇合適的叢集位置）
### Regions and zones overview（區域與可用區概述）
Compute Engine resources, used for your cluster's nodes, are hosted in multiple locations worldwide. These locations are composed of regions and zones. A region is a specific geographical location where you can host your resources. Regions have three or more zones.（支援叢集節點的 Compute Engine 資源遍佈全球多個位置，這些位置由區域（regions）與可用區（zones）組成；區域是可託管資源的特定地理位置，且每個區域至少有三個可用區。）
Resources that live in a zone, such as virtual machine instances or zonal persistent disks, are referred to as zonal resources. Other resources, like static external IP addresses, are regional. Regional resources can be used by any resource in that region, regardless of zone, while zonal resources can only be used by other resources in the same zone.（位於單一可用區的資源（如 VM 或單一可用區的持久性磁碟）稱為「區域性資源（zonal）」；其他資源（例如固定外部 IP）則為區域層級（regional）。區域資源可供該區域內任一可用區的資源使用，而區域性資源僅能供同一可用區的資源使用。）
When choosing a region or zone, it's important to think about:（選擇區域或可用區時，需考量：）
1. *Handling failures* - If your resources for your app are only distributed in one zone and that zone becomes unavailable, your app will also become unavailable. For larger scale, high demand apps it's often best practice to distribute resources across multiple zones or regions in order to handle failures.（**故障處理**——若資源僅分佈在單一可用區且該區不可用，應用也會不可用；對大型高需求應用，最佳做法是跨多個可用區或區域分佈資源以提高容錯。）
2. *Decreased network latency* - To decrease network latency, you might want to choose a region or zone that is close to your point of service. For example, if you mostly have customers on the East Coast of the US, then you might want to choose a primary region and zone that is close to that area.（**降低網路延遲**——為降低延遲，可選擇靠近服務據點的區域或可用區；例如客戶多在美國東岸，則可選擇接近該區的主要區域與可用區。）

### Best practices for clusters（叢集最佳做法）
Costs vary between regions based on a variety of factors. For example, resources in the us-west2 region tend to be more expensive than those in us-central1.（各區域的成本因多種因素而異；例如 us‑west2 的資源通常比 us‑central1 更昂貴。）
When selecting a region or zone for your cluster, examine what your app is doing. For a latency-sensitive production environment, placing your app in a region/zone with decreased network latency and increased efficiency would likely give you the best performance-to-cost ratio.（選擇叢集所在區域/可用區時，應檢視應用特性；若是對延遲敏感的生產環境，部署在延遲較低、效率較高的區域/可用區，通常可獲得最好之效能/成本比。）
However, a non-latency-sensitive dev environment could be placed in a less expensive region to reduce costs.（相對地，對延遲不敏感的開發環境可放在較便宜的區域以降低成本。）

### Handling cluster availability（處理叢集可用性）
The types of available clusters in GKE include zonal (single-zone or multi-zonal) and regional. At face value, a single-zone cluster will be the least expensive option. However, for high-availability of your applications, it is best to distribute your cluster’s infrastructure resources across zones.（GKE 的叢集型態包含單一可用區、多可用區與區域型；表面上單一可用區叢集最省，但若要確保高可用，最好將叢集基礎資源跨可用區分散。）
For many cases, prioritizing availability in your cluster through a multi-zonal or regional cluster results in the best cost-to-performance architecture.（在許多情境下，透過多可用區或區域型叢集優先確保可用性，通常能得到最佳的成本/效能架構。）
> Note: A multi-zonal cluster has at least one additional zone defined but only has a single replica of the control plane running in a single zone. Workloads can still run during an outage of the control plane's zone, but no configurations can be made to the cluster until the control plane is available.（注意：多可用區叢集定義了至少一個額外可用區，但控制平面僅在單一可用區執行一個副本；控制平面區域故障期間，工作負載仍可運行，但無法對叢集進行設定，直至控制平面恢復。）
A regional cluster has multiple replicas of the control plane, running in multiple zones within a given region. Nodes also run in each zone where a replica of the control plane runs. Regional clusters consume the most resources but offer the best availability.（區域型叢集在同一區域的多個可用區中運行多個控制平面副本；在有控制平面副本的每個可用區都會運行節點；區域型叢集資源消耗最多，但可用性最佳。）

## Task 3. Managing a regional cluster（任務 3：管理區域型叢集）
### Setup（設定）
Managing your cluster's resources across multiple zones becomes a little more complex. If not careful, it's possible to accumulate extra costs from unnecessary inter-zonal communication between your pods.（跨多個可用區管理叢集資源會更複雜；若不注意，pods 之間不必要的跨可用區通訊可能累積額外成本。）
In this section, you'll observe the network traffic of your cluster and move two chatty pods, pods which are generating a lot of traffic to one another, to be in the same zone.（本節將觀察叢集的網路流量，並把兩個彼此頻繁通訊的 pods 移到同一可用區。）
1. In your Cloud Shell tab, create a new regional cluster (this command will take a few minutes to complete):（在 Cloud Shell 分頁建立新的區域型叢集（需幾分鐘完成）：）
> gcloud container clusters create regional-demo --region=us-central1 --num-nodes=1
In order to demonstrate traffic between your pods and nodes, you will create two pods on separate nodes in your regional cluster. We will use ping to generate traffic from one pod to the other to generate traffic which we can then monitor.（為示範 pods 與節點間的流量，將在區域型叢集不同節點上建立兩個 pods；我們使用 ping 自一個 pod 發送至另一個 pod，以便監控流量。）
2. Run this command to create a manifest for your first pod:（執行此命令為第一個 pod 建立 manifest：）
```
cat << EOF > pod-1.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-1
  labels:
    security: demo
spec:
  containers:
  - name: container-1
    image: wbitt/network-multitool
EOF
```
3. Create the first pod in Kubernetes by using this command:（以此命令在 Kubernetes 建立第一個 pod：）
> kubectl apply -f pod-1.yaml
4. Next, run this command to create a manifest for your second pod:（接著為第二個 pod 建立 manifest：）
```
cat << EOF > pod-2.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-2
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: security
            operator: In
            values:
            - demo
        topologyKey: "kubernetes.io/hostname"
  containers:
  - name: container-2
    image: us-docker.pkg.dev/google-samples/containers/gke/hello-app:1.0
EOF
```
5. Create the second pod in Kubernetes:（建立第二個 pod：）
> kubectl apply -f pod-2.yaml
The pods you created use the `node-hello` container and output a `Hello Kubernetes` message when requested.（你建立的 pods 使用 `node-hello` 容器，並在請求時輸出 `Hello Kubernetes` 訊息。）
If you look back at the `pod-2.yaml` file you created, you can see that *Pod Anti Affinity* is a defined rule. This enables you to ensure that the pod is not scheduled on the same node as `pod-1`. This is done by matching an expression based on pod-1’s security: demo label. *Pod Affinity* is used to ensure pods are scheduled on the same node, while *Pod Anti Affinity* is used to ensure pods are not scheduled on the same node.（回看 `pod-2.yaml` 可見已定義 **Pod Anti Affinity** 規則，確保該 pod 不會與 `pod-1` 排程在同一節點；透過匹配 pod‑1 的 `security: demo` 標籤達成。**Pod Affinity** 用於確保 pods 被排在同一節點；**Pod Anti Affinity** 則相反，確保不在同一節點。）
> Note: Kubernetes also has a concept of [Node Affinity](https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/), which can help you optimize which applications are run on what machine types.（注意：Kubernetes 也有 **Node Affinity** 概念，可協助優化應用與機器類型的匹配。）
In this case, Pod Anti Affinity is being used to help illustrate traffic between nodes, but smart use of Pod Anti Affinity and Pod Affinity can help you utilize your regional cluster's resources even better.（此例使用 Pod Anti Affinity 來示範跨節點流量；善用 Pod Affinity/Anti Affinity 能更有效利用區域型叢集資源。）
6. View the pods you created:（檢視所建立的 pods：）

> kubectl get pod pod-1 pod-2 --output wide

You will see both pods returned with a `Running` status and internal IPs.（你將看到兩個 pods 皆為 `Running` 並有內部 IP。）
Sample output:（範例輸出：）
![alt text](image-13.png)
Take note of the IP address of `pod-2`. You will use it in the following command.（記下 `pod-2` 的 IP；稍後命令會用到。）

### Simulate traffic（模擬流量）
1. Get a shell to your `pod-1` container:（連線到 `pod-1` 容器的 shell：）
> kubectl exec -it pod-1 -- sh
2. In your shell, send a request to pod-2 replacing [POD-2-IP] with the internal IP displayed for pod-2:（在 shell 中向 pod‑2 發送請求，並以其內部 IP 取代 [POD-2-IP]：）
> ping [POD-2-IP]
Take note of the average latency it takes to ping pod-2 from pod-1.（記下從 pod‑1 ping 到 pod‑2 的平均延遲。）

### Examine flow logs（檢視流量記錄）
With `pod-1` pinging `pod-2`, you can enable flow logs on the subnet of the VPC the cluster was created to observe traffic.（在 `pod-1` 對 `pod-2` 進行 ping 時，於叢集所用 VPC 的子網路啟用 Flow Logs 以觀察流量。）
1. Click `Enable the Network Management API` under VPC Network > `VPC Flow Logs` console.（於 VPC Network > `VPC Flow Logs` 主控台點選 `Enable the Network Management API`。）
2. Click the `Add VPC flow logs configuration` button, then under Subnets click `Add a configuration for subnets`.（點選 `Add VPC flow logs configuration`，在 Subnets 底下點選 `Add a configuration for subnets`。）
3. On the `Subnets in current project` tab, in VPC networks, check `default` then OK.（在 `Subnets in current project` 分頁於 VPC networks 勾選 `default` 並按 OK。）
4. Now select the subnet in `us-central1` region and click on `Manage flow logs` and then click `Add new configuration`.（選擇 `us-central1` 的子網路，點選 `Manage flow logs`，再按 `Add new configuration`。）
5. Click `Add a configuration` under Configurations - Subnets (Compute Engine API), then click Done.（在 Configurations - Subnets（Compute Engine API）下按 `Add a configuration`，再按 Done。）
![alt text](image-14.png)
6. Then, click Save.（接著按 Save。）
7. Next, go to cloud `Logs Explorer`. Click on `All log names`, then select `vpc_flows`. Click Apply.（前往 `Logs Explorer`，點選 `All log names`，選擇 `vpc_flows` 並按 Apply。）
You'll now see a list of logs that display a large amount of information any time something was sent or received from one of your instances.（現在你會看到訊息傳送/接收時的詳細記錄列表。）
> Note: If you do not see the vpc_flows logs name immediately, please wait for a minute and then refresh the console.（注意：若尚未看到 vpc_flows，請稍候再重新整理。）
![alt text](image-15.png)
If the logs are not generated then replace / before vpc_flows with %2F as given in the above screenshot.（若未生成記錄，請如圖所示把 vpc_flows 前的 `/` 改為 `%2F`。）
This can be a little difficult to read. Next, export it to a BigQuery table so you can query the relevant information.（這些記錄較難閱讀；接下來匯出到 BigQuery 表以便查詢相關資訊。）
8. Click on `Actions` > `Create Sink`.（點選 `Actions` > `Create Sink`。）
![alt text](image-16.png)
9. Name your sink `FlowLogsSample`.（將匯出命名為 `FlowLogsSample`。）
10. Click Next.（點選 Next。）

### Sink destination（匯出目的地）
- For your `Sink Service`, select `BigQuery Dataset`.（於 `Sink Service` 選擇 `BigQuery Dataset`。）
- For your `BigQuery Dataset`, select `Create new BigQuery dataset`.（於 `BigQuery Dataset` 選擇 `Create new BigQuery dataset`。）
- Name your dataset as 'us_flow_logs', and click `Create dataset`.（資料集命名為 `us_flow_logs`，並按 `Create dataset`。）
Everything else can be left as-is.（其他設定維持預設即可。）
1. Click `Create Sink`.（按下 `Create Sink`。）
2. Now, inspect your newly created dataset. In the Cloud Console, from the Navigation Menu in the Analytics section, click `BigQuery`.（檢視新建立的資料集：在主控台導覽選單的 Analytics 區段點選 `BigQuery`。）
3. Click Done.（按 Done。）
4. Select your project name, and then select the `us_flow_logs` to see the newly created table. If no table is there, you may need to refresh until it has been created.（選擇你的專案後選擇 `us_flow_logs` 以查看新建表；若尚未出現，請重新整理等待建立完成。）
5. Click on the `compute_googleapis_com_vpc_flows_xxx` table under your `us_flow_logs` dataset.（在 `us_flow_logs` 資料集下點選 `compute_googleapis_com_vpc_flows_xxx` 表。）
6. Click on `Query`.（點選 `Query`。）
7. In the BigQuery Editor, paste this in between `SELECT` and `FROM`:（在 BigQuery 編輯器中把以下欄位置於 `SELECT` 與 `FROM` 之間：）
```
jsonPayload.src_instance.zone AS src_zone,
jsonPayload.src_instance.vm_name AS src_vm,
jsonPayload.dest_instance.zone AS dest_zone,
jsonPayload.dest_instance.vm_name
```
8. Click Run.（點選 Run。）
You'll see the flow logs from before but filtered by source zone, source vm, destination zone, and destination vm.（你將看到先前的流量記錄，並依來源可用區/VM 與目的可用區/VM 進行過濾。）
Locate a few rows where there are calls being made between two different zones in your regional-demo cluster.（找出區域型叢集中不同可用區間的呼叫記錄。）
Observing the flow logs, you can see that there is frequent traffic between different zones.（從記錄可見不同可用區間存在頻繁流量。）
Next, you will move the pods into the same zone and observe the benefits.（接下來把 pods 移到同一可用區並觀察成效。）

### Move a chatty pod to minimize cross-zonal traffic costs（移動頻繁通訊的 pod 以降低跨可用區流量成本）
1. Back in Cloud Shell, press Ctrl + C to cancel the ping command.（回到 Cloud Shell，按 Ctrl + C 取消 ping。）
2. Type the exit command to exit pod-1's shell:（輸入 exit 離開 pod‑1 的 shell：）
> exit
3. Run this command to edit the pod-2 manifest:（執行此命令編輯 pod‑2 的 manifest：）
> sed -i 's/podAntiAffinity/podAffinity/g' pod-2.yaml
This changes your Pod Anti Affinity rule into a Pod Affinity rule while still using the same logic. Now pod-2 will be scheduled on the same node as pod-1.（這會把 Pod Anti Affinity 規則改為 Pod Affinity，邏輯不變；現在 pod‑2 會排程到與 pod‑1 相同節點。）
4. Delete the current running pod-2:（刪除目前運行中的 pod‑2：）
> kubectl delete pod pod-2
5. With pod-2 deleted, recreate it using the newly edited manifest:（刪除後以更新後的 manifest 重新建立：）
> kubectl create -f pod-2.yaml
6. View the pods you created and ensure they are both Running:（檢視兩個 pods 並確認皆為 Running：）
> kubectl get pod pod-1 pod-2 --output wide
From the output, you can see that Pod-1 and Pod-2 are now running on the same node.（輸出可見 Pod‑1 與 Pod‑2 已在同一節點上運行。）
Take note of the IP address of pod-2. You will use it in the following command.（記下 pod‑2 的 IP，稍後命令會用到。）
7. Get a shell to your pod-1 container:（連線到 pod‑1 容器：）
> kubectl exec -it pod-1 -- sh
8. In your shell, send a request to pod-2 replacing [POD-2-IP] with the internal IP for pod-2 from the earlier command:（在 shell 中對 pod‑2 發送請求，並以其內部 IP 取代 [POD-2-IP]：）
> ping [POD-2-IP]
You'll notice the average ping time between these pods is much faster now.（你會注意到這兩個 pods 間的平均 ping 時間明顯更快。）
At this point, you can go back to your flow logs BigQuery dataset and check recent logs to verify there are no more undesired inter-zonal communications.（此時可回到 BigQuery 的流量記錄資料集，檢查近期記錄以驗證不再出現不必要的跨可用區通訊。）

### Cost analysis（成本分析）
Take a look at the `VM-VM egress pricing within Google Cloud`:（查看 Google Cloud 的 `VM-VM egress` 價格：）
![alt text](image-17.png)
When the pods were pinging each other from different zones, it was costing $0.01 per GB. While that may seem small, it could add up very quickly in a large scale cluster with multiple services making frequent calls between zones.（當 pods 位於不同可用區時互相 ping，費率為 $0.01/GB；雖然看似微小，但在大型叢集中多服務頻繁跨區呼叫時，成本會迅速累積。）
When you moved the pods into the same zone, the pinging became free of charge.（當把 pods 移到同一可用區後，ping 成本為零。）
