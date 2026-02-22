# Challenge Lab - Build Infrastructure with Terraform on Google Cloud

## Challenge scenario
You are a cloud engineer intern for a new startup. For your first project, your new boss has tasked you with creating infrastructure in a quick and efficient manner and generating a mechanism to keep track of it for future reference and changes. You have been directed to use Terraform to complete the project.

For this project, you will use Terraform to create, deploy, and keep track of infrastructure on the startup's preferred provider, Google Cloud. You will also need to import some mismanaged instances into your configuration and fix them.

In this lab, you will use Terraform to import and create multiple VM instances, a VPC network with two subnetworks, and a firewall rule for the VPC to allow connections between the two instances. You will also create a Cloud Storage bucket to host your remote backend.

## Task 1. Create the configuration files

1. In Cloud Shell, create your Terraform configuration files and a directory structure that resembles the following:

```
main.tf
variables.tf
modules/
└── instances
    ├── instances.tf
    ├── outputs.tf
    └── variables.tf
└── storage
    ├── storage.tf
    ├── outputs.tf
    └── variables.tf
```

2. Fill out the variables.tf files in the root directory and within the modules. Add three variables to each file: region, zone, and project_id. For their default values, use <us-west1>, <us-west1-b>, <qwiklabs-gcp-01-44f869a28f01>, and your Google Cloud Project ID.

3. Add the Terraform block and the Google Provider to the main.tf file. Verify the zone argument is added along with the project and region arguments in the Google Provider block.

4. Initialize Terraform.

### solution

This looks like a **structured setup** for a Terraform project on Google Cloud, leveraging **modules** for organization. Here's a step-by-step guide to complete the required files and actions.

## 1\. 🏗️ Create Directory and File Structure

You'll use the `mkdir` and `touch` commands in Cloud Shell to create the directory structure and files.

```bash
# Create the root files
touch main.tf variables.tf

# Create the modules directory
mkdir modules

# Create the 'instances' module directory and files
mkdir -p modules/instances
touch modules/instances/instances.tf \
      modules/instances/outputs.tf \
      modules/instances/variables.tf

# Create the 'storage' module directory and files
mkdir -p modules/storage
touch modules/storage/storage.tf \
      modules/storage/outputs.tf \
      modules/storage/variables.tf
```

-----

## 2\. 📝 Fill out `variables.tf` Files

You'll need to define the **project**, **region**, and **zone** variables in both the root directory and within each module. Since I don't have your specific lab values, I will use placeholders (`<GCP_REGION>`, `<GCP_ZONE>`, `<GCP_PROJECT_ID>`)—**you must replace these with your actual lab values.**

### **Root Directory `variables.tf`**

This file will hold the primary configuration variables.

```terraform
# variables.tf (Root Directory)

variable "project_id" {
  description = "The ID of the Google Cloud Project."
  type        = string
  default     = "<GCP_PROJECT_ID>" # REPLACE ME
}

variable "region" {
  description = "The Google Cloud region to deploy resources."
  type        = string
  default     = "<GCP_REGION>" # REPLACE ME (e.g., us-central1)
}

variable "zone" {
  description = "The Google Cloud zone to deploy zonal resources."
  type        = string
  default     = "<GCP_ZONE>" # REPLACE ME (e.g., us-central1-a)
}
```

### **Module `variables.tf` Files**

The module files will reference the variables defined in the root directory or allow for overrides. For simplicity and to satisfy the requirement, we'll define them here similarly, but in a real-world scenario, you'd pass these values *into* the module from the root `main.tf`.

#### **`modules/instances/variables.tf`**

```terraform
# modules/instances/variables.tf

variable "project_id" {
  description = "The ID of the Google Cloud Project."
  type        = string
  default     = "<GCP_PROJECT_ID>" # REPLACE ME
}

variable "region" {
  description = "The Google Cloud region."
  type        = string
  default     = "<GCP_REGION>" # REPLACE ME
}

variable "zone" {
  description = "The Google Cloud zone."
  type        = string
  default     = "<GCP_ZONE>" # REPLACE ME
}
```

#### **`modules/storage/variables.tf`**

```terraform
# modules/storage/variables.tf

variable "project_id" {
  description = "The ID of the Google Cloud Project."
  type        = string
  default     = "<GCP_PROJECT_ID>" # REPLACE ME
}

variable "region" {
  description = "The Google Cloud region."
  type        = string
  default     = "<GCP_REGION>" # REPLACE ME
}

variable "zone" {
  description = "The Google Cloud zone."
  type        = string
  default     = "<GCP_ZONE>" # REPLACE ME
}
```

