# Build and Deploy a Docker Image to a Kubernetes Cluster

https://www.skills.google/course_templates/640/labs/613293

## Challenge scenario

Your development team is interested in adopting a containerized microservices approach to application architecture. You need to test a sample application they have provided for you to make sure that it can be deployed to a Google Kubernetes container. The development group provided a simple Go application called echo-web with a Dockerfile and the associated context that allows you to build a Docker image immediately.

## Your challenge
To test the deployment, you need to download the sample application, then build the Docker container image using a tag that allows it to be stored on the Container Registry. Once the image has been built, you'll push it out to the Container Registry before you can deploy it.

With the image prepared you can then create a Kubernetes cluster, then deploy the sample application to the cluster.

> Note: In order to ensure accurate lab activity tracking you must use `echo-app` as the container repository image name, call your Kubernetes cluster `echo-cluster`, create the Kubernetes cluster in [us-west1-c] zone and use `echo-web` for the deployment name.

Project ID: `qwiklabs-gcp-00-bf9497f7bef6`

## Task 1. Create a Kubernetes cluster

Your test environment is limited in capacity, so you should limit the test Kubernetes cluster you are creating to just two `e2-standard-2` instances. You must call your cluster `echo-cluster`.

-------------------------------------------------------------------------------
Here are the commands to complete **Task 1: Create a Kubernetes cluster**.

Run the following command in your Cloud Shell:

```bash
gcloud container clusters create echo-cluster \
  --zone=us-west1-c \
  --machine-type=e2-standard-2 \
  --num-nodes=2
```

### Explanation of flags used:
*   `create echo-cluster`: Sets the name of the cluster as required.
*   `--zone=us-west1-c`: Specifies the zone required by the lab note.
*   `--machine-type=e2-standard-2`: Sets the machine type for the nodes.
*   `--num-nodes=2`: Limits the cluster to 2 nodes.
-------------------------------------------------------------------------------

## Task 2. Build a tagged Docker image

The sample application, including the Dockerfile and the application context files, are contained in an archive called `echo-web.tar.gz`. The archive has been copied to a Cloud Storage bucket belonging to your lab project called gs://qwiklabs-gcp-00-bf9497f7bef6.

You must deploy this with a tag called `v1`.

-------------------------------------------------------------------------------
Here are the commands for **Task 2: Build a tagged Docker image**.

These commands will download the archive, extract it, and build the Docker image with the required `echo-app` name and `v1` tag.

Run the following in Cloud Shell:

```bash
# 1. Download the file
gsutil cp gs://$DEVSHELL_PROJECT_ID/echo-web.tar.gz .

# 2. Extract the archive
tar -xvf echo-web.tar.gz

# 3. Build the image with the required tag
docker build -t gcr.io/$DEVSHELL_PROJECT_ID/echo-app:v1 .
```

### Explanation:
*   `$DEVSHELL_PROJECT_ID`: This automatically pulls your specific Project ID (`qwiklabs-gcp-00-bf9497f7bef6`) so you don't have to type it manually.
*   `docker build`: Builds the container.
*   `-t ...`: Tags the image specifically for the **Container Registry** (`gcr.io`) with the name `echo-app` and version `v1` as requested in the challenge notes.
-------------------------------------------------------------------------------


## Task 3. Push the image to the Google Container Registry

Your organization has decided that it will always use the `gcr.io` Container Registry hostname for all projects. The sample application is a simple web application that reports some data describing the configuration of the system where the application is running. It is configured to use TCP port 8000 by default.

-------------------------------------------------------------------------------
Here are the commands for **Task 3: Push the image to the Google Container Registry**.

Run the following command to upload the image you built in the previous step:

```bash
docker push gcr.io/$DEVSHELL_PROJECT_ID/echo-app:v1
```

### Explanation:
*   `docker push`: Uploads the local docker image to the remote repository.
*   `gcr.io/$DEVSHELL_PROJECT_ID/echo-app:v1`: Specifies the exact image and tag created in Task 2.
-------------------------------------------------------------------------------


## Task 4. Deploy the application to the Kubernetes cluster

Even though the application is configured to respond to HTTP requests on port 8000, you must configure the service to respond to normal web requests on port 80. When configuring the cluster for your sample application, call your deployment `echo-web`.

-------------------------------------------------------------------------------
Here are the commands for **Task 4: Deploy the application to the Kubernetes cluster**.

You need to create a deployment using the image from GCR and then expose it as a LoadBalancer service to map port 80 to port 8000.

Run the following commands:

```bash
# 1. Create the deployment
kubectl create deployment echo-web --image=gcr.io/$DEVSHELL_PROJECT_ID/echo-app:v1

# 2. Expose the deployment (Map external port 80 to container port 8000)
kubectl expose deployment echo-web --type=LoadBalancer --port=80 --target-port=8000
```

### Explanation:
*   `create deployment echo-web`: Creates the pod controller with the required name `echo-web`.
*   `--image=...`: Pulls the specific image and tag you pushed in Task 3.
*   `expose deployment`: Creates a Service to allow network traffic.
*   `--type=LoadBalancer`: Provision an external IP address so you can access the app over the internet.
*   `--port=80`: The port the Service exposes (for "normal web requests").
*   `--target-port=8000`: The port the application is actually listening on inside the container.
-------------------------------------------------------------------------------


## Troubleshooting

*Receiving a 504, Gateway timeout error*: This might just indicate that the application hasn't quite initialized yet, but it could also be caused by a mismatch between the default port that is set in the Dockerfile (TCP port 8000) and the choice of application port you configured when deploying the application image, or when you configured external access.

*Not receiving assessment score for the last three objectives*: This might just indicate that you have created your Kubernetes cluster in the different zone rather than [us-west1-c] zone which is expected in the lab.