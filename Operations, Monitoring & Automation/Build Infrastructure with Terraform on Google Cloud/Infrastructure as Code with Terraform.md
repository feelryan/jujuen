Here is the transcript of the video content:

**Task 1. Build infrastructure**

Terraform comes pre-installed in Cloud Shell. With Terraform already installed, you can dive right in and create some infrastructure.

Start by creating your example configuration to a file named `main.tf`. Terraform recognizes files ending in `.tf` or `.tf.json` as configuration files and loads them when it runs.

1.  Create the `main.tf` file:

    ```bash
    touch main.tf
    ```

2.  Click the **Open Editor** button on the toolbar of Cloud Shell. (You can switch between Cloud Shell and the code editor by using the **Open Editor** and **Open Terminal** icons as required, or click the **Open in new window** button to leave the Editor open in a separate tab).

3.  In the Editor, add the following content to the `main.tf` file.

    ```hcl
    terraform {
      required_providers {
        google = {
          source = "hashicorp/google"
          version = "3.5.0"
        }
      }
    }

    provider "google" {
      project = "qwiklabs-gcp-02-39d5f4a8b6e1"
      region  = "us-east1"
      zone    = "us-east1-d"
    }

    resource "google_compute_network" "vpc_network" {
      name = "terraform-network"
    }
    ```

**Terraform block**

The `terraform {}` block is required so Terraform knows which provider to download from the Terraform Registry. In the configuration above, the `google` provider's source is defined as `hashicorp/google` which is shorthand for `registry.terraform.io/hashicorp/google`.

You can also assign a version to each provider defined in the `required_providers` block. The `version` argument is optional, but recommended. It is used to constrain the provider to a specific version or a range of versions in order to prevent downloading a new provider that may possibly contain breaking changes. If the version isn't specified, Terraform automatically downloads the most recent provider during initialization.

To learn more, on the HashiCorp Terraform website, refer to the Provider Requirements.

**Providers**

The `provider` block is used to configure the named provider, in this case `google`. A provider is responsible for creating and managing resources. Multiple provider blocks can exist if a Terraform configuration manages resources from different providers.

**Initialization**

The first command to run for a new configuration—or after checking out an existing configuration from version control—is `terraform init`. This will initialize various local settings and data that will be used by subsequent commands.

*   Initialize your new Terraform configuration by running the `terraform init` command in the same directory as your `main.tf` file:

    ```bash
    terraform init
    ```

**Creating resources**

1.  Apply your configuration now by running the command `terraform apply`:

    ```bash
    terraform apply
    ```

The output has a `+` next to resource `"google_compute_network" "vpc_network"`, meaning that Terraform will create this resource. Beneath that, it shows the attributes that will be set. When the value displayed is `(known after apply)`, it means that the value won't be known until the resource is created.

If the plan was created successfully, Terraform now pauses and waits for approval before proceeding. If anything in the plan seems incorrect or dangerous, it is safe to abort here with no changes made to your infrastructure.

If `terraform apply` failed with an error, read the error message and fix the error that occurred.

2.  The plan looks acceptable here, so type `yes` at the confirmation prompt, and press **ENTER** to proceed.

    Executing the plan takes a few minutes since Terraform waits for the network to be created successfully:

    ```text
    # ...
    Enter a value: yes

    google_compute_network.vpc_network: Creating...
    google_compute_network.vpc_network: Still creating... [10s elapsed]
    google_compute_network.vpc_network: Still creating... [20s elapsed]
    google_compute_network.vpc_network: Still creating... [30s elapsed]
    google_compute_network.vpc_network: Still creating... [40s elapsed]
    google_compute_network.vpc_network: Still creating... [50s elapsed]
    google_compute_network.vpc_network: Creation complete after 58s [id=terraform-network]

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

After this, Terraform is all done! You can go to the Cloud console to see the network you have provisioned.

3.  In the Google Cloud console, from the **Navigation menu**, navigate to **VPC network**. You should see the `terraform-network` has been provisioned.

4.  In Cloud Shell, run the `terraform show` command to inspect the current state:

    ```bash
    terraform show
    ```

These values can be referenced to configure other resources or outputs, which are covered later in this lab.

Click **Check my progress** to verify the objective.
*   Create resources in Terraform

**Task 2. Change the infrastructure**

In the previous section, you created basic infrastructure with a VPC network. In this section, you're going to modify your configuration, and see how Terraform handles change.

Infrastructure is continuously evolving, and Terraform was built to help manage and enact that change. As you change Terraform configurations, Terraform builds an execution plan that only modifies what is necessary to reach your desired state.

By using Terraform to change infrastructure, you can version control not only your configurations but also your state so you can see how the infrastructure evolves over time.

**Add resources**

You can add new resources by adding them to your Terraform configuration and running `terraform apply` to provision them.

1.  In the Editor, add a compute instance resource to `main.tf`:

    ```hcl
    resource "google_compute_instance" "vm_instance" {
      name         = "terraform-instance"
      machine_type = "e2-micro"

      boot_disk {
        initialize_params {
          image = "debian-cloud/debian-12"
        }
      }

      network_interface {
        network = "google_compute_network.vpc_network.name"
        access_config {
        }
      }
    }
    ```

    *Note: To use this snippet with Terraform 0.12, remove the `terraform {}` block.*

This resource includes a few more arguments. The `name` and `machine_type` are simple strings, but `boot_disk` and `network_interface` are more complex blocks. You can see all of the available options in the google_compute_instance documentation.

For this example, your compute instance will use a Debian operating system, and will be connected to the VPC Network you created earlier. Notice how this configuration refers to the network's name property with `google_compute_network.vpc_network.name` — `google_compute_network.vpc_network` is the ID, matching the values in the block that defines the network, and `name` is a property of that resource.

The presence of the `access_config` block, even without any arguments, ensures that the instance is accessible over the internet.

2.  Now run `terraform apply` to create the compute instance:

    ```bash
    terraform apply
    ```

3.  Once again, answer `yes` to the confirmation prompt.

This is a fairly straightforward change - you added a `"google_compute_instance"` resource named `"vm_instance"` to your configuration, and Terraform created the resource in Google Cloud.

**Enable Gemini Code Assist in the Cloud Shell IDE**

You can use Gemini Code Assist in an integrated development environment (IDE) such as Cloud Shell to receive guidance on code or solve problems with your code. Before you can start using Gemini Code Assist, you need to enable it.

1.  In Cloud Shell, enable the **Gemini for Google Cloud** API with the following command:

    ```bash
    gcloud services enable cloudaicompanion.googleapis.com
    ```

2.  Click **Open Editor** on the Cloud Shell toolbar.

    *Note: To open the Cloud Shell Editor, click Open Editor on the Cloud Shell toolbar. You can switch between Cloud Shell and the code editor by clicking Open Editor or Open Terminal, as required.*

3.  In the left pane, click the **Settings** icon, then in the **Settings** view, search for **Gemini Code Assist**.

4.  Locate and ensure that the checkbox is selected for **Geminicodeassist: Enable**, and close the **Settings**.

5.  Click **Cloud Code - No Project** in the status bar at the bottom of the screen.

6.  Authorize the plugin as instructed. If a project is not automatically selected, click **Select a Google Cloud Project**, and choose `qwiklabs-gcp-02-39d5f4a8b6e1`.

7.  Verify that your Google Cloud project (`qwiklabs-gcp-02-39d5f4a8b6e1`) displays in the Cloud Code status message in the status bar.

**Change resources with help from Gemini Code Assist**

In addition to creating resources, Terraform can also make changes to those resources.

To help you be more productive while minimizing context switching, Gemini Code Assist provides AI-powered smart actions directly in your code editor. In this section, you decide to use Gemini Code Assist to help you modify some resources with Terraform.

You want to add a `tags` argument to your `vm_instance` resource in the configuration file `main.tf`.

1.  Click the **Gemini Code Assist: Smart Actions** icon on the toolbar.

2.  Paste the following prompt into the Gemini Code Assist inline text field that opens from the toolbar.

    ```text
    In the configuration file "main.tf", update the "vm_instance" resource by adding a "tags" argument. Set the value to ["web", "dev"].
    ```

3.  To prompt Gemini to modify the code accordingly, press **ENTER**.

4.  When prompted in the **Gemini Diff** view, click **Accept**.

5.  The added `tags` argument inside the `vm_instance` resource in the configuration file `main.tf` now looks like this:

    ```hcl
    resource "google_compute_instance" "vm_instance" {
      name         = "terraform-instance"
      machine_type = "e2-micro"
      tags         = ["web", "dev"]
      # ...
    }
    ```

6.  Run `terraform apply` again to update the instance:

    ```bash
    terraform apply
    ```

7.  The prefix `~` means that Terraform updates the resource in-place. You can go and apply this change by responding `yes`, and Terraform adds the tags to your instance.

Click **Check my progress** to verify the objective.
*   Change the infrastructure

**Make destructive changes**

A destructive change is a change that requires the provider to replace the existing resource rather than updating it. This usually happens because the cloud provider doesn't support updating the resource in the way described by your configuration.

Changing the disk image of your instance is one example of a destructive change. In this section, you edit the `boot_disk` block inside the `vm_instance` resource in your configuration file `main.tf` with the help of Gemini Code Assist's Smart Actions.

1.  Click **Open Editor** to switch back to the Cloud Shell Editor, and click the **Gemini Code Assist: Smart Actions** icon on the toolbar.

2.  Paste the following prompt into the Gemini Code Assist inline text box that opens from the toolbar:

    ```text
    In the configuration file "main.tf", update the image in the boot_disk block of the "vm_instance" resource to "cos-cloud/cos-stable".
    ```

3.  Press **ENTER** to change the image in the `vm_instance` resource accordingly.

4.  When prompted in the **Gemini Diff** view, click **Accept**.

5.  The `boot_disk` block inside the `vm_instance` resource in the configuration file `main.tf` should now look like this:

    ```hcl
    boot_disk {
      initialize_params {
        image = "cos-cloud/cos-stable"
      }
    }
    ```

6.  Now run `terraform apply` again to explore how Terraform applies this change to the existing resources:

    ```bash
    terraform apply
    ```

The prefix `-/+` means that Terraform will destroy and recreate the resource, rather than updating it in-place. While some attributes can be updated in-place (which are shown with the `~` prefix), changing the boot disk image for an instance requires recreating it. Terraform and the Google Cloud provider handle these details for you, and the execution plan makes it clear what Terraform will do.

Additionally, the execution plan shows that the disk image change is what required your instance to be replaced. Using this information, you can adjust your changes to possibly avoid destroy/create updates if they are not acceptable in some situations.

7.  Once again, Terraform prompts for approval of the execution plan before proceeding. Answer `yes` to execute the planned steps.

As indicated by the execution plan, Terraform first destroyed the existing instance and then created a new one in its place. You can use `terraform show` again to see the new values associated with this instance.

**Destroy infrastructure**

You have now seen how to build and change infrastructure. Before moving on to creating multiple resources and showing resource dependencies, you explore how to completely destroy your Terraform-managed infrastructure.

Destroying your infrastructure is a rare event in production environments. But if you're using Terraform to spin up multiple environments such as development, testing, and staging, then destroying is often a useful action.

Resources can be destroyed using the `terraform destroy` command, which is similar to `terraform apply` but it behaves as if all of the resources have been removed from the configuration.

*   Try the `terraform destroy` command. Answer `yes` when prompted to execute this plan and destroy the infrastructure:

    ```bash
    terraform destroy
    ```

The `-` prefix indicates that the instance and the network will be destroyed. As with apply, Terraform shows its execution plan and waits for approval before making any changes.

Just like with `terraform apply`, Terraform determines the order in which things must be destroyed. Google Cloud won't allow a VPC network to be deleted if there are resources still in it, so Terraform waits until the instance is destroyed before destroying the network. When performing operations, Terraform creates a dependency graph to determine the correct order of operations. In more complicated cases with multiple resources, Terraform performs operations in parallel when it's safe to do so.

Click **Check my progress** to verify the objective.
*   Make destructive changes

**Task 3. Create resource dependencies**

In this section, you learn more about resource dependencies and how to use resource parameters to share information about one resource with other resources.

Real-world infrastructure has a diverse set of resources and resource types. Terraform configurations can contain multiple resources, multiple resource types, and these types can even span multiple providers.

In this section, you are shown a basic example of how to configure multiple resources and how to use resource attributes to configure other resources.

*   Run the following command to recreate your network and instance:

    ```bash
    terraform apply
    ```

After you respond to the prompt with `yes`, the resources are created.

**Assign a static IP address**

1.  Now run the following to add to your configuration and assign a static IP to the VM instance in `main.tf`:

    ```hcl
    resource "google_compute_address" "vm_static_ip" {
      name = "terraform-static-ip"
    }
    ```

This should look familiar from the earlier example of adding a VM instance resource, except this time you're creating a `"google_compute_address"` resource type. This resource type allocates a reserved IP address to your project.

2.  Next, run `terraform plan`:

    ```bash
    terraform plan
    ```

You can see what will be created with `terraform plan`:

```text
# ...
Terraform will perform the following actions:

  # google_compute_address.vm_static_ip will be created
  + resource "google_compute_address" "vm_static_ip" {
      + address            = (known after apply)
      + address_type       = "EXTERNAL"
      + creation_timestamp = (known after apply)
      + id                 = (known after apply)
      + name               = "terraform-static-ip"
      + network_tier       = (known after apply)
      + project            = (known after apply)
      + region             = (known after apply)
      + self_link          = (known after apply)
      + subnetwork         = (known after apply)
      + users              = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

*Note: You didn't specify an "-out" parameter to save this plan, so Terraform "terraform apply" is subsequently run.*

Unlike `terraform apply`, the `plan` command will only show what would be changed, and never actually applies the changes directly. Notice that the only change you have made so far is to add a static IP. Next, you need to attach the IP address to your instance.

3.  Update the `network_interface` configuration for your instance like so:

    ```hcl
    network_interface {
      network = "google_compute_network.vpc_network.self_link"
      access_config {
        nat_ip = google_compute_address.vm_static_ip.address
      }
    }
    ```

The `access_config` block has several optional arguments, and in this case you'll set `nat_ip` to be the static IP address. When Terraform reads this configuration, it will:

*   Ensure that `vm_static_ip` is created before `vm_instance`
*   Save the properties of `vm_static_ip` in the state
*   Set `nat_ip` to the value of the `vm_static_ip.address` property

4.  Run `terraform plan` again, but this time, save the plan:

    ```bash
    terraform plan -out static_ip
    ```

Saving the plan this way ensures that you can apply exactly the same plan in the future. If you try to apply the file created by the plan, Terraform will first check to make sure the exact same set of changes will be made before applying the plan.

In this case, you can see that Terraform will create a new `google_compute_address` and update the existing VM to use it.

5.  Run `terraform apply "static_ip"` to see how Terraform plans to apply this change:

    ```bash
    terraform apply "static_ip"
    ```

As shown above, Terraform created the static IP before modifying the VM instance. Due to the interpolation expression that passes the IP address to the instance's network interface configuration, Terraform is able to infer a dependency, and knows it must create the static IP before updating the instance.

Click **Check my progress** to verify the objective.
*   Create resource dependencies

**Explore implicit and explicit dependencies**

By studying the resource attributes used in interpolation expressions, Terraform can automatically infer when one resource depends on another. In the example above, the reference to `google_compute_address.vm_static_ip.address` creates an *implicit dependency* on the `google_compute_address` named `vm_static_ip`.

Terraform uses this dependency information to determine the correct order in which to create and update different resources. In the example above, Terraform knows that the `vm_static_ip` must be created before the `vm_instance` is updated to use it.

Implicit dependencies via interpolation expressions are the primary way to inform Terraform about these relationships, and should be used whenever possible.

Sometimes there are dependencies between resources that are not visible to Terraform. The `depends_on` argument can be added to any resource and accepts a list of resources to create explicit dependencies for.

For example, perhaps an application you run on your instance expects to use a specific Cloud Storage bucket, but that dependency is configured inside the application code and thus not visible to Terraform. In that case, you can use `depends_on` to explicitly declare the dependency.

1.  Add a Cloud Storage bucket and an instance with an explicit dependency on the bucket by adding the following to `main.tf`:

    ```hcl
    # New resource for the storage bucket our application will use.
    resource "google_storage_bucket" "example_bucket" {
      name     = "UNIQUE-BUCKET-NAME"
      location = "US"

      website {
        main_page_suffix = "index.html"
        not_found_page   = "404.html"
      }
    }

    # Create a new instance that uses the bucket
    resource "google_compute_instance" "another_instance" {
      # ...
      # Tells Terraform that this VM instance must be created only after the
      # storage bucket has been created.
      depends_on = [google_storage_bucket.example_bucket]
    }
    ```

    *Note: Storage buckets must be globally unique. Because of this, you need to replace UNIQUE-BUCKET-NAME with a unique, valid name for a bucket. Using your name and the date is usually a good way to guess a unique bucket name.*

You may wonder where in your configuration these resources should go. The order that resources are defined in a terraform configuration file has no effect on how Terraform applies your changes. Organize your configuration files in a way that makes the most sense for you and your team.

2.  Now run `terraform plan` and `terraform apply` to see these changes in action:

    ```bash
    terraform plan
    terraform apply
    ```

3.  Before moving on, remove these new resources from your configuration and run `terraform apply` once again to destroy them. You won't use the bucket or the second instance any further in this lab.

**Task 4. Provision infrastructure**

The compute instance you launched at this point is based on the Google image given, but has no additional software installed or configuration applied.

Google Cloud allows customers to manage their own custom operating system images. This can be a great way to ensure that the instances you provision with Terraform are pre-configured based on your needs. Packer is the perfect tool for this and includes a builder for Google Cloud.

Terraform uses provisioners to upload files, run shell scripts, or install and trigger other software like configuration management tools.

**Define a provisioner**

1.  To define a provisioner, modify the resource block defining the first `vm_instance` in your configuration to look like the following:

    ```hcl
    resource "google_compute_instance" "vm_instance" {
      name         = "terraform-instance"
      machine_type = "e2-micro"
      tags         = ["web", "dev"]

      provisioner "local-exec" {
        command = "echo ${google_compute_instance.vm_instance.name}:  ${google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip} >> ip_address.txt"
      }
      # ...
    }
    ```

This adds a `provisioner` block within the `resource` block. Multiple provisioner blocks can be added to define multiple provisioning steps. Terraform supports many provisioners, but for this example you are using the `local-exec` provisioner.

The `local-exec` provisioner executes a command locally on the machine running Terraform, not the VM instance itself. You're using this provisioner versus the others so we don't have to worry about specifying any connection info right now.

This also shows a more complex example of string interpolation than you've seen before. Each VM instance can have multiple network interfaces, so refer to the first one with `network_interface[0]`, count starting from 0, as most programming languages do. Each network interface can have multiple `access_config` blocks as well, so once again you specify the first one.

2.  Run `terraform apply`:

    ```bash
    terraform apply
    ```

At this point, the output may be confusing at first.

Terraform found nothing to do - and if you check, you'll find that there's no `ip_address.txt` file on your local machine.

Terraform treats provisioners differently from other arguments. Provisioners only run when a resource is created, but adding a provisioner does not force that resource to be destroyed and recreated.

3.  Use `terraform taint` to tell Terraform to recreate the instance:

    ```bash
    terraform taint google_compute_instance.vm_instance
    ```

A tainted resource will be destroyed and recreated during the next `apply`.

4.  Run `terraform apply` now:

    ```bash
    terraform apply
    ```

5.  Verify everything worked by looking at the contents of the `ip_address.txt` file.

    It contains the IP address, just as you asked.

**Failed provisioners and tainted resources**

If a resource is successfully created but fails a provisioning step, Terraform will error and mark the resource as tainted. A resource that is tainted still exists, but shouldn't be considered safe to use, since provisioning failed.

When you generate your next execution plan, Terraform will remove any tainted resources and create new resources, attempting to provision them again after creation.

**Destroy provisioners**

Provisioners can also be defined that run only during a destroy operation. These are useful for performing system cleanup, extracting data, etc.

For many resources, using built-in cleanup mechanisms is recommended if possible (such as init scripts), but provisioners can be used if necessary.

This lab won't show any destroyed provisioner examples. If you need to use destroy provisioners, please refer to the provisioners documentation.

**Congratulations!**

In this lab, you learned how to build, change, and destroy infrastructure with Terraform. You then created resource dependencies, and provisioned basic infrastructure with Terraform configuration files.

**Next steps/Learn more**

Be sure to check out the following resources to receive more hands-on practice with Terraform:

*   Hashicorp on the Google Cloud Marketplace!
*   Hashicorp Learn
*   Terraform Community
*   Terraform Google Examples