-----

## 3\. ⚙️ Add Terraform Block and Provider to `main.tf`

This file defines the required Terraform version, the **Google Provider**, and passes the variables to the provider configuration.

### **Root Directory `main.tf`**

```terraform
# main.tf (Root Directory)

# 1. Terraform Block
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  # This block is required for managing state in a persistent location
  # backend "gcs" {
  #   bucket = "tf-state-bucket-unique-name" # Replace with a unique bucket name
  # }
}

# 2. Google Provider Block
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Add a simple resource to keep the linter happy (optional, but good practice)
# You can remove this when you add your modules.
/*
resource "google_compute_network" "vpc_network" {
  name = "terraform-network"
  auto_create_subnetworks = true
}
*/
```

-----

## 4\. 🚀 Initialize Terraform

After creating and saving all the files, you can initialize Terraform in the root directory of your project (where `main.tf` is located).

```bash
terraform init
```


## Task 2. Import infrastructure

1. In the Google Cloud Console, on the Navigation menu, click Compute Engine > VM Instances. Two instances named tf-instance-1 and tf-instance-2 have already been created for you.

```
Note: by clicking on one of the instances, you can find its Instance ID, boot disk image, and machine type. These are all necessary for writing the configurations correctly and importing them into Terraform.
```

2. Import the existing instances into the instances module. To do this, you will need to follow these steps:

- First, add the module reference into the main.tf file then re-initialize Terraform.
- Next, write the resource configurations in the instances.tf file to match the pre-existing instances.
    * Name your instances tf-instance-1 and tf-instance-2.
    * For the purposes of this lab, the resource configuration should be as minimal as possible. To accomplish this, you will only need to include the following additional arguments in your configuration: machine_type, boot_disk, network_interface, metadata_startup_script, and allow_stopping_for_update. For the last two arguments, use the following configuration as this will ensure you won't need to recreate it:

    ```
    metadata_startup_script = <<-EOT
            #!/bin/bash
        EOT
    allow_stopping_for_update = true
    ```

- Once you have written the resource configurations within the module, use the terraform import command to import them into your instances module.

3. Apply your changes. Note that since you did not fill out all of the arguments in the entire configuration, the apply will update the instances in-place. This is fine for lab purposes, but in a production environment, you should make sure to fill out all of the arguments correctly before importing.

### task2 - solution

That's a great next step\! You're moving into **Terraform State Management** by using the `import` feature, which is essential for bringing existing cloud resources under Terraform's control.

Here is the plan to import the two Compute Engine instances into your `instances` module.

## 1\. ⚙️ Reference the Module and Re-initialize

### A. Update `main.tf`

Add the module block in your root `main.tf` file. This tells Terraform to look inside the `modules/instances` directory when executing.

```terraform
# main.tf (Root Directory) - ADD THIS BLOCK

# ... (Provider and Terraform blocks from previous task are here)

module "instances" {
  source = "./modules/instances"

  # Pass the root variables into the module
  project_id = var.project_id
  region     = var.region
  zone       = var.zone
}
```

### B. Re-initialize Terraform

Since you've added a new module reference, you must re-initialize Terraform so it can discover and load the module configuration.

```bash
terraform init
```

-----

## 2\. 📝 Write the Resource Configuration

You need to write the configuration for the two instances in the `modules/instances/instances.tf` file. You must get the **Instance ID**, **Machine Type**, and **Boot Disk Image** from the Google Cloud Console for the existing instances (`tf-instance-1` and `tf-instance-2`).

### A. Template for `modules/instances/instances.tf`

Replace the placeholders (`<MACHINE_TYPE>` and `<BOOT_DISK_IMAGE>`) with the actual values you retrieve from the Cloud Console.

