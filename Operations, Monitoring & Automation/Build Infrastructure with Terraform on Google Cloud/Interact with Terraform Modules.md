Here is the transcript of the video content:

**What is a Terraform module?**

A Terraform module is a set of Terraform configuration files in a single directory. Even a simple configuration consisting of a single directory with one or more `.tf` files is a module. When you run Terraform commands directly from such a directory, it is considered the **root module**. So in this sense, every Terraform configuration is part of a module. You may have a simple set of Terraform configuration files like this:

*   LICENSE
*   README.md
*   main.tf
*   variables.tf
*   outputs.tf

In this case, when you run Terraform commands from within the `minimal-module` directory, the contents of that directory are considered the root module.

**Calling modules**

Terraform commands only directly use the configuration files in one directory, which is usually the current working directory. However, your configuration can use module blocks to call modules in other directories. When Terraform encounters a module block, it loads and processes that module's configuration files.

A module that is called by another configuration is sometimes referred to as a "child module" of that configuration.

**Local and remote modules**

Modules can be loaded from either the local filesystem or a remote source. Terraform supports a variety of remote sources, including the Terraform Registry, most version control systems, HTTP URLs, and Terraform Cloud or Terraform Enterprise private module registries.

**Module best practices**

In many ways, Terraform modules are similar to the concepts of libraries, packages, or modules found in most programming languages, and they provide many of the same benefits. Just like almost any non-trivial computer program, real-world Terraform configurations should almost always use modules to provide the benefits mentioned above.

It is recommended that every Terraform practitioner use modules by following these best practices:

*   Start writing your configuration with a plan for modules. Even for slightly complex Terraform configurations managed by a single person, the benefits of using modules outweigh the time it takes to use them properly.
*   Use local modules to organize and encapsulate your code. Even if you aren't using or publishing remote modules, organizing your configuration in terms of modules from the beginning significantly reduces the burden of maintaining and updating your configuration as your infrastructure grows in complexity.
*   Use the public Terraform Registry to find useful modules. This way you can quickly and confidently implement your configuration by relying on the work of others.
*   Publish and share modules with your team. Most infrastructure is managed by a team of people, and modules are an important tool that teams can use to create and maintain infrastructure. As mentioned earlier, you can publish modules either publicly or privately. You explore how to do this in a later lab in this series.

**Task 1. Use modules from the Registry**

In this section, you use modules from the Terraform Registry to provision an example environment in Google Cloud. The concepts you use here are applicable to any modules from any source.

*   Open the Terraform Registry page for the Terraform Network module in a new browser tab or window. The page looks like this:

The page includes information about the module and a link to the source repository. The right side of the page includes a dropdown interface to select the module version and instructions for using the module to provision infrastructure.

When you call a module, the `source` argument is required. In this example, Terraform searches for a module in the Terraform Registry that matches the given string. You could also use a URL or local file path for the source of your modules. Refer to the Terraform documentation for a list of possible module sources.

The other argument shown here is the `version`. For supported sources, the version lets you define what version or versions of the module are loaded. In this lab, you specify an exact version number for the modules you use. You can read about more ways to specify versions in the module documentation.

Other arguments to module blocks are treated as input variables to the modules.

**Create a Terraform configuration**

1.  To start, run the following commands in Cloud Shell to clone the example simple project from the Google Terraform modules GitHub repository and switch to the `v6.0.1` branch:

    ```bash
    git clone https://github.com/terraform-google-modules/terraform-google-network
    cd terraform-google-network
    git checkout tags/v6.0.1 -b v6.0.1
    ```

    This ensures that you're using the correct version number.

2.  On the Cloud Shell toolbar, click **Open Editor**.

