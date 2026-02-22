# Challenge Lab - Develop your Google Cloud Network

https://www.skills.google/course_templates/625/labs/592706

## Challenge scenario
As a cloud engineer at Jooli Inc. and recently trained with Google Cloud and Kubernetes, you have been asked to help a new team (Griffin) set up their environment. The team has asked for your help and has done some work, but needs you to complete the work.

You are expected to have the skills and knowledge for these tasks so don’t expect step-by-step guides.

You need to complete the following tasks:

- Create a development VPC with three subnets manually
- Create a production VPC with three subnets manually
- Create a bastion that is connected to both VPCs
- Create a development Cloud SQL Instance and connect and prepare the WordPress environment
- Create a Kubernetes cluster in the development VPC for WordPress
- Prepare the Kubernetes cluster for the WordPress environment
- Create a WordPress deployment using the supplied configuration
- Enable monitoring of the cluster
- Provide access for an additional engineer

Some Jooli Inc. standards you should follow:

- Create all resources in the `us-central1` region and `us-central1-c` zone, unless otherwise directed.
- Use the project VPCs.
- Naming is normally team-resource, e.g. an instance could be named `kraken-webserver1`.
- Allocate cost effective resource sizes. Projects are monitored and excessive resource use will result in the containing - project's termination (and possibly yours), so beware. This is the guidance the monitoring team is willing to share: unless - directed, use e2-medium.

### Your challenge
You need to help the team with some of their initial work on a new project. They plan to use WordPress and need you to set up a development environment. Some of the work was already done for you, but other parts require your expert skills.

As soon as you sit down at your desk and open your new laptop you receive the following request to complete these tasks. Good luck!

#### Environment

![alt text](image-1.png)

## Task 1. Create development VPC manually
- Create a VPC called griffin-dev-vpc with the following subnets only:
    - griffin-dev-wp
        - IP address block: 192.168.16.0/20
    - griffin-dev-mgmt
        - IP address block: 192.168.32.0/20


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Based on the instructions, your region is **`europe-west1`**.

Run these commands in Cloud Shell:

```bash
# Set the region variable
export REGION=europe-west1

# Create the custom VPC
gcloud compute networks create griffin-dev-vpc --subnet-mode=custom

# Create the 'griffin-dev-wp' subnet
gcloud compute networks subnets create griffin-dev-wp \
    --network=griffin-dev-vpc \
    --region=$REGION \
    --range=192.168.16.0/20

# Create the 'griffin-dev-mgmt' subnet
gcloud compute networks subnets create griffin-dev-mgmt \
    --network=griffin-dev-vpc \
    --region=$REGION \
    --range=192.168.32.0/20
```

**What this does:**
1.  Creates the network shell.
2.  Adds the WordPress subnet (`192.168.16.0/20`).
3.  Adds the Management subnet (`192.168.32.0/20`).

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 2. Create production VPC manually
- Create a VPC called griffin-prod-vpc with the following subnets only:
    - griffin-prod-wp
        - IP address block: 192.168.48.0/20
    - griffin-prod-mgmt
        - IP address block: 192.168.64.0/20


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

This follows the same pattern as Task 1, using the `europe-west1` region.

```bash
# Create the custom Production VPC
gcloud compute networks create griffin-prod-vpc --subnet-mode=custom

# Create the 'griffin-prod-wp' subnet
gcloud compute networks subnets create griffin-prod-wp \
    --network=griffin-prod-vpc \
    --region=$REGION \
    --range=192.168.48.0/20

# Create the 'griffin-prod-mgmt' subnet
gcloud compute networks subnets create griffin-prod-mgmt \
    --network=griffin-prod-vpc \
    --region=$REGION \
    --range=192.168.64.0/20
```

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 3. Create bastion host
- Create a bastion host with two network interfaces, one connected to `griffin-dev-mgmt` and the other connected to `griffin-prod-mgmt`. Make sure you can SSH to the host.


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

These commands create firewall rules to allow SSH access and then create the VM instance with **two network interfaces** (one for the Dev VPC, one for the Prod VPC).