```terraform
# modules/instances/instances.tf

data "google_compute_subnetwork" "default" {
  name   = "default"
  region = var.region
}

resource "google_compute_instance" "tf_instance_1" {
  # Required argument for import
  name         = "tf-instance-1"
  project      = var.project_id
  zone         = var.zone

  # Configuration arguments required by the prompt
  machine_type = "e2-micro" # e.g., e2-micro
  
  boot_disk {
    initialize_params {
      image = "debian-11-bullseye-v20251111" # e.g., debian-cloud/debian-11
    }
  }

  network_interface {
    network    = "default"
    subnetwork = data.google_compute_subnetwork.default.self_link
    access_config {
      # This block creates an external IP address
    }
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
  EOT
  allow_stopping_for_update = true
}

resource "google_compute_instance" "tf_instance_2" {
  # Required argument for import
  name         = "tf-instance-2"
  project      = var.project_id
  zone         = var.zone

  # Configuration arguments required by the prompt
  machine_type = "e2-micro" # e.g., e2-small
  
  boot_disk {
    initialize_params {
      image = "debian-11-bullseye-v20251111" # e.g., debian-cloud/debian-11
    }
  }

  network_interface {
    network    = "default"
    subnetwork = data.google_compute_subnetwork.default.self_link
    access_config {
      # This block creates an external IP address
    }
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
  EOT
  allow_stopping_for_update = true
}
```

### B. Import the Instances

The `terraform import` command uses the format:

```bash
terraform import <MODULE_REFERENCE>.<RESOURCE_TYPE>.<RESOURCE_NAME> <GCP_RESOURCE_ID>
```

For Google Compute Engine instances, the **GCP Resource ID** is typically formatted as: `projects/<PROJECT_ID>/zones/<ZONE>/instances/<INSTANCE_NAME>`. Since you're importing into a module, the module reference is critical.

**Import Instance 1:**

```bash
terraform import module.instances.google_compute_instance.tf_instance_1 projects/${YOUR_PROJECT_ID}/zones/${YOUR_ZONE}/instances/tf-instance-1
```

> terraform import module.instances.google_compute_instance.tf_instance_1 projects/qwiklabs-gcp-01-44f869a28f01/zones/us-west1-b/instances/tf-instance-1


**Import Instance 2:**

```bash
terraform import module.instances.google_compute_instance.tf_instance_2 projects/${YOUR_PROJECT_ID}/zones/${YOUR_ZONE}/instances/tf-instance-2
```

> terraform import module.instances.google_compute_instance.tf_instance_2 projects/qwiklabs-gcp-01-44f869a28f01/zones/us-west1-b/instances/tf-instance-2


> **Note:** Replace `${YOUR_PROJECT_ID}` and `${YOUR_ZONE}` with your actual lab values.

-----

## 3\. ✅ Apply Your Changes

After successfully importing, the existing instances are now tracked in your Terraform state. The final step is to run `terraform apply`. This will compare the minimal configuration you wrote in `instances.tf` with the actual state of the resources and attempt to apply the missing or different arguments (`metadata_startup_script` and `allow_stopping_for_update`).

```bash
terraform apply
```

Review the plan that is displayed. It should show that the existing instances will be updated (modified in-place) to match your minimal configuration. Type `yes` when prompted to confirm the application.

## Task 3. Configure a remote backend

1. Create a Cloud Storage bucket resource inside the storage module. For the bucket name, use <Bucket Name>. For the rest of the arguments, you can simply use:

location = "US"
force_destroy = true
uniform_bucket_level_access = true

> Note: You can optionally add output values inside of the outputs.tf file.

2. Add the module reference to the main.tf file. Initialize the module and apply the changes to create the bucket using Terraform.

3. Configure this storage bucket as the remote backend inside the main.tf file. Be sure to use the prefix terraform/state so it can be graded successfully.

4. If you've written the configuration correctly, upon init, Terraform will ask whether you want to copy the existing state data to the new backend. Type yes at the prompt.

### task3 - solution

This task involves creating the Google Cloud Storage (GCS) bucket, which will then be used to host your **Terraform state file**—a critical step for managing infrastructure in a team environment.

Make sure to replace `<Bucket Name>` with a globally unique name (e.g., `tf-state-bucket-your-project-id`).

## 1\. 📝 Configure the Storage Module

First, update the `storage` module's configuration files to define the bucket and accept the bucket name.

### A. Update `modules/storage/variables.tf`

Add the `bucket_name` variable to the existing variables (`project_id`, `region`, `zone`):

```terraform
# modules/storage/variables.tf (ADD THIS)

variable "bucket_name" {
  description = "The globally unique name for the GCS state backend bucket."
  type        = string
  default     = "tf-bucket-378555"
}

# (Existing project_id, region, and zone variables are also in this file)
```

### B. Update `modules/storage/storage.tf`

Create the `google_storage_bucket` resource using the required arguments.