3.  In the Editor, navigate to `terraform-google-network/examples/simple_project`, and open the `main.tf` file. Your `main.tf` configuration should look like this:

    ```hcl
    module "test-vpc-module" {
      source       = "terraform-google-modules/network/google"
      version      = "~> 6.0"
      project_id   = var.project_id
      network_name = "my-custom-mode-network"
      mtu          = 1460

      subnets = [
        {
          subnet_name   = "subnet-01"
          subnet_ip     = "10.10.10.0/24"
          subnet_region = "us-west1"
        },
        {
          subnet_name           = "subnet-02"
          subnet_ip             = "10.10.20.0/24"
          subnet_region         = "us-west1"
          subnet_private_access = "true"
          subnet_flow_logs      = "true"
        },
        {
          subnet_name               = "subnet-03"
          subnet_ip                 = "10.10.30.0/24"
          subnet_region             = "us-west1"
          subnet_flow_logs          = "true"
          subnet_flow_logs_interval = "INTERVAL_10_MIN"
          subnet_flow_logs_sampling = 0.7
          subnet_flow_logs_metadata = "INCLUDE_ALL_METADATA"
          subnet_flow_logs_filter   = "false"
        }
      ]
    }
    ```

    This configuration includes one important block:

    *   `module "test-vpc-module"` defines a Virtual Private Cloud (VPC), which provides networking services for the rest of your infrastructure.

**Set values for module input variables**

Some input variables are required, which means that the module doesn't provide a default value; an explicit value must be provided in order for Terraform to run correctly.

*   Within the `module "test-vpc-module"` block, review the input variables you are setting. Each of these input variables is documented in the Terraform Registry. The required inputs for this module are:
    *   `network_name`: The name of the network being created
    *   `project_id`: The ID of the project where this VPC is created
    *   `subnets`: The list of subnets being created

In order to use most modules, you need to pass input variables to the module configuration. The configuration that calls a module is responsible for setting its input values, which are passed as arguments to the module block. Aside from `source` and `version`, most of the arguments to a module block set variable values.

On the Terraform Registry page for the Google Cloud network module, an **Inputs** tab describes all of the input variables that module supports.

**Enable Gemini Code Assist in the Cloud Shell IDE**

You can use Gemini Code Assist in an integrated development environment (IDE) such as Cloud Shell to receive guidance on code or solve problems with your code. Before you can start using Gemini Code Assist, you need to enable it.

1.  In Cloud Shell, enable the **Gemini for Google Cloud** API with the following command:

    ```bash
    gcloud services enable cloudaicompanion.googleapis.com
    ```

2.  Click **Open Editor** on the Cloud Shell toolbar.

    **Note:** To open the Cloud Shell Editor, click **Open Editor** on the Cloud Shell toolbar. You can switch between Cloud Shell and the code editor by clicking **Open Editor** or **Open Terminal**, as required.

3.  In the left pane, click the **Settings** icon, then in the **Settings** view, search for **Gemini Code Assist**.

4.  Locate and ensure that the checkbox is selected for **Geminicodeassist: Enable**, and close the **Settings**.

5.  Click **Cloud Code - No Project** in the status bar at the bottom of the screen.

6.  Authorize the plugin as instructed. If a project is not automatically selected, click **Select a Google Cloud Project**, and choose `qwiklabs-gcp-00-177abd52dfd9`.

7.  Verify that your Google Cloud project (`qwiklabs-gcp-00-177abd52dfd9`) displays in the Cloud Code status message in the status bar.

**Define root input variables**

Using input variables with modules is very similar to how you use variables in any Terraform configuration. A common pattern is to identify which module input variables you might want to change in the future, and then create matching variables in your configuration's `variables.tf` file with sensible default values. Those variables can then be passed to the module block as arguments.

To help you be more productive while minimizing context switching, Gemini Code Assist provides AI-powered smart actions directly in your code editor. In this section, you decide to use Gemini Code Assist help you make some updates to your Terraform code, such as configuring the variable block for a project resource to add a "default" argument to it, as well as other code changes.

1.  In the Cloud Shell Editor, still in the same directory, navigate to `variables.tf`.
    This action enables Gemini Code Assist, as indicated by the presence of the spark icon in the upper-right corner of the editor.

2.  Click the **Gemini Code Assist: Smart Actions** spark icon on the toolbar.

