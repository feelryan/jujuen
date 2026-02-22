Here is the transcript of the video content.

**You are just starting your junior cloud engineer role with Jooli Inc.** So far you have been helping teams create and manage Google Cloud resources.

You are expected to have the skills and knowledge for these tasks, so don't expect step-by-step guides.

**Your challenge**

You are asked to help a newly formed development team with some of their initial work on a new project around storing and organizing photographs, called *Memories*. You have been asked to assist the Memories team with initial configuration for their application development environment.

You receive the following request to complete the following tasks:

*   Create a bucket for storing the photographs.
*   Create a Pub/Sub topic that will be used by a Cloud Run Function you create.
*   Create a Cloud Run Function.
*   Remove the previous cloud engineer's access from the memories project.

Some Jooli Inc. standards you should follow:

*   Create all resources in the **us-east1** region and **us-east1-c** zone, unless otherwise directed.
*   Use the project VPCs.
*   Naming is normally team-resource, e.g. an instance could be named **kraken-webserver1**.
*   Allocate cost effective resource sizes. Projects are monitored and excessive resource use will result in the containing project's termination (and possibly yours), so beware. This is the guidance the monitoring team is willing to share; unless directed, use **e2-micro** for small Linux VMs and **e2-medium** for Windows or other applications such as Kubernetes nodes.

Each task is described in detail below, good luck!

---

### **Task 1. Create a bucket**

You need to create a bucket called **qwiklabs-gcp-03-dbcc25e8f9d7-bucket**, for the storage of the photographs. Ensure the resource is created in the **us-east1** region and **us-east1-c** zone.

*   Create a bucket called **qwiklabs-gcp-03-dbcc25e8f9d7-bucket**
    *   [Check my progress]

---

### **Task 2. Create a Pub/Sub topic**

Create a Pub/Sub topic called **topic-memories-371** for the Cloud Run Function to send messages.

*   Create a Pub/Sub topic called **topic-memories-371**
    *   [Check my progress]

---

### **Task 3. Create the thumbnail Cloud Run Function**

**Create the function**

Create a Cloud Run Function **memories-thumbnail-generator** that will create a thumbnail from an image added to the **qwiklabs-gcp-03-dbcc25e8f9d7-bucket** bucket.

Ensure the Cloud Run Function is using the **Cloud Run function** environment (which is 2nd generation). Ensure the resource is created in the **us-east1** region and **us-east1-c** zone.

1.  Create a Cloud Run Function (2nd generation) called **memories-thumbnail-generator** using **Node.js 22**.

    **Note:** The Cloud Run Function is required to execute every time an object is created in the bucket created in Task 1. During the process, Cloud Run Function may request permission to enable APIs or request permission to grant roles to service accounts. Please enable each of the required APIs and grant roles as requested.

2.  Make sure you set the **Entry point** (Function to execute) to **memories-thumbnail-generator** and **Trigger** to Cloud Storage.

3.  Add the following code to the `index.js`:

```javascript
const functions = require('@google-cloud/functions-framework');
const { Storage } = require('@google-cloud/storage');
const { PubSub } = require('@google-cloud/pubsub');
const sharp = require('sharp');

functions.cloudEvent('memories-thumbnail-generator', async cloudEvent => {
  const event = cloudEvent.data;

  console.log(`Event: ${JSON.stringify(event)}`);
  console.log(`Hello ${event.bucket}`);

  const fileName = event.name;
  const bucketName = event.bucket;
  const size = '64x64';
  const bucket = new Storage().bucket(bucketName);
  const topicName = 'topic-memories-371';
  const pubsub = new PubSub();

  if (fileName.search('64x64_thumbnail') == -1) {
    // doesn't have a thumbnail, get the filename extension
    const filename_split = fileName.split('.');
    const filename_ext = filename_split[filename_split.length - 1];
    const filename_without_ext = fileName.substring(0, fileName.length - (filename_ext.length + 1));

    if (filename_ext.toLowerCase() == 'png' || filename_ext.toLowerCase() == 'jpg'){
      // only support png and jpg at this point
      console.log(`Processing Original: gs://${bucketName}/${fileName}`);
      const gcsObject = bucket.file(fileName);
      let newFilename = `${filename_without_ext}_${size}_thumbnail.${filename_ext}`;
      const gcsNewObject = bucket.file(newFilename);

      try {
        const [buffer] = await gcsObject.download();
        const resizedBuffer = await sharp(buffer)
          .resize(64, 64, {
            fit: 'inside',
            withoutEnlargement: true,
          })
          .toFormat(filename_ext)
          .toBuffer();

        await gcsNewObject.save(resizedBuffer, {
          metadata: {
            contentType: `image/${filename_ext}`,
          },
        });

        console.log(`Success: ${fileName} -> ${newFilename}`);

        await pubsub
          .topic(topicName)
          .publishMessage({data: Buffer.from(newFilename)});
      } catch (err) {
        console.error(`Error: ${err}`);
      }
    } else {
      console.log(`gs://${bucketName}/${fileName} is not an image I can handle`);
    }
  } else {
    console.log(`gs://${bucketName}/${fileName} already has a thumbnail`);
  }
});
```

4.  Add the following code to the `package.json`:

```json
{
  "name": "thumbnails",
  "version": "1.0.0",
  "description": "Create Thumbnail of uploaded image",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "@google-cloud/functions-framework": "^3.0.0",
    "@google-cloud/pubsub": "^2.0.0",
    "@google-cloud/storage": "^6.11.0",
    "sharp": "^0.32.1"
  },
  "devDependencies": {},
  "engines": {
    "node": ">=4.3.2"
  }
}
```

**Note:** If you get a permission denied error stating it may take a few minutes before all necessary permissions are propagated to the Service Agent, wait a few minutes and try again. Ensure you have the appropriate roles (Eventarc Service Agent, Eventarc Event Receiver, Service Account Token Creator, and Pub/Sub Publisher) assigned to the correct service accounts.

**Test the function**

*   Upload a PNG or JPG image of your choice to the **qwiklabs-gcp-03-dbcc25e8f9d7-bucket** bucket.

**Note:** Alternatively, download this image `https://storage.googleapis.com/cloud-training/gsp315/map.jpg` to your machine. Then, upload it to the bucket.

You will see a thumbnail image appear shortly afterwards (use **REFRESH** on the bucket details page).

After you upload the image file, you can click to check your progress below. You do not need to wait for the thumbnail image to be created.

**Optional:** If the function deployed successfully and you do not see the thumbnail image in the bucket, you can check that the **Triggers** tab displays the trigger information that you previously provided for the function, which may not have saved correctly if you previously encountered errors. If you do not see the Cloud Storage trigger in the **Triggers** tab of the function, you can recreate the trigger (see the documentation page titled **Create a trigger for services**), and then upload a new file again to test again (refresh the page after adding a new file).

*   Verify the Cloud Run Function
    *   [Check my progress]

---

### **Task 4. Remove the previous cloud engineer**

You will see that there are two users defined in the project.

*   One is your account (**student-03-8925060e51e9@qwiklabs.net** with the role of Owner).
*   The other is the previous cloud engineer (**student-03-b5c297af1eef@qwiklabs.net** with the role of Viewer).

1.  Remove the previous cloud engineer's access from the project.

*   Remove the previous cloud engineer
    *   [Check my progress]

---

**Congratulations!**

Google Cloud
**Set Up an App Dev Environment on Google Cloud**
Infrastructure Modernization