```terraform
# modules/storage/storage.tf

resource "google_storage_bucket" "state_bucket" {
  name                        = var.bucket_name
  project                     = var.project_id
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}
```

-----

## 2\. ⚙️ Reference the Module and Create the Bucket

### A. Update Root `variables.tf`

Define the bucket name variable in your root directory so it can be passed into the module.

```terraform
# variables.tf (Root Directory - ADD THIS TO YOUR EXISTING VARIABLES)

variable "bucket_name" {
  description = "The globally unique name for the GCS state backend bucket."
  type        = string
  default     = "<Bucket Name>" # 👈 REPLACE ME with your UNIQUE bucket name
}

# (Existing project_id, region, and zone variables are also in this file)
```

### B. Update Root `main.tf`

Add the `storage` module reference and pass the necessary variables.

```terraform
# main.tf (Root Directory - ADD THIS BLOCK)

# ... (Existing 'instances' module block is here)

module "storage" {
  source = "./modules/storage"

  # Pass the root variables into the module
  project_id  = var.project_id
  region      = var.region
  zone        = var.zone
  bucket_name = var.bucket_name
}
```

### C. Initialize and Apply

Since you added a new module, re-initialize Terraform, then apply the configuration to create the bucket.

```bash
# Re-initialize to discover the new module
terraform init

# Apply to create the Google Cloud Storage bucket
terraform apply
```

Type `yes` to confirm the plan and create the bucket.

-----

## 3\. ☁️ Configure Remote Backend

Now that the bucket is created, you can configure Terraform to use it for state storage.

### A. Update Root `main.tf`

Modify the `terraform` block in your root `main.tf` to use the `gcs` backend. **Important:** The `backend` block cannot use variables, so you must hardcode the `<Bucket Name>` you used in the previous step.

```terraform
# main.tf (Root Directory - MODIFY THE TERRAFORM BLOCK)

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # 👈 ADD/MODIFY THIS BACKEND BLOCK
  backend "gcs" {
    bucket = "<Bucket Name>" # 👈 Hardcode your unique bucket name here!
    prefix = "terraform/state"
  }
}

# ... (The rest of main.tf, including provider and module blocks, remains below)
```

### B. Re-initialize and Migrate State

Run `terraform init` again. Terraform will detect the change to the backend configuration and ask if you want to migrate your local state file (`terraform.tfstate`) to the newly configured remote backend.

```bash
terraform init
```

When prompted, type **`yes`** to copy the existing state data to the GCS bucket at the path `gs://<Bucket Name>/terraform/state/default.tfstate`.

## Task 4. Modify and update infrastructure

1. Navigate to the instances module and modify the tf-instance-1 resource to use an e2-standard-2 machine type.

2. Modify the tf-instance-2 resource to use an e2-standard-2 machine type.

3. Add a third instance resource and name it <Instance Name>. For this third resource, use an e2-standard-2 machine type. Make sure to change the machine type to e2-standard-2 to all the three instances.

4. Initialize Terraform and apply your changes.

> Note: Optionally, you can add output values from these resources in the outputs.tf file within the module.

### task 4 - solution

This task involves modifying the existing instances and adding a new one, all while updating the machine type to **`e2-standard-2`**.

Here are the steps to modify your `instances` module and apply the changes.

## 1\. ✍️ Modify `modules/instances/instances.tf`

You need to update the configuration for `tf_instance_1` and `tf_instance_2` and add the new third instance (`<Instance Name>`).

Make sure to replace `<Instance Name>` with a unique name for the third instance. The machine type for all three should be set to **`e2-standard-2`**. You will also need to reuse the boot disk image from your existing imports.