3.  To update the `default` argument for the `project_id` variable, paste the following prompt into the Gemini Code Assist inline text field that opens from the toolbar.

    ```text
    In the configuration file variables.tf, update the variable block "project_id" resource by adding a "default" argument. Set the value to qwiklabs-gcp-00-177abd52dfd9.
    ```

4.  To prompt Gemini to modify the code accordingly, press **ENTER**.

5.  When prompted in the **Gemini Diff** view, click **Accept**.

    The updated `default` argument for the `project_id` variable in the `variables.tf` configuration file now looks something like this:

    ```hcl
    variable "project_id" {
      description = "The project ID to host the network in"
      default     = "qwiklabs-gcp-00-177abd52dfd9"
    }
    ```

6.  You now want to let Gemini Code Assist help you define the variable `network_name` in the `variables.tf` file. You can use the name `example-vpc` or any other name you'd like.

7.  To set the default value for the variable, paste the following prompt into the Gemini Code Assist inline text field that opens from the toolbar.

    ```text
    In the configuration file variables.tf, define the variable "network_name" and set the value "example-vpc" to the "default" argument.
    ```

8.  To prompt Gemini to modify the code accordingly, press **ENTER**.

9.  When prompted in the **Gemini Diff** view, click **Accept**.

    The added `network_name` variable in the configuration file `variables.tf` now looks like this:

    ```hcl
    variable "network_name" {
      description = "The name of the network to be created"
      default     = "example-vpc"
    }
    ```

10. Navigate to the `main.tf` configuration file. This action enables Gemini Code Assist, as indicated by the presence of the spark icon in the upper-right corner of the editor.

11. Click the **Gemini Code Assist: Smart Actions** spark icon on the toolbar.

12. You decide to use Gemini Code Assist to help you update the `network_name` argument to use the variable you just defined by setting the value to `var.network_name` and update the subnet regions from `us-west1` to `us-central1`.

13. In the Gemini Code Assist inline text field, paste the following prompt to update the arguments of the `test-vpc-module` module in the `main.tf` file:

    ```text
    Update the "test-vpc-module" module within the main.tf configuration file. Modify the network name from "my-custom-mode-network" to var.network_name and change the subnet region from us-west1 to us-central1.
    ```

    Your module should resemble the following:

    ```hcl
    module "test-vpc-module" {
      source       = "terraform-google-modules/network/google"
      version      = "~> 6.0"
      project_id   = var.project_id
      network_name = var.network_name
      mtu          = 1460

      subnets = [
        {
          subnet_name   = "subnet-01"
          subnet_ip     = "10.10.10.0/24"
          subnet_region = "us-central1"
        },
        {
          subnet_name           = "subnet-02"
          subnet_ip             = "10.10.20.0/24"
          subnet_region         = "us-central1"
          subnet_private_access = "true"
          subnet_flow_logs      = "true"
        },
        {
          subnet_name               = "subnet-03"
          subnet_ip                 = "10.10.30.0/24"
          subnet_region             = "us-central1"
          subnet_flow_logs          = "true"
          subnet_flow_logs_interval = "INTERVAL_10_MIN"
          subnet_flow_logs_sampling = 0.7
          subnet_flow_logs_metadata = "INCLUDE_ALL_METADATA"
          subnet_flow_logs_filter   = "false"
        }
      ]
    }
    ```

**Define root output values**

Modules also have output values, which are defined within the module with the `output` keyword. You can access them by referring to `module.<MODULE NAME>.<OUTPUT NAME>`. Like input variables, module outputs are listed under the **outputs** tab in the Terraform Registry.

Module outputs are usually either passed to other parts of your configuration or defined as outputs in your root module. This lab includes examples of both.

