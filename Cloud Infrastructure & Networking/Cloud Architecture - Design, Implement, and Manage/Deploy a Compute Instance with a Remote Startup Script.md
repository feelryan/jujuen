# Deploy a Compute Instance with a Remote Startup Script.md

https://www.skills.google/course_templates/640/labs/613291

## Challenge scenario
You have been given the responsibility of managing the configuration of your organization's Google Cloud virtual machines. You have decided to make some changes to the framework used for managing the deployment and configuration machines - you want to make it easier to modify the startup scripts used to initialize a number of the compute instances. Instead of storing startup scripts directly in the instances' metadata, you have decided to store the scripts in a Cloud Storage bucket and then configure the virtual machines to point to the relevant script file in the bucket.

A basic bash script that installs the Apache web server software called install-web.sh has been provided for you as a sample startup script. You can download this from the Student Resources links on the left side of the page. You can also find the startup script in a public Cloud Storage bucket at gs://spls/gsp301/install-web.sh.

## Your challenge
Configure a Linux Compute Engine instance that installs the Apache web server software using a remote startup script. In order to confirm that a compute instance Apache has successfully installed, the Compute Engine instance must be accessible via HTTP from the internet. You must create your instance in the following zone: `us-east4-b`.

> Note: In order to ensure accurate activity tracking you should not modify or change any of the pre-created lab resources, in particular the lab-monitor Compute Engine instance.

## Task 1. Create a storage bucket

Based on the challenge scenario and the specific requirements for **Task 1**, here are the commands to run in the Cloud Shell.

These commands will define the required region (derived from your assigned zone `us-east4-b`), create a uniquely named bucket using your Project ID, and copy the provided startup script into it.

### Commands for Task 1

```bash
# 1. Set the region variable based on the required zone (us-east4-b)
export REGION=us-east4

# 2. Create the storage bucket (using Project ID guarantees a unique name)
gcloud storage buckets create gs://$DEVSHELL_PROJECT_ID --location=$REGION

# 3. Copy the provided startup script from the public bucket to your new bucket
gcloud storage cp gs://spls/gsp301/install-web.sh gs://$DEVSHELL_PROJECT_ID/install-web.sh
```

**Explanation of what this does:**
*   **`export REGION=...`**: Sets the region to match the zone specified in your instructions.
*   **`gcloud storage buckets create...`**: Creates the bucket in the correct location. `$DEVSHELL_PROJECT_ID` is an environment variable automatically set in the Cloud Shell containing your active Project ID.
*   **`gcloud storage cp...`**: Downloads the `install-web.sh` file from the source provided in the lab description and uploads it to your bucket so it can be used by the VM in the next task.

## Task 2. Create a VM instance with a remote startup script

Here are the commands for **Task 2**.

This command creates the VM instance in the required zone, tags it to allow HTTP traffic, and points the metadata to the startup script you uploaded to your bucket in the previous task.

### Commands for Task 2

```bash
gcloud compute instances create my-instance \
  --zone=us-east4-b \
  --tags=http-server \
  --metadata=startup-script-url=gs://$DEVSHELL_PROJECT_ID/install-web.sh
```

### Explanation of the flags:
*   **`--zone=us-east4-b`**: Specifies the zone required by the challenge.
*   **`--tags=http-server`**: applies the network tag that allows traffic on Port 80 (HTTP), ensuring the server is accessible from the internet.
*   **`--metadata=startup-script-url=...`**: Configures the instance to pull the startup script from your Cloud Storage bucket instead of local metadata.

> **Note:** Providing the `--tags=http-server` flag usually relies on the `default-allow-http` firewall rule existing in the default network. If the lab environment does not have this rule pre-configured, you may need to run this command as well to open port 80:
> ```bash
> gcloud compute firewall-rules create default-allow-http \
>   --direction=INGRESS \
>   --priority=1000 \
>   --network=default \
>   --action=ALLOW \
>   --rules=tcp:80 \
>   --source-ranges=0.0.0.0/0 \
>   --target-tags=http-server
> ```

## Task 3. Create a firewall rule to allow traffic (80/tcp)

Here are the commands for **Task 3**.

This command creates an ingress firewall rule to allow TCP traffic on port 80 (HTTP) from any source to instances with the `http-server` tag.

### Commands for Task 3

```bash
gcloud compute firewall-rules create allow-http \
  --direction=INGRESS \
  --network=default \
  --action=ALLOW \
  --rules=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server
```

### Explanation of the flags:
*   **`--action=ALLOW`**: Configures the rule to permit the traffic.
*   **`--rules=tcp:80`**: Specifies that the rule applies to the TCP protocol on Port 80.
*   **`--source-ranges=0.0.0.0/0`**: Allows traffic from any IP address (the open internet).
*   **`--target-tags=http-server`**: Applies this rule only to VMs with the `http-server` tag (which you added to your VM in Task 2).

## Task 4. Test that the VM is serving web content



## Tips and tricks
Configure Instance Metadata. The [Running Startup Scripts](https://cloud.google.com/compute/docs/startupscript) documentation page explains how Compute Engine instance metadata can be used to configure startup scripts.
Check if your Compute Engine instance is executing the startup script. Use the Serial Console for the running virtual machine to look at the startup events to make sure that the startup script is being executed.
Check permissions. Your Compute Engine instance might not have the correct permissions required to read the startup script from the storage bucket. The virtual machine needs to be given permissions that align with the storage permissions.
Check firewalls. If the startup script has installed the software you may be unable to connect if a firewall has not been correctly configured.
Check the URL and address. You will be unable to connect to the Apache web server if you are trying to access the Compute Engine instance using an HTTPS address rather than HTTP; or you are using the incorrect IP address. Check that your URL is http://[EXTERNAL_IP] rather than https://[EXTERNAL_IP] or http://[INTERNAL_IP]