```terraform
# modules/instances/instances.tf (Modified Content)

# 1. Modify tf-instance-1 to e2-standard-2
resource "google_compute_instance" "tf_instance_1" {
  name         = "tf-instance-1"
  project      = var.project_id
  zone         = var.zone

  # 👈 MODIFIED: Change machine_type to e2-standard-2
  machine_type = "e2-standard-2" 
  
  boot_disk {
    initialize_params {
      image = "<BOOT_DISK_IMAGE_1>" # Reuse the image from your import
    }
  }

  network_interface {
    network    = "default"
    subnetwork = "regions/${var.region}/subnetworks/default"
    access_config {
      # This block creates an external IP address
    }
  }
  
  metadata_startup_script = <<-EOT
            #!/bin/bash
        EOT
        
  allow_stopping_for_update = true
}

# 2. Modify tf-instance-2 to e2-standard-2
resource "google_compute_instance" "tf_instance_2" {
  name         = "tf-instance-2"
  project      = var.project_id
  zone         = var.zone

  # 👈 MODIFIED: Change machine_type to e2-standard-2
  machine_type = "e2-standard-2" 
  
  boot_disk {
    initialize_params {
      image = "<BOOT_DISK_IMAGE_2>" # Reuse the image from your import
    }
  }

  network_interface {
    network    = "default"
    subnetwork = "regions/${var.region}/subnetworks/default"
    access_config {
      # This block creates an external IP address
    }
  }
  
  metadata_startup_script = <<-EOT
            #!/bin/bash
        EOT
        
  allow_stopping_for_update = true
}

# 3. Add the third instance
resource "google_compute_instance" "new_instance" {
  # 👈 NEW INSTANCE
  name         = "<Instance Name>" # 👈 REPLACE ME (e.g., tf-instance-3)
  project      = var.project_id
  zone         = var.zone
  
  machine_type = "e2-standard-2"
  
  boot_disk {
    initialize_params {
      # You can reuse one of the boot disk images or a general one like debian-cloud/debian-11
      image = "<BOOT_DISK_IMAGE_FOR_NEW_INSTANCE>" 
    }
  }

  network_interface {
    network    = "default"
    subnetwork = "regions/${var.region}/subnetworks/default"
    access_config {
      # This block creates an external IP address
    }
  }
  
  metadata_startup_script = <<-EOT
            #!/bin/bash
        EOT
        
  allow_stopping_for_update = true
}
```

-----

## 2\. 🚀 Initialize and Apply Changes

Since you only modified files within an existing module and did not change the root `main.tf` configuration (or the backend configuration), you do not need to run `terraform init` unless you made changes to the module's input variables or the provider block. However, running it is safe.

1.  **Initialize Terraform (if necessary, or for safety):**

    ```bash
    terraform init
    ```

    *If you correctly configured the GCS backend in Task 3, this will confirm you are still using the remote state.*

2.  **Apply the Changes:**

    This command will:

      * **Modify** `tf-instance-1` and `tf-instance-2` by updating their machine type to **`e2-standard-2`**. Since the instance is being updated and not recreated, Terraform will stop the instance, change the machine type, and then restart it.
      * **Create** the new instance resource (`new_instance`) with the name `<Instance Name>` and the `e2-standard-2` machine type.

    <!-- end list -->

    ```bash
    terraform apply
    ```

Review the plan carefully. You should see:

  * **`~ resource "google_compute_instance" "tf_instance_1"`**: 1 to change (update in-place)
  * **`~ resource "google_compute_instance" "tf_instance_2"`**: 1 to change (update in-place)
  * **`+ resource "google_compute_instance" "new_instance"`**: 1 to add

Type **`yes`** to confirm the application and complete Task 4.

## Task 5. Destroy resources

1. Destroy the third instance <Instance Name> by removing the resource from the configuration file. After removing it, initialize terraform and apply the changes.

### task 5 - solution

This final task involves modifying your configuration to explicitly remove the third instance, which tells Terraform to **destroy** the corresponding cloud resource.

## 1\. 🗑️ Remove the Resource from the Configuration

Navigate to your `modules/instances/instances.tf` file and delete the configuration block for the third instance you added in Task 4.

### `modules/instances/instances.tf` (Updated Content)

You will remove the block that looks like this (using `new_instance` as the example name):

```terraform
# DELETE this entire block:
/*
resource "google_compute_instance" "new_instance" {
  name         = "<Instance Name>" # e.g., tf-instance-3
  project      = var.project_id
  zone         = var.zone
  
  machine_type = "e2-standard-2"
  
  boot_disk {
    initialize_params {
      image = "<BOOT_DISK_IMAGE_FOR_NEW_INSTANCE>" 
    }
  }

  network_interface {
    network    = "default"
    subnetwork = "regions/${var.region}/subnetworks/default"
    access_config {
      # This block creates an external IP address
    }
  }
  
  metadata_startup_script = <<-EOT
            #!/bin/bash
        EOT
        
  allow_stopping_for_update = true
}
*/
```

Your `instances.tf` file should now only contain the configuration for `tf-instance-1` and `tf-instance-2`.

-----

## 2\. 🚀 Initialize and Apply Changes