*   Navigate to the `outputs.tf` file inside of your configuration's directory. Verify that the file contains the following:

    ```hcl
    output "network_name" {
      value       = module.test-vpc-module.network_name
      description = "The name of the VPC being created"
    }

    output "network_self_link" {
      value       = module.test-vpc-module.network_self_link
      description = "The URI of the VPC being created"
    }

    output "project_id" {
      value       = module.test-vpc-module.project_id
      description = "VPC project id"
    }

    output "subnets_names" {
      value       = module.test-vpc-module.subnets_names
      description = "The names of the subnets being created"
    }

    output "subnets_ips" {
      value       = module.test-vpc-module.subnets_ips
      description = "The IP and cidrs of the subnets being created"
    }

    output "subnets_regions" {
      value       = module.test-vpc-module.subnets_regions
      description = "The region where subnets will be created"
    }

    output "subnets_private_access" {
      value       = module.test-vpc-module.subnets_private_access
      description = "Whether the subnets will have access to Google API's without a public IP"
    }

    output "subnets_flow_logs" {
      value       = module.test-vpc-module.subnets_flow_logs
      description = "Whether the subnets will have VPC flow logs enabled"
    }

    output "subnets_secondary_ranges" {
      value       = module.test-vpc-module.subnets_secondary_ranges
      description = "The secondary ranges associated with these subnets"
    }

    output "route_names" {
      value       = module.test-vpc-module.route_names
      description = "The routes associated with this VPC"
    }
    ```

**Provision infrastructure**

1.  In Cloud Shell, navigate to your `simple_project` directory:

    ```bash
    cd ~/terraform-google-network/examples/simple_project
    ```

2.  Initialize your Terraform configuration:

    ```bash
    terraform init
    ```

3.  Create your VPC:

    ```bash
    terraform apply
    ```

4.  To apply the changes and continue, respond to the prompt with `yes`.

    Great! You've just used your first module. Your configuration's output should resemble the following.

    **Output:**

    ```hcl
    network_name = "example-vpc"
    network_self_link = "https://www.googleapis.com/compute/v1/projects/qwiklabs-gcp-00-177abd52dfd9/global/networks/example-vpc"
    project_id = "qwiklabs-gcp-00-177abd52dfd9"
    route_names = []
    subnets_flow_logs = [
      false,
      true,
      true,
    ]
    subnets_ips = [
      "10.10.10.0/24",
      "10.10.20.0/24",
      "10.10.30.0/24",
    ]
    subnets_names = [
      "subnet-01",
      "subnet-02",
      "subnet-03",
    ]
    # ...
    ```

**Understand how modules work**

When using a new module for the first time, you must run either `terraform init` or `terraform get` to install the module. When either of these commands is run, Terraform installs any new modules in the `.terraform/modules` directory within your configuration's working directory. For local modules, Terraform creates a symlink to the module's directory. Because of this, any changes to local modules are effective immediately, without your having to re-run `terraform get`.

**Clean up your infrastructure**

Now that you have explored how to use modules from the Terraform Registry, how to configure those modules with input variables, and how to get output values from those modules, it's a good idea to do some cleanup.

1.  Destroy the infrastructure you created:

    ```bash
    terraform destroy
    ```

2.  Respond to the prompt with `yes`. Terraform destroys the infrastructure you created.

3.  Once you've destroyed your resourced, delete the `terraform-google-network` folder.

    ```bash
    cd ~
    rm -rd terraform-google-network -f
    ```

Click **Check my progress** to verify the objective.
*   Provision infrastructure

**Task 2. Build a module**

In the last task, you used a module from the Terraform Registry to create a VPC network in Google Cloud. Although using existing Terraform modules correctly is an important skill, every Terraform practitioner also benefits from learning how to create modules. We recommend that you create every Terraform configuration with the assumption that it may be used as a module, because this helps you design your configurations to be flexible, reusable, and composable.

As you may already know, Terraform treats every configuration as a module. When you run `terraform commands`, or use Terraform Cloud or Terraform Enterprise to remotely run Terraform, the target directory containing Terraform configuration is treated as the **root module**.

In this task, you create a module to manage Compute Storage buckets used to host static websites.

**Module structure**

Terraform treats any local directory referenced in the `source` argument of a `module` block as a module. A typical file structure for a new module is:

*   LICENSE
*   README.md
*   main.tf
*   variables.tf
*   outputs.tf

**Note:** None of these files are required or has any special meaning to Terraform when it uses your module. You can create a module with a single `.tf` file or use any other file structure you like.

Each of these files serves a purpose:

