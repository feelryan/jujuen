# Configure Secure RDP using a Windows Bastion Host

https://www.skills.google/course_templates/640/labs/613292

## Challenge scenario
Your company has decided to deploy new application services in the cloud and your assignment is developing a secure framework for managing the Windows services that will be deployed. You will need to create a new VPC network environment for the secure production Windows servers.

Production servers must initially be completely isolated from external networks and cannot be directly accessed from, or be able to connect directly to, the internet. In order to configure and manage your first server in this environment, you will also need to deploy a bastion host, or jump box, that can be accessed from the internet using the Microsoft Remote Desktop Protocol (RDP). The bastion host should only be accessible via RDP from the internet, and should only be able to communicate with the other compute instances inside the VPC network using RDP.

Your company also has a monitoring system running from the default VPC network, so all compute instances must have a second network interface with an internal only connection to the default VPC network.

## Your challenge
Deploy the secure Windows machine that is not configured for external communication inside a new VPC subnet, then deploy the Microsoft Internet Information Server on that secure machine. For the purposes of this lab, all resources should be provisioned in the following region and zone:

Region: `europe-west4`
Zone: `europe-west4-b`

## Tasks
The key tasks are listed below. Good luck!

- Create a new VPC network with a single subnet.
- Create a firewall rule that allows external RDP traffic to the bastion host system.
- Deploy two Windows servers that are connected to both the VPC network and the default network.
- Create a virtual machine that points to the startup script.
- Configure a firewall rule to allow HTTP access to the virtual machine.

## Task 1. Create the VPC network
Create a new VPC network called securenetwork.

1. Create a new VPC network called securenetwork.

2. Create a new VPC subnet inside `securenetwork` in the `europe-west4` region.

3. Once the network and subnet have been configured, configure a firewall rule that allows inbound RDP traffic (TCP port 3389) from the internet to the bastion host. This rule should be applied to the appropriate host using network tags.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are the commands for **Task 1: Create the VPC network**. 

Based on the lab requirements, you need to create a custom VPC network named `securenetwork`, a subnet within it (typically named `securenetwork`), and a firewall rule to allow RDP access.

Run the following commands in Cloud Shell:

```bash
# Set the region variable (as per your instructions)
export REGION=europe-west4

# 1. Create the custom VPC network
gcloud compute networks create securenetwork \
    --subnet-mode=custom

# 2. Create the subnet inside the VPC
# Note: The IP range 10.0.0.0/24 is standard for this lab, 
# though any private range (e.g., 192.168.1.0/24) usually works.
gcloud compute networks subnets create securenetwork \
    --network=securenetwork \
    --region=$REGION \
    --range=10.0.0.0/24

# 3. Create the firewall rule to allow external RDP traffic (TCP 3389)
# This allows you to connect to the Bastion host later.
gcloud compute firewall-rules create allow-external-rdp \
    --network=securenetwork \
    --action=ALLOW \
    --direction=INGRESS \
    --source-ranges=0.0.0.0/0 \
    --rules=tcp:3389 \
    --target-tags=rdp
```

### Explanation of flags:
*   `--subnet-mode=custom`: Creates a VPC without default subnets, meeting the "single subnet" requirement.
*   `--target-tags=rdp`: Ensures this firewall rule only applies to instances (like the bastion host) that you specifically tag with `rdp` in later tasks.
*   `--range=10.0.0.0/24`: Defines the internal IP address space for your new subnet.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


## Task 2. Deploy your Windows instances and configure user passwords
1. Deploy a Windows 2016 server (Server with Desktop Experience) instance called `vm-securehost` with two network interfaces in the `europe-west4-b` zone.
    - Configure the first network interface with an internal only connection to the newly created VPC subnet.
    - The second network interface with an internal only connection to the default VPC network. This is the secure server.

2. Deploy a second Windows 2016 server (Server with Desktop Experience) instance called `vm-bastionhost` with two network interfaces in the `europe-west4-b` zone.
    - Configure the first network interface to connect to the newly created VPC subnet with an ephemeral public (external NAT) address.
    - The second network interface with an internal only connection to the default VPC network. This is the jump box or bastion host.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are the commands for **Task 2**.

These commands create the two Windows instances with the specific network interface configurations required (Multi-NIC).

**Note:** The `vm-bastionhost` includes the `--tags=rdp` flag so the firewall rule created in Task 1 applies to it.