Removing the resource block signals to Terraform that the resource is no longer desired and should be destroyed.

1.  **Initialize Terraform (Optional):**
    Running `terraform init` is not strictly necessary since only a resource within an existing module was modified, but it's always safe to run.

    ```bash
    terraform init
    ```

2.  **Apply the Changes to Destroy the Instance:**
    Run `terraform apply`. Terraform will compare the current state (which still shows three instances) with the new configuration (which only has two instances) and identify the third instance for destruction.

    ```bash
    terraform apply
    ```

    Review the plan carefully. You should see:

      * **`- resource "google_compute_instance" "new_instance"`**: 1 to destroy.
      * **`Plan: 0 to add, 0 to change, 1 to destroy.`**

    Type **`yes`** to confirm and destroy the instance named `<Instance Name>` in Google Cloud.

-----

This completes the destruction task. Your infrastructure is now back to having only the two original instances, `tf-instance-1` and `tf-instance-2`, and your state file remains clean and up-to-date in your remote GCS backend.

## Task 6. Use a module from the Registry

1. In the Terraform Registry, browse to the Network Module.

2. Add this module to your main.tf file. Use the following configurations:

- Use version 10.0.0 (different versions might cause compatibility errors).
- Name the VPC <VPC Name>, and use a global routing mode.
- Specify 2 subnets in <the region>, and name them subnet-01 and subnet-02. For the subnets arguments, you just need the Name, IP, and Region.
- Use the IP 10.10.10.0/24 for subnet-01, and 10.10.20.0/24 for subnet-02.
- You do not need any secondary ranges or routes associated with this VPC, so you can omit them from the configuration.

3. Once you've written the module configuration, initialize Terraform and run an apply to create the networks.

4. Next, navigate to the instances.tf file and update the configuration resources to connect tf-instance-1 to subnet-01 and tf-instance-2 to subnet-02.

> Note: Within the instance configuration, you will need to update the network argument to <VPC Name>, and then add the subnetwork argument with the correct subnet for each instance.

### task 6 - solution

This task walks you through integrating a **pre-built, verified module** from the Terraform Registry, which is a common practice for reusing complex infrastructure configurations.

## 1\. 🔍 Find the Network Module

The official module you need is the **`google/network/google`** module in the Terraform Registry.

## 2\. 📝 Configure the Network Module in `main.tf`

You will add a new module block to your root `main.tf` file. You'll need to use your unique project ID, region variable, and a placeholder for the VPC name (`<VPC Name>`).

```terraform
# main.tf (Root Directory - ADD THIS BLOCK)

# ... (Existing 'instances' and 'storage' module blocks are here)

module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "10.0.0" # Required version

  project_id   = var.project_id
  network_name = "<VPC Name>" # 👈 REPLACE ME (e.g., tf-custom-vpc)
  routing_mode = "GLOBAL"     # Required routing mode

  # Define the two required subnets
  subnets = [
    {
      subnet_name   = "subnet-01"
      subnet_ip     = "10.10.10.0/24"
      subnet_region = var.region
    },
    {
      subnet_name   = "subnet-02"
      subnet_ip     = "10.10.20.0/24"
      subnet_region = var.region
    }
  ]
}
```

-----

## 3\. 🚀 Initialize and Apply to Create the VPC

Since you added a new module reference in `main.tf`, you must initialize Terraform again before applying.

1.  **Initialize Terraform:**

    ```bash
    terraform init
    ```

    This will download the external network module version 10.0.0.

2.  **Apply the Changes:**

    ```bash
    terraform apply
    ```

    Review the plan, which should show the creation of the new VPC network and two subnets. Type **`yes`** to confirm.

-----

## 4\. 🔗 Connect Instances to the New Subnets

Now that the VPC and subnets are created, you must modify your existing Compute Engine instances to use the new network instead of the default network. You'll need the VPC name you chose (`<VPC Name>`).

### Update `modules/instances/instances.tf`

Modify the `network_interface` block for both `tf_instance_1` and `tf_instance_2`.