*   `LICENSE` contains the license under which your module will be distributed. When you share your module, the `LICENSE` file will let people know the terms under which it has been made available. Terraform itself does not use this file.
*   `README.md` contains documentation in markdown format that describes how to use your module. Terraform does not use this file, but services like the Terraform Registry and GitHub will display the contents of this file to visitors to your module's Terraform Registry or GitHub page.
*   `main.tf` contains the main set of configurations for your module. You can also create other configuration files and organize them in a way that makes sense for your project.
*   `variables.tf` contains the variable definitions for your module. When your module is used by others, the variables will be configured as arguments in the module block. Because all Terraform values must be defined, any variables that don't have a default value will become required arguments. A variable with a default value can also be provided as a module argument, thus overriding the default value.
*   `outputs.tf` contains the output definitions for your module. Module outputs are made available to the configuration using the module, so they are often used to pass information about the parts of your infrastructure defined by the module to other parts of your configuration.

Be aware of these files and ensure that you don't distribute them as part of your module:

*   `terraform.tfstate` and `terraform.tfstate.backup` files contain your Terraform state and are how Terraform keeps track of the relationship between your configuration and the infrastructure provisioned by it.
*   The `.terraform` directory contains the modules and plugins used to provision your infrastructure. These files are specific to an individual instance of Terraform when provisioning infrastructure, not the configuration of the infrastructure defined in `.tf` files.
*   `*.tfvars` files don't need to be distributed with your module unless you are also using it as a standalone Terraform configuration because module input variables are set via arguments to the module block in your configuration.