```bash
# Set the Zone variable
export ZONE=europe-west1-c

# 1. Create Firewall rule for Dev VPC to allow SSH
gcloud compute firewall-rules create griffin-dev-allow-ssh \
    --network=griffin-dev-vpc \
    --allow=tcp:22 \
    --source-ranges=0.0.0.0/0

# 2. Create Firewall rule for Prod VPC to allow SSH
gcloud compute firewall-rules create griffin-prod-allow-ssh \
    --network=griffin-prod-vpc \
    --allow=tcp:22 \
    --source-ranges=0.0.0.0/0

# 3. Create the Bastion Host with dual network interfaces
gcloud compute instances create bastion \
    --zone=$ZONE \
    --machine-type=e2-medium \
    --network-interface=network=griffin-dev-vpc,subnet=griffin-dev-mgmt \
    --network-interface=network=griffin-prod-vpc,subnet=griffin-prod-mgmt
```

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 4. Create and configure Cloud SQL Instance
1. Create a MySQL Cloud SQL Instance called `griffin-dev-db` in `europe-west1`.
2. Connect to the instance and run the following SQL commands to prepare the `WordPress` environment:
```
CREATE DATABASE wordpress;
CREATE USER "wp_user"@"%" IDENTIFIED BY "stormwind_rules";
GRANT ALL PRIVILEGES ON wordpress.* TO "wp_user"@"%";
FLUSH PRIVILEGES;
```
These SQL statements create the worpdress database and create a user with access to the wordpress database.

You will use the username and password in task 6.


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


**Note:** Creating a Cloud SQL instance takes **5-10 minutes**. Start this command immediately.

```bash
gcloud sql instances create griffin-dev-db \
    --tier=db-f1-micro \
    --region=$REGION
```

To run the SQL commands, you first need to set a password for the `root` user, then connect to the database.

**1. Set the root password:**
```bash
gcloud sql users set-password root \
    --host=% \
    --instance=griffin-dev-db \
    --password=root_password_123
```

**2. Connect to the database:**
Run this command. When asked for the password, type `root_password_123`.
```bash
gcloud sql connect griffin-dev-db --user=root
```
*(It may take a minute to allow your IP address).*

**3. Once you see the `mysql>` prompt, paste this block exactly:**

```sql
CREATE DATABASE wordpress;
CREATE USER "wp_user"@"%" IDENTIFIED BY "stormwind_rules";
GRANT ALL PRIVILEGES ON wordpress.* TO "wp_user"@"%";
FLUSH PRIVILEGES;
EXIT;
```


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 5. Create Kubernetes cluster
- Create a 2 node cluster (e2-standard-4) called `griffin-dev`, in the `griffin-dev-wp` subnet, and in zone `europe-west1-c`.


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

This creates the cluster `griffin-dev` inside the `griffin-dev-vpc` network.

```bash
gcloud container clusters create griffin-dev \
    --zone=europe-west1-c \
    --network=griffin-dev-vpc \
    --subnetwork=griffin-dev-wp \
    --machine-type=e2-standard-4 \
    --num-nodes=2
```

*(This usually takes 3-5 minutes to provision).*

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 6. Prepare the Kubernetes cluster
1. From Cloud Shell copy all files from `gs://spls/gsp321/wp-k8s`.

The `WordPress` server needs to access the MySQL database using the username and password you created in task 4.

2. You do this by setting the values as secrets. WordPress also needs to store its working files outside the container, so you need to create a volume.

3. Add the following secrets and volume to the cluster using `wp-env.yaml`.

4. Make sure you configure the username to `wp_user` and password to `stormwind_rules` before creating the configuration.

You also need to provide a key for a service account that was already set up. This service account provides access to the database for a sidecar container.

5. Use the command below to create the key, and then add the key to the Kubernetes environment:

```
gcloud iam service-accounts keys create key.json \
    --iam-account=cloud-sql-proxy@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com
kubectl create secret generic cloudsql-instance-credentials \
    --from-file key.json
```


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Run these commands in order:

**1. Connect to your cluster and download the files**
```bash
# Get credentials to ensure kubectl is pointing to the right cluster
gcloud container clusters get-credentials griffin-dev --zone=europe-west1-c

# Copy the lab files
cd ~
gsutil -m cp -r gs://spls/gsp321/wp-k8s .

# Enter the directory
cd wp-k8s
```

**2. Configure and Apply the `wp-env.yaml` (Secrets & Volume)**
This block modifies the file to inject the `wp_user` and `stormwind_rules` password, then applies it to the cluster.

```bash
# Inject username
sed -i 's/username: .*/username: wp_user/' wp-env.yaml

# Inject password
sed -i 's/password: .*/password: stormwind_rules/' wp-env.yaml

# Apply the configuration to the cluster
kubectl apply -f wp-env.yaml
```