```terraform
# modules/instances/instances.tf (MODIFIED network_interface blocks)

# --- tf-instance-1 ---
resource "google_compute_instance" "tf_instance_1" {
  # ... other arguments ...

  network_interface {
    # 👈 UPDATE: Change network from "default" to your new VPC
    network    = "<VPC Name>" 
    
    # 👈 ADD: Specify the target subnetwork
    subnetwork = "regions/${var.region}/subnetworks/subnet-01" 
    
    access_config {
      # This block creates an external IP address
    }
  }
  
  # ... other arguments ...
}

    ```
    network_interface {
        network    = var.network
        subnetwork = var.subnet_1
        access_config {
        # This block creates an external IP address
        }
    }
    ```

# --- tf-instance-2 ---
resource "google_compute_instance" "tf_instance_2" {
  # ... other arguments ...

  network_interface {
    # 👈 UPDATE: Change network from "default" to your new VPC
    network    = "<VPC Name>" 
    
    # 👈 ADD: Specify the target subnetwork
    subnetwork = "regions/${var.region}/subnetworks/subnet-02" 
    
    access_config {
      # This block creates an external IP address
    }
  }
  
  # ... other arguments ...
}

    ```
    network_interface {
        network    = var.network
        subnetwork = var.subnet_2
        access_config {
        # This block creates an external IP address
        }
    }
    ```
```

``` modules/instances/variables.tf
variable "network" {
  description = "The VPC network name."
  type        = string
}

variable "subnet_1" {
  description = "The self-link for the first subnet."
  type        = string
}

variable "subnet_2" {
  description = "The self-link for the second subnet."
  type        = string
}
```

## 5\. 🔄 Apply Final Changes

Run `terraform apply` one last time. This will detect that the network interfaces on the two existing instances are moving from the `default` network to the new custom VPC network.

```bash
terraform apply
```

Review the plan. It should show that both instances will be modified in-place to update their network interfaces. Type **`yes`** to confirm the application.

## Task 7. Configure a firewall

- Create a firewall rule resource in the main.tf file, and name it tf-firewall.
    * This firewall rule should permit the <VPC Name> network to allow ingress connections on all IP ranges (0.0.0.0/0) on TCP port 80.
    * Make sure you add the source_ranges argument with the correct IP range (0.0.0.0/0).
    * Initialize Terraform and apply your changes.

> Note: To retrieve the required network argument, you can inspect the state and find the ID or self_link of the google_compute_network resource you created. It will be in the form projects/PROJECT_ID/global/networks/<VPC Name>.

### task 7 - solution

This final configuration task involves creating a **Firewall Rule** to permit web traffic (HTTP on port 80) into your new custom Virtual Private Cloud (VPC).

Since the network resource was created using the `vpc` module, you can reference its output directly within the `main.tf` file to get the required network self-link, simplifying the process.

## 1\. 📝 Add Firewall Rule to `main.tf`

You will add the `google_compute_firewall` resource to your root `main.tf` file. You need the VPC name you used in the previous task (`<VPC Name>`).

The network link can be accessed using the module output, typically in the format: `module.vpc.network_self_link`.

```terraform
# main.tf (Root Directory - ADD THIS BLOCK)

# ... (All previous module blocks are here)

resource "google_compute_firewall" "tf_firewall" {
  name    = "tf-firewall"
  project = var.project_id
  
  # Reference the network created by the 'vpc' module
  network = module.vpc.network_self_link 

  # Define the rule to allow ingress connections (INCOMING)
  allow {
    protocol = "tcp"
    ports    = ["80"] # Allow HTTP traffic
  }

  # Apply the rule to traffic originating from any IP range
  source_ranges = ["0.0.0.0/0"] 
  
  # Since you are only allowing ingress, you must explicitly set direction
  direction = "INGRESS"
}
```

```
resource "google_compute_firewall" "tf_firewall" {
  name    = "tf-firewall"
  project = var.project_id
  network = module.vpc.network_name

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
}
```

-----

## 2\. 🚀 Initialize and Apply Changes

Since you only added a new resource definition in the root `main.tf` and did not change the backend or provider, you only need to run `terraform apply`. However, running `terraform init` is always a safe best practice after configuration changes.

1.  **Initialize Terraform (Optional, but recommended):**

    ```bash
    terraform init
    ```

2.  **Apply the Changes to Create the Firewall Rule:**

    ```bash
    terraform apply
    ```

    Review the plan. It should show **1 to add** (the `tf-firewall` resource). Type **`yes`** to confirm the application and create the firewall rule.

This completes the Challenge Lab tasks\! Your infrastructure now includes:

  * Two imported, updated VM instances (`tf-instance-1`, `tf-instance-2`).
  * A custom VPC network with two subnets.
  * A firewall rule allowing web traffic to the VPC.
  * A remote GCS backend for state management.