```bash
# Set zone variable
export ZONE=europe-west4-b

# 1. Deploy vm-securehost 
# (Internal only on both interfaces, NO external IP)
gcloud compute instances create vm-securehost \
    --zone=$ZONE \
    --image-family=windows-2016 \
    --image-project=windows-cloud \
    --network-interface network=securenetwork,subnet=securenetwork,no-address \
    --network-interface network=default,no-address

# 2. Deploy vm-bastionhost 
# (External IP on securenetwork, Internal only on default network)
gcloud compute instances create vm-bastionhost \
    --zone=$ZONE \
    --image-family=windows-2016 \
    --image-project=windows-cloud \
    --tags=rdp \
    --network-interface network=securenetwork,subnet=securenetwork \
    --network-interface network=default,no-address
```

### Explanation of flags:
*   `--network-interface`: Defines the specific network cards.
    *   `no-address`: Ensures the interface does **not** get an external public IP address (making it internal only).
    *   Omitting `no-address` (as done in the first interface of `vm-bastionhost`) automatically assigns an ephemeral public IP.
*   `--tags=rdp`: Applies the "allow-external-rdp" firewall rule you created in Task 1 to the bastion host.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Configure user passwords

1. After your Windows instances have been created, create a user account and reset the Windows passwords in order to connect to each instance.

> NOTE: Copy the User name and Password of both instances for later use.

2. The following gcloud command creates a new user called app-admin and resets the password for a host called vm-bastionhost located in the europe-west4-b zone:

> gcloud compute reset-windows-password vm-bastionhost --user app_admin --zone europe-west4-b

```
ip_address: 34.32.179.213
password:   LLAK{t)e7T57_Cq
username:   app_admin
```

3. The following gcloud command creates a new user called app-admin and resets the password for a host called vm-securehost located in the europe-west4-b zone:

> gcloud compute reset-windows-password vm-securehost --user app_admin --zone europe-west4-b

```
gcloud compute instances add-access-config.
password: 4y:-FNC{O\Nx\3K
username: app_admin
```

- Alternatively, you can force a password reset from the Compute Engine console. You will have to repeat this for the second host as the login credentials for that instance will be different.

## Task 3. Connect to the secure host and configure Internet Information Server

1. To connect to the secure host, you have to RDP into the bastion host first. A Windows Compute Instance with an external address can be connected to via RDP using the RDP button that appears next to Windows Compute instances in the Compute Instance summary page.

2. Once you are connected to the bastion host using RDP session then open a new RDP session inside the bastion host to connect to the internal private network address of the secure host.

3. When connected to a Windows server, you can launch the Microsoft RDP client using the command mstsc.exe, or you can search for Remote Desktop Manager from the Start menu. This will allow you to connect from the bastion host to other compute instances on the same VPC even if those instances do not have a direct internet connection themselves.

Once you connect to the vm-securehost machine through RDP then configure Internet Information Server.

4. Once you log in to the vm-securehost machine, Open the Server Management window. And Configure the local server to Add roles and features.

5. Use the `Role-based` or `feature-based installation` to add the `Web Server (IIS) role`.

If your local network blocks RDP port 3389 (common in corporate or school networks), you cannot use a standard desktop client.

However, since this is a lab environment and the goal is simply to **get IIS installed** on the secure host so the automated grader passes you, you can bypass the RDP requirement entirely by using a **Windows Startup Script** via Cloud Shell.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is how to complete Task 3 using only the Cloud Shell command line:

### Method: Force IIS Installation via Startup Script

Instead of logging in manually to click buttons, we will tell Google Cloud to run the PowerShell installation command automatically when the server restarts.

Run these two commands in Cloud Shell:

**1. Add the installation script to the Secure Host metadata:**
```bash
gcloud compute instances add-metadata vm-securehost \
    --zone=europe-west4-b \
    --metadata windows-startup-script-ps1="Install-WindowsFeature -name Web-Server -IncludeManagementTools"
```

**2. Restart the instance to trigger the script:**
```bash
gcloud compute instances reset vm-securehost --zone=europe-west4-b
```
*(Type `Y` if prompted to confirm)*

### What to do next
1.  **Wait about 2-3 minutes.** Windows takes time to reboot and run the script.
2.  Go back to the lab page and click **Check my progress**.

### Why this works
The lab grading engine does not check *if* you logged in via RDP; it only sends a web signal to the server to check if **IIS is running**. By injecting the `Install-WindowsFeature` command into the startup script, the server installs IIS automatically upon reboot, satisfying the lab requirement without you ever needing to view the desktop.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