**3. Create the Service Account Key and K8s Secret**
This allows the "sidecar" container to talk to Cloud SQL securely.

```bash
# Create the Service Account Key
gcloud iam service-accounts keys create key.json \
    --iam-account=cloud-sql-proxy@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com

# Create the Kubernetes secret using that key
kubectl create secret generic cloudsql-instance-credentials \
    --from-file key.json
```

**Verify success:**
Run `kubectl get secrets`. You should see `cloudsql-db-credentials` and `cloudsql-instance-credentials` in the list.

---

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 7. Create a WordPress deployment

Now that you have provisioned the MySQL database, and set up the secrets and volume, you can create the deployment using `wp-deployment.yaml`.

1. Before you create the deployment you need to edit `wp-deployment.yaml`.

2. Replace `YOUR_SQL_INSTANCE` with griffin-dev-db's *Instance connection name*.

3. Get the Instance connection name from your Cloud SQL instance.

4. After you create your WordPress deployment, create the service with `wp-service.yaml`.

5. Once the Load Balancer is created, you can visit the site and ensure you see the WordPress site installer.
At this point the dev team will take over and complete the install and you move on to the next task.


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Make sure you are still in the `~/wp-k8s` directory.

**1. Configure and apply the Deployment**

```bash
# Get the Cloud SQL Connection Name into a variable
export SQL_CONNECTION=$(gcloud sql instances describe griffin-dev-db --format="value(connectionName)")

# Replace the placeholder in the YAML file
sed -i "s/YOUR_SQL_INSTANCE/$SQL_CONNECTION/g" wp-deployment.yaml

# Create the deployment
kubectl apply -f wp-deployment.yaml
```

**2. Create the Service (Load Balancer)**

```bash
kubectl apply -f wp-service.yaml
```

**3. Verify the setup**
Run the following command and wait for the **EXTERNAL-IP** to change from `<pending>` to a real IP address.

```bash
kubectl get svc -w
```

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 8. Enable monitoring
- Create an uptime check for your WordPress development site.


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

For **Task 8**, we need to create an Uptime Check. We can do this via the command line by extracting the External IP of your WordPress service.

**1. Capture the External IP**
Run this to save your Load Balancer IP into a variable.
*Note: If this returns nothing or `<pending>`, wait a minute and try again.*
```bash
export WP_IP=$(kubectl get svc wordpress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Your WordPress IP is: $WP_IP"
```

**2. Create the Uptime Check**
Once you see an IP address printed above, run this command:

```bash
gcloud monitoring uptime-check-configs create wordpress-uptime-check \
  --display-name="WordPress Uptime Check" \
  --resource-type=uptime_url \
  --resource-labels=host=$WP_IP,project=$GOOGLE_CLOUD_PROJECT \
  --http-check-path="/" \
  --period=1
```

*(If the command fails or you prefer the Console: Go to **Monitoring > Uptime checks**, click **Create Uptime Check**, enter "WordPress Uptime Check" as the title, and enter the IP address ($WP_IP) as the **Hostname**).*


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

I apologize for that error. The `uptime-check-configs` command is sometimes restricted to the `alpha` or `beta` component in certain Cloud Shell environments, or the syntax changes frequently.

To ensure you pass this check quickly without debugging the CLI tools, **please use the Google Cloud Console** for this specific task. It is fast and reliable.

### **Manual Steps for Task 8 (Monitoring)**

1.  In the Google Cloud Console, search for **"Monitoring"** in the top search bar and select **Monitoring**.
2.  In the left menu, click **Uptime checks**.
3.  Click **+ CREATE UPTIME CHECK** (top of the page).
4.  **Target:**
    *   **Protocol:** HTTP
    *   **Resource Type:** URL
    *   **Hostname:** Paste the **External IP** of your WordPress service (the one you saw in Task 7).
    *   **Path:** `/`
5.  **Friendly Name:** Enter `WordPress Uptime Check`.
6.  Click **Next**, then **Next** again (leave defaults).
7.  Click **Create**.

---

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Task 9. Provide access for an additional engineer
- You have an additional engineer starting and you want to ensure they have access to the project. Grant them the editor role to the project.

The second user account is student-01-24b5fa1c4e10@qwiklabs.net


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

gcloud projects add-iam-
policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="user:student-01-24b5fa1c4e10@qwiklabs.net" \
    --role="roles/editor"

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
