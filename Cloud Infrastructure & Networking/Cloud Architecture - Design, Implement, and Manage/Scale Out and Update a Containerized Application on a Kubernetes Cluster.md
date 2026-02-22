# Scale Out and Update a Containerized Application on a Kubernetes Cluster

https://www.skills.google/course_templates/640/labs/613294

## Challenge scenario
You are taking over ownership of a test environment and have been given an updated version of a containerized test application to deploy. Your systems' architecture team has started adopting a containerized microservice architecture. You are responsible for managing the containerized test web applications. You will first deploy the initial version of a test application, called echo-app to a Kubernetes cluster called `echo-cluster` in a deployment called `echo-web`. The cluster will be deployed in the [europe-west4-a] zone.

1. Before you get started, in the Navigation menu, select Cloud Storage > Buckets.

2. Verify the `echo-web-v2.tar.gz` file is in the [gs://qwiklabs-gcp-00-53235f242cda] bucket.

Next, you will check to make sure your GKE cluster has been created before continuing.

3. In the Navigation menu, select Kubernetes Engine > Clusters.

Continue when you see a green checkmark next to `echo-cluster`

4. To deploy your first version of the application, run the following commands in Cloud Shell to get up and running:

> gcloud container clusters get-credentials echo-cluster --zone=europe-west4-a

> kubectl create deployment echo-web --image=gcr.io/qwiklabs-resources/echo-app:v1

> kubectl expose deployment echo-web --type=LoadBalancer --port 80 --target-port 8000

## Your challenge

You need to update the running `echo-app` application in the `echo-web` deployment from the v1 to the v2 code you have been provided. You must also scale out the application to 2 instances and confirm that they are all running.

## Task 1. Build and deploy the updated application with a new tag

The updated sample application, including the Dockerfile and the application context files, are contained in an archive called `echo-web-v2.tar.gz`. The archive has been copied to a Cloud Storage bucket in your lab project called [gs://qwiklabs-gcp-00-53235f242cda]. V2 of the application adds a version number to the output of the application. In this task, you will download the archive, build the Docker image, and tag it with the `v2` tag.

## Task 2. Push the image to the Container Registry

Your organization uses the Container Registry to host Docker images for deployments, and uses the `gcr.io` Container Registry hostname for all projects. You must push the updated image to the Container Registry before deploying it.

## Task 3. Deploy the updated application to the Kubernetes cluster

In this task, you will deploy the updated application to the Kubernetes cluster. The deployment should be named `echo-web` and the application should be exposed on port 80. The application should be accessible from outside the cluster.

## Task 4. Scale out the application

In this task, you will need to scale out the application to 2 replicas.

## Task 5. Confirm the application is running

In this task, you will need to confirm that the application is running and responding correctly. You can use the external IP address of the application to test it.

## Troubleshooting

*Receiving a 504, Gateway timeout error*: This might just indicate that the application hasn't quite initialized yet, but it could also be caused by a mismatch between the default port that is set in the Dockerfile (TCP port 8000) and:

- The choice of application port you configured when deploying the application image, or
- When you configured external access.

## Solution

Based on the scenario and Task 1 description, here are the commands you need to run in Cloud Shell.

Although the task title mentions "deploy," the specific instructions for **Task 1** focus on downloading, building, and tagging the image. However, for the lab to verify your progress (and to fulfill the title's implication), you usually must **push** the image to the Container Registry as well.

### **Task 1 Commands**

Run these commands in Cloud Shell to download the archive, build the `v2` image, and push it to the Google Container Registry (GCR):

```bash
# 1. Download the v2 archive
gsutil cp gs://qwiklabs-gcp-00-53235f242cda/echo-web-v2.tar.gz .

# 2. Extract the archive
tar -xvzf echo-web-v2.tar.gz

# 3. Build the Docker image with the v2 tag
# (Make sure you are in the directory containing the Dockerfile, which the tar extraction usually handles)
docker build -t gcr.io/$DEVSHELL_PROJECT_ID/echo-app:v2 .

# 4. Push the image to the Container Registry
# (This step allows the lab to verify the "tagged image" exists)
docker push gcr.io/$DEVSHELL_PROJECT_ID/echo-app:v2
```

---

### **Next Steps (Deployment & Scaling)**

While the text for Task 1 often stops at the image build, the "Challenge" section and the task title ("Build and **deploy**") imply you may need to update the cluster immediately or in the next task.

If you need to **update the running application** to the v2 image and **scale it out** (as per the "Your Challenge" section), run these additional commands:

```bash
# Update the deployment to use the v2 image
kubectl set image deployment/echo-web echo-app=gcr.io/$DEVSHELL_PROJECT_ID/echo-app:v2

# Scale the deployment to 2 replicas
kubectl scale deployment echo-web --replicas=2
```