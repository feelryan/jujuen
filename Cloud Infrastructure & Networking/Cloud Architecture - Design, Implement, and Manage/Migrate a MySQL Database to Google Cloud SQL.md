# Migrate a MySQL Database to Google Cloud SQL

https://www.skills.google/course_templates/640/labs/613295

## Challenge scenario

Your WordPress blog is running on a server that is no longer suitable. As the first part of a complete migration exercise, you are migrating the locally hosted database used by the blog to Cloud SQL.

The existing WordPress installation is installed in the `/var/www/html/wordpress` directory in the instance called `blog` that is already running in the lab. You can access the blog by opening a web browser and pointing to the external IP address of the blog instance.

The existing database for the blog is provided by MySQL running on the same server. The existing MySQL database is called `wordpress` and the user called blogadmin with password `Password1*`, which provides full access to that database.

## Your challenge
1. You need to create a new Cloud SQL instance to host the migrated database.
2. Once you have created the new database and configured it, you can then create a database dump of the existing database and import it into Cloud SQL.
3. When the data has been migrated, you will then reconfigure the blog software to use the migrated database.

For this lab, the WordPress site configuration file is located here: `/var/www/html/wordpress/wp-config.php`.

To sum it all up, your challenge is to migrate the database to Cloud SQL and then reconfigure the application so that it no longer relies on the local MySQL database. Good luck!

> Note: Your lab activity tracking score will initially report a score of 20 points because your blog is running. If you reconfigure the blog application to use Cloud SQL database successfully, those points will remain in your grand total.
If the database has been incorrectly migrated, the "blog is running" test will fail, reducing your score by 20 points.

> Note: Use the following values for the zone and region where applicable Zone: [us-central1-b] Region: [us-central1]

## Tips and tricks
*Google Cloud SQL - How-To Guides*: The Cloud SQL documentation includes a set of [How-to guides](https://cloud.google.com/sql/docs/mysql/how-to) that provide guidance on how to create instances and databases, and how to connect applications to those databases.

*WordPress Installation and Migration*: The [WordPress Codex](https://codex.wordpress.org/Installing_WordPress) provides information on how to install, configure, and migrate WordPress sites. You will find the instructions on how to create and prepare databases for use with WordPress [here](https://codex.wordpress.org/Installing_WordPress#Detailed_Instructions).

## Task 1. Create a new Cloud SQL instance
In this task, you need to set up a new Cloud SQL instance in Google Cloud. Choose the right configurations and make sure to create the SQL instance in the Zone:[us-central1-b] and Region: [us-central1] that will be suitable for hosting the WordPress database. Make sure you understand the requirements for the database to support the WordPress blog.

```
gcloud sql instances create wordpress-db \
    --tier=db-n1-standard-1 \
    --zone=us-central1-b \
    --database-version=MYSQL_5_7 \
    --root-password=Password1*
```

## Task 2. Configure the new database
Once you've created the Cloud SQL instance, your next step is to configure the database within it. Set up the necessary database parameters, ensuring it's prepared to receive the existing WordPress database data.

1) Create the wordpress database (recommended charset/collation for WordPress)

```

gcloud sql databases create wordpress \
  --instance=wordpress-db \
  --charset=utf8mb4 \
  --collation=utf8mb4_unicode_ci

```

2) Create the DB user blogadmin (used by WordPress)

```

gcloud sql users create blogadmin \
  --instance=wordpress-db \
  --password='Password1*'

```

## Task 3. Perform a database dump and import the data
Your task here is to perform a dump of the existing wordpress MySQL database and then import this data into your newly created Cloud SQL database. This step is crucial in migrating the database effectively.

```
gcloud compute ssh blog --zone=us-central1-b
mysqldump -u blogadmin -pPassword1* wordpress > wordpress.sql

# Get the project ID to use as a unique bucket name
GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)

# Create a new bucket
gsutil mb gs://$GOOGLE_CLOUD_PROJECT

# Copy the dump file to the bucket
gsutil cp wordpress.sql gs://$GOOGLE_CLOUD_PROJECT/

gcloud auth login

SQL_SA_EMAIL=$(gcloud sql instances describe wordpress-db --format="value(serviceAccountEmailAddress)")

gsutil iam ch serviceAccount:$SQL_SA_EMAIL:objectAdmin gs://$DEVSHELL_PROJECT_ID


gcloud sql import sql wordpress-db gs://$DEVSHELL_PROJECT_ID/wordpress.sql --database=wordpress

BLOG_IP=$(gcloud compute instances describe blog --zone=us-central1-b --format='value(networkInterfaces[0].accessConfigs[0].natIP)')

gcloud sql instances patch wordpress-db --authorized-networks=$BLOG_IP/32

```

## Task 4. Reconfigure the WordPress installation
Now that the database has been migrated to Cloud SQL, you need to reconfigure the WordPress software to use this new database. This involves editing the wp-config.php file in the WordPress directory to point to the Cloud SQL database, moving away from the local MySQL database.

```
gcloud compute ssh blog --zone=us-central1-b

sudo nano /var/www/html/wordpress/wp-config.php

# Update the Database Host
/** MySQL hostname */
define('DB_HOST', '34.xxx.xxx.xxx'); 
```

## Task 5. Validate and troubleshoot
Your final task is to ensure that the WordPress blog is functioning correctly with the new Cloud SQL database. Check if the blog operates as expected and troubleshoot any issues you encounter. This step is important to confirm the success of your database migration and the overall functionality of the blog.