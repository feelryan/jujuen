Here is the step-by-step solution to the "Implement Load Balancing on Compute Engine" Challenge Lab. This solution synthesizes the specific requirements of the challenge with the procedural commands found in the provided tutorials.

### **Prerequisites: Configure Environment**

First, set the default region and zone to match the challenge requirements (`us-west3` and `us-west3-b`).

```bash
gcloud config set compute/region us-west3
gcloud config set compute/zone us-west3-b
```

-----

### **Task 1: Create Multiple Web Server Instances**

You need to create three specific VMs (`web1`, `web2`, `web3`) with the tag `network-lb-tag` and install Apache.

**1. Create the three instances**
Run the following commands to create the instances with the required `e2-small` machine type and `debian-12` image.

```bash
# Create web1
gcloud compute instances create web1 \
  --zone=us-west3-b \
  --tags=network-lb-tag \
  --machine-type=e2-small \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install apache2 -y
    service apache2 restart
    echo "<h3>Web Server: web1</h3>" | tee /var/www/html/index.html'

# Create web2
gcloud compute instances create web2 \
  --zone=us-west3-b \
  --tags=network-lb-tag \
  --machine-type=e2-small \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install apache2 -y
    service apache2 restart
    echo "<h3>Web Server: web2</h3>" | tee /var/www/html/index.html'

# Create web3
gcloud compute instances create web3 \
  --zone=us-west3-b \
  --tags=network-lb-tag \
  --machine-type=e2-small \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install apache2 -y
    service apache2 restart
    echo "<h3>Web Server: web3</h3>" | tee /var/www/html/index.html'
```

**2. Create the firewall rule**
Allow external traffic to reach these instances on port 80.

```bash
gcloud compute firewall-rules create www-firewall-network-lb \
  --target-tags network-lb-tag --allow tcp:80
```

-----

### **Task 2: Configure the Network Load Balancer**

Now, set up the legacy Network Load Balancer to distribute traffic across the three VMs created above.

**1. Create a static external IP**
Reserve the IP address named `network-lb-ip-1`.

```bash
gcloud compute addresses create network-lb-ip-1 \
 --region us-west3
```

**2. Create a legacy health check**
This is required for the target pool to function.

```bash
gcloud compute http-health-checks create basic-check
```

**3. Create the target pool and add instances**
Create the pool `www-pool` and add your three instances to it.

```bash
gcloud compute target-pools create www-pool \
  --region us-west3 --http-health-check basic-check

gcloud compute target-pools add-instances www-pool \
  --instances web1,web2,web3
```

**4. Create the forwarding rule**
Route traffic from the static IP to the target pool.

```bash
gcloud compute forwarding-rules create www-rule \
  --region us-west3 \
  --ports 80 \
  --address network-lb-ip-1 \
  --target-pool www-pool
```

-----

### **Task 3: Create an HTTP Load Balancer**

This task involves creating a Managed Instance Group (MIG) and setting up a global HTTP Load Balancer.

**1. Create the Instance Template**
Create `lb-backend-template` using `e2-medium` and `debian-12`.

```bash
gcloud compute instance-templates create lb-backend-template \
   --region=us-west3 \
   --network=default \
   --subnet=default \
   --tags=allow-health-check \
   --machine-type=e2-medium \
   --image-family=debian-12 \
   --image-project=debian-cloud \
   --metadata=startup-script='#!/bin/bash
     apt-get update
     apt-get install apache2 -y
     a2ensite default-ssl
     a2enmod ssl
     vm_hostname="$(curl -H "Metadata-Flavor:Google" \
     http://169.254.169.254/computeMetadata/v1/instance/name)"
     echo "Page served from: $vm_hostname" | \
     tee /var/www/html/index.html
     systemctl restart apache2'
```

**2. Create the Managed Instance Group**
Create the group `lb-backend-group` with size 2.

```bash
gcloud compute instance-groups managed create lb-backend-group \
   --template=lb-backend-template --size=2 --zone=us-west3-b
```

**3. Create the Firewall Rule for Health Checks**
Create `fw-allow-health-check` to allow Google's health check systems to communicate with the backend.

```bash
gcloud compute firewall-rules create fw-allow-health-check \
  --network=default \
  --action=allow \
  --direction=ingress \
  --source-ranges=130.211.0.0/22,35.191.0.0/16 \
  --target-tags=allow-health-check \
  --rules=tcp:80
```

**4. Reserve a Global IP**
Create the IPv4 address `lb-ipv4-1`.

```bash
gcloud compute addresses create lb-ipv4-1 \
  --ip-version=IPV4 \
  --global
```

**5. Create the Health Check**
Create the `http-basic-check`.

```bash
gcloud compute health-checks create http http-basic-check \
  --port 80
```

**6. Create the Backend Service**
Create the backend service (we will name it `web-backend-service` to follow standard convention, though the challenge mentions "http-lb-proxy" which is technically the target proxy name).

```bash
gcloud compute backend-services create web-backend-service \
  --protocol=HTTP \
  --port-name=http \
  --health-checks=http-basic-check \
  --global
```

**7. Add the Instance Group to the Backend Service**
Link the MIG `lb-backend-group` to the service.

```bash
gcloud compute backend-services add-backend web-backend-service \
  --instance-group=lb-backend-group \
  --instance-group-zone=us-west3-b \
  --global
```

**8. Create the URL Map**
Create the map `web-map-http`.

```bash
gcloud compute url-maps create web-map-http \
  --default-service web-backend-service
```

**9. Create the Target HTTP Proxy**
Create the proxy `http-lb-proxy` pointing to the URL map.

```bash
gcloud compute target-http-proxies create http-lb-proxy \
  --url-map=web-map-http
```

**10. Create the Global Forwarding Rule**
Finally, wire the IP address to the proxy.

```bash
gcloud compute forwarding-rules create http-content-rule \
   --address=lb-ipv4-1 \
   --global \
   --target-http-proxy=http-lb-proxy \
   --ports=80
```

-----

### **Verification**

To verify the setup, retrieve the IP of the HTTP load balancer and test it.

```bash
# Get the IP address
gcloud compute addresses describe lb-ipv4-1 --format="get(address)" --global
```

Visit the IP address in your browser. It may take 5-7 minutes for the Global Load Balancer to propagate. You should see a page that says: `Page served from: lb-backend-group-xxxx`.