**Note:** If you are tracking changes to your module in a version control system such as Git, you may want to configure your version control system to ignore these files. For an example, see this [.gitignore file](https://github.com/github/gitignore/blob/master/Terraform.gitignore) from GitHub.

**Create a module**

Navigate to your home directory and create your root module by constructing a new `main.tf` configuration file. Then create a directory called **modules** that contains another folder called `gcs-static-website-bucket`. You work with three Terraform configuration files inside the `gcs-static-website-bucket` directory: `website.tf`, `variables.tf`, and `outputs.tf`.

1.  Create the directory for your new module:

    ```bash
    cd ~
    touch main.tf
    mkdir -p modules/gcs-static-website-bucket
    ```

2.  Navigate to the module directory and run the following commands to create three empty files:

    ```bash
    cd modules/gcs-static-website-bucket
    touch website.tf variables.tf outputs.tf
    ```

3.  Inside the `gcs-static-website-bucket` directory, run the following command to create a file called `README.md` with the following content:

    ```bash
    tee -a README.md <<EOF
    # GCS static website bucket

    This module provisions Cloud Storage buckets configured for static website hosting.
    EOF
    ```

    **Note:** Choosing the correct license for your modules is out of the scope of this lab. This lab uses the Apache 2.0 open source license.

4.  Create another file called `LICENSE` with the following content:

    ```bash
    tee -a LICENSE <<EOF
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    EOF
    ```

    **Note:** Neither of these files is required or used by Terraform. Having them is a best practice for modules that might be shared with others.

    Your current module directory structure should now look like this:

    ```text
    main.tf
    modules/
    └── gcs-static-website-bucket
        ├── LICENSE
        ├── README.md
        ├── website.tf
        ├── outputs.tf
        └── variables.tf
    ```

5.  Add this Cloud Storage bucket resource to your `website.tf` file inside the `modules/gcs-static-website-bucket` directory:

    ```hcl
    resource "google_storage_bucket" "bucket" {
      name               = var.name
      project            = var.project_id
      location           = var.location
      storage_class      = var.storage_class
      labels             = var.labels
      force_destroy      = var.force_destroy
      uniform_bucket_level_access = true

      versioning {
        enabled = var.versioning
      }

      dynamic "retention_policy" {
        for_each = var.retention_policy == null ? [] : [var.retention_policy]
        content {
          is_locked        = var.retention_policy.is_locked
          retention_period = var.retention_policy.retention_period
        }
      }

      dynamic "encryption" {
        for_each = var.encryption == null ? [] : [var.encryption]
        content {
          default_kms_key_name = var.encryption.default_kms_key_name
        }
      }

      dynamic "lifecycle_rule" {
        for_each = var.lifecycle_rules
        content {
          action {
            type          = lifecycle_rule.value.action.type
            storage_class = lookup(lifecycle_rule.value.action, "storage_class", null)
          }
          condition {
            age                   = lookup(lifecycle_rule.value.condition, "age", null)
            created_before        = lookup(lifecycle_rule.value.condition, "created_before", null)
            with_state            = lookup(lifecycle_rule.value.condition, "with_state", null)
            matches_storage_class = lookup(lifecycle_rule.value.condition, "matches_storage_class", null)
            num_newer_versions    = lookup(lifecycle_rule.value.condition, "num_newer_versions", null)
          }
        }
      }
    }
    ```

    The provider documentation is on GitHub.

6.  Navigate to the `variables.tf` file in your module and add the following code:

    ```hcl
    variable "name" {
      description = "The name of the bucket."
      type        = string
    }

    variable "project_id" {
      description = "The ID of the project to create the bucket in."
      type        = string
    }

    variable "location" {
      description = "The location of the bucket."
      type        = string
    }

    variable "storage_class" {
      description = "The Storage Class of the new bucket."
      type        = string
      default     = null
    }

    variable "labels" {
      description = "A set of key/value label pairs to assign to the bucket."
      type        = map(string)
      default     = null
    }

    variable "bucket_policy_only" {
      description = "Enables Bucket Policy Only access to a bucket."
      type        = bool
      default     = true
    }

    variable "versioning" {
      description = "While set to true, versioning is fully enabled for this bucket."
      type        = bool
      default     = true
    }

    variable "force_destroy" {
      description = "When deleting a bucket, this boolean option will delete all contained objects. If false, Terraform will fail to delete buckets which contain objects."
      type        = bool
      default     = true
    }

    variable "iam_members" {
      description = "The list of IAM members to grant permissions on the bucket."
      type = list(object({
        role   = string
        member = string
      }))
      default = []
    }

    variable "retention_policy" {
      description = "Configuration of the bucket's data retention policy for how long objects in the bucket should be retained."
      type = object({
        is_locked        = bool
        retention_period = number
      })
      default = null
    }

    variable "encryption" {
      description = "A Cloud KMS key that will be used to encrypt objects inserted into this bucket"
      type = object({
        default_kms_key_name = string
      })
      default = null
    }

    variable "lifecycle_rules" {
      description = "The bucket's Lifecycle Rules configuration."
      type = list(object({
        # Object with keys:
        # - type - The type of the action of this Lifecycle Rule. Supported values: Delete and SetStorageClass.
        # - storage_class - (Required if action type is SetStorageClass) The target Storage Class of objects affected by this Lifecycle Rule.
        action = any

        # Object with keys:
        # - age - (Optional) Minimum age of an object in days to satisfy this condition.
        # - created_before - (Optional) Creation date of an object in RFC 3339 (e.g. 2017-06-13) to satisfy this condition.
        # - with_state - (Optional) Match to live and/or archived objects. Supported values include: "LIVE", "ARCHIVED", "ANY".
        # - matches_storage_class - (Optional) Storage Class of objects to satisfy this condition. Supported values include: MULTI_REGIONAL, REGIONAL, NEARLINE, COLDLINE, STANDARD, DURABLE_REDUCED_AVAILABILITY.
        # - num_newer_versions - (Optional) Relevant only for versioned objects. The number of newer versions of an object to satisfy this condition.
        condition = any
      }))
      default = []
    }
    ```

7.  Add an output to your module in the `outputs.tf` file inside your module:

    ```hcl
    output "bucket" {
      description = "The created storage bucket"
      value       = google_storage_bucket.bucket
    }
    ```

    Like variables, outputs in modules perform the same function as they do in the root module but are accessed in a different way. A module's outputs can be accessed as read-only attributes on the module object, which is available within the configuration that calls the module.

8.  Return to the `main.tf` in your **root directory** and add a reference to the new module:

    ```hcl
    module "gcs-static-website-bucket" {
      source = "./modules/gcs-static-website-bucket"

      name       = var.name
      project_id = var.project_id
      location   = "us-central1"

      lifecycle_rules = [{
        action = {
          type = "Delete"
        }
        condition = {
          age        = 365
          with_state = "ANY"
        }
      }]
    }
    ```

9.  In your **root directory**, create an `outputs.tf` file for your root module:

    ```bash
    cd ~
    touch outputs.tf
    ```

10. Add the following code in the `outputs.tf` file:

    ```hcl
    output "bucket-name" {
      description = "Bucket names."
      value       = module.gcs-static-website-bucket.bucket
    }
    ```

11. In your **root directory**, create a `variables.tf` file:

    ```bash
    touch variables.tf
    ```

12. Add the following code in the `variables.tf` file:

    ```hcl
    variable "project_id" {
      description = "The ID of the project in which to provision resources."
      type        = string
      default     = "qwiklabs-gcp-00-177abd52dfd9"
    }

    variable "name" {
      description = "Name of the buckets to create."
      type        = string
      default     = "qwiklabs-gcp-00-177abd52dfd9"
    }
    ```

    **Note:** The name of your storage bucket must be globally unique. Using your name and the date is usually a good way to create a unique bucket name.

**Install the local module**

Whenever you add a new module to a configuration, Terraform must install the module before it can be used. Both the `terraform get` and `terraform init` commands install and update modules. The `terraform init` command also initializes backends and installs plugins.

1.  Install the module:

    ```bash
    terraform init
    ```

2.  Provision your bucket:

    ```bash
    terraform apply
    ```

3.  Respond `yes` to the prompt. Your bucket and other resources are provisioned.

**Upload files to the bucket**

You have now configured and used your own module to create a static website. You may want to visit this static website. Right now there is nothing inside your bucket, so there is nothing to see at the website. In order to see any content, you need to upload objects to your bucket. You can upload the contents of the `www` directory in the GitHub repository.

1.  Download the sample contents to your home directory:

    ```bash
    cd ~
    curl https://raw.githubusercontent.com/hashicorp/learn-terraform-modules/master/modules/aws-s3-static-website-bucket/www/index.html > index.html
    curl https://raw.githubusercontent.com/hashicorp/learn-terraform-modules/master/modules/aws-s3-static-website-bucket/www/error.html > error.html
    ```

2.  Copy the files over to the cloud storage bucket `qwiklabs-gcp-00-177abd52dfd9`:

    ```bash
    gsutil cp *.html gs://qwiklabs-gcp-00-177abd52dfd9
    ```

3.  In a new tab in your browser, go to the website `https://storage.cloud.google.com/YOUR-BUCKET-NAME/index.html`, replacing `YOUR-BUCKET-NAME` with the name of your storage bucket `qwiklabs-gcp-00-177abd52dfd9`.

    You should see a basic HTML web page that says **Nothing to see here**.

Click **Check my progress** to verify the objective.
*   Build a module

**Clean up the website and infrastructure**

Lastly, you clean up your project by destroying the infrastructure you just created.

1.  Destroy your Terraform resources:

    ```bash
    terraform destroy
    ```

2.  Respond to the prompt with `yes`. Terraform destroys all of the resources you created by following this lab.

**Congratulations!**

In this lab, you explored the foundations of Terraform modules and how to use a pre-existing module from the Registry. You then built your own module to create a static website hosted on a Cloud Storage bucket. In doing so, you defined inputs, outputs, and variables for your configuration files and learned the best-practices for building modules.

**Next steps/Learn More**

These links provide more hands-on practice with Terraform:

*   Hashicorp on the Google Cloud Marketplace!
*   Hashicorp Learn
*   Terraform Community
*   Terraform Google Examples

**Google Cloud training and certification**

...helps you make the most of Google Cloud technologies. Our classes include technical skills and best practices to help you get up to speed quickly and continue your learning journey. We offer fundamental to advanced level training, with on-demand, live, and virtual options to suit your busy schedule. Certifications help you validate and prove your skill and expertise in Google Cloud technologies.