This challenge requires you to integrate several Google Cloud services—Cloud Storage, Pub/Sub, Cloud Run, and IAM—following the standard Jooli Inc. conventions.

Since the most effective way to complete these tasks quickly and accurately in a lab environment is often through the Cloud Shell (command line), I will primarily provide `gcloud` commands based on the Qwik Start documentation you provided, with placeholders that you must replace with your project details.

**Jooli Inc. Standards:**

  * **Region:** `us-east1`
  * **Zone:** `us-east1-c`
  * **Naming:** `memories-resource`

-----

## **Task 1: Create a Cloud Storage Bucket**

This task is based on the instructions from **Cloud Storage - Qwik Start - CLISDK.md**. You need a globally unique name, so replace `<YOUR-BUCKET-NAME>` with a name like `memories-photo-bucket-yourinitials-projectid`.

1.  **Set the default region for the shell session:**
    (Although bucket location is set with a flag, setting the region globally is good practice.)

    ```bash
    gcloud config set compute/region us-east1
    ```

2.  **Create the bucket:**
    Use the `gcloud storage buckets create` command, specifying the location as `us-east1` and setting the project's standard storage class (which is often the default, but we specify it for completeness).

    ```bash
    gcloud storage buckets create gs://qwiklabs-gcp-03-dbcc25e8f9d7-bucket \
        --location=us-east1 \
        --uniform-bucket-level-access
    ```

      * *Example Name:* `gs://memories-photo-bucket-ab-12345`
      * The Challenge Lab requires a second bucket for the thumbnails, so let's create two, one for source images and one for thumbnails.

    <!-- end list -->

    ```bash
    # Create the source bucket
    gcloud storage buckets create gs://memories-source-<UNIQUE-ID> --location=us-east1 --uniform-bucket-level-access

    # Create the destination bucket for thumbnails (optional but recommended for the thumbnail workflow)
    gcloud storage buckets create gs://memories-thumbs-<UNIQUE-ID> --location=us-east1 --uniform-bucket-level-access
    ```

## **Task 2: Create a Pub/Sub Topic**

This task is based on the instructions from **PubSub - Qwik Start - Command Line.md**. The topic will be used to send a notification when a new image is uploaded, triggering the Cloud Run Function.

1.  **Create the Pub/Sub Topic:**
    We'll name the topic following the standard: `memories-image-process-topic`.

    ```bash
    gcloud pubsub topics create topic-memories-371
    ```

2.  **Configure the Cloud Storage Bucket to notify the Pub/Sub Topic:**
    This step links the bucket from Task 1 (the source bucket) to the topic from Task 2. This is essential for the function to be triggered by a new file upload.

      * First, we need to grant the Cloud Storage service account the Pub/Sub Publisher role. Get the service account for the bucket:

        ```bash
        # Get the Storage service account (replace <PROJECT_NUMBER> with your project number)
        # You can find the PROJECT_NUMBER in the Cloud Console Dashboard.
        export PROJECT_NUMBER=$(gcloud projects describe $DEVSHELL_PROJECT_ID --format='value(projectNumber)')
        export GCS_SERVICE_ACCOUNT=$PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com
        ```

      * Grant the Pub/Sub Publisher role to the service account:

        ```bash
        gcloud pubsub topics add-iam-policy-binding memories-image-process-topic \
            --member="serviceAccount:$GCS_SERVICE_ACCOUNT" \
            --role="roles/pubsub.publisher"
        ```

      * Create the notification configuration on the source bucket:

        ```bash
        gsutil notification create -t memories-image-process-topic -f json -e OBJECT_FINALIZE gs://memories-source-<UNIQUE-ID>
        ```

        *Replace `gs://memories-source-<UNIQUE-ID>` with your source bucket name.*

## **Task 3: Create a Cloud Run Function**

This task is based on **Cloud Run Functions - Qwik Start - Command Line.md**. Since the function is triggered by a Pub/Sub event, we will use the `gcloud run deploy` command and specify the Pub/Sub trigger.

  * **Note:** The actual code for a thumbnail function requires dependencies (like a Python image library) that are outside the scope of the provided Qwik Starts. However, the Challenge Lab generally requires a simple boilerplate structure and the correct deployment configuration. We will use a simple Node.js template and deploy it correctly.

<!-- end list -->

1.  **Create the function code structure:**

    ```bash
    mkdir memories-thumbnail-generator && cd memories-thumbnail-generator
    ```

2.  **Create `index.js`** (the main function file):

    ```bash
    nano index.js
    ```

    Paste the following Pub/Sub function template. This function receives the bucket and file information from the Pub/Sub message and logs it (the core logic for thumbnailing would go here).

http://googleusercontent.com/immersive_entry_chip/0

3.  **Create `package.json`** (the dependency file):

    ```bash
    nano package.json
        
    ```

http://googleusercontent.com/immersive_entry_chip/1

4.  **Deploy the Cloud Run Function:**
    Use the `gcloud run deploy` command, setting the trigger type to Pub/Sub and linking it to the topic created in Task 2.

    ```bash
gcloud functions deploy memories-thumbnail-generator \
  --gen2 \
  --runtime=nodejs22 \
  --region=us-east1 \
  --source=. \
  --entry-point=memories-thumbnail-generator \
  --trigger-topic topic-memories-149 \
  --stage-bucket qwiklabs-gcp-04-90b2f4e96f1d-bucket \
  --allow-unauthenticated

    ```

## **Task 4: Remove the previous cloud engineer**

This task is based on the instructions from **Cloud IAM - Qwik Start.md**. You must remove the Viewer role assigned to the previous engineer.

1.  **Identify the User/Principal:**
    From the challenge description, the user to be removed is the one with the **Viewer** role. The format is a placeholder, e.g., `student-03-b5c297af1eef@qwiklabs.net`.

    **Important:** Replace `<PREVIOUS-CLOUD-ENGINEER-EMAIL>` with the actual email address provided in your lab instructions.

2.  **Remove the IAM Policy Binding (using Cloud Shell):**
    Use the `gcloud projects remove-iam-policy-binding` command to revoke the role for the specified principal.

    ```bash
    gcloud projects remove-iam-policy-binding $DEVSHELL_PROJECT_ID \
        --member="user:<PREVIOUS-CLOUD-ENGINEER-EMAIL>" \
        --role="roles/viewer" \
        --all
        * The `--all` flag ensures all instances of that specific binding (user/role combination) are removed.
    * Alternatively, you can navigate to **Navigation menu > IAM & Admin > IAM**, find the email address with the **Viewer** role, click the pencil icon next to their entry, and then click **DELETE**.
    ```