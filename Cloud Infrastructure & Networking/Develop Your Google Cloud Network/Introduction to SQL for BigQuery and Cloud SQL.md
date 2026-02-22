# Introduction to SQL for BigQuery and Cloud SQL

https://www.skills.google/course_templates/625/labs/592702

## Overview

SQL (Structured Query Language) is a standard language for data operations that allows you to ask questions and get insights from structured datasets. It's commonly used in database management and allows you to perform tasks like transaction record writing into relational databases and petabyte-scale data analysis.

This lab is divided into two parts: in the first half, you will learn fundamental SQL querying keywords, which you will run in BigQuery on a public dataset that contains information on London bikeshares.

In the second half, you will learn how to export subsets of the London bikeshare dataset into CSV files, which you will then upload to Cloud SQL. From there you will learn how to use Cloud SQL to create and manage databases and tables. Towards the end, you will get hands-on practice with additional SQL keywords that manipulate and edit data.

### What you'll learn
In this lab, you will learn how to:

- Read data into BigQuery.
- Execute simple queries in BigQuery to explore data.
- Export a subset of data into a CSV file and store that file in a new Cloud Storage bucket.
- Create a new Cloud SQL instance and load your exported CSV file as a new table.

## Task 1. The basics of SQL
### Databases and tables
As mentioned earlier, SQL allows you to get information from "structured datasets". Structured datasets have clear rules and formatting and often times are organized into tables, or data that's formatted in rows and columns.

An example of unstructured data would be an image file. Unstructured data is inoperable with SQL and cannot be stored in BigQuery datasets or tables (at least natively.) To work with image data (for instance), you would use a service like [Cloud Vision](https://google.qwiklabs.com/catalog_lab/1112?_gl=1*1pm926t*_ga*MTY4NTkxNTYzMi4xNzYyMzIxNjM3*_ga_2X30ZRBDSG*czE3NjgwODc5MTAkbzc1JGcxJHQxNzY4MDg5MDkwJGo1MSRsMCRoMA..), perhaps through its [API](https://google.qwiklabs.com/catalog_lab/1241?_gl=1*1pm926t*_ga*MTY4NTkxNTYzMi4xNzYyMzIxNjM3*_ga_2X30ZRBDSG*czE3NjgwODc5MTAkbzc1JGcxJHQxNzY4MDg5MDkwJGo1MSRsMCRoMA..) directly.

The following is an example of a structured dataset—a simple table:

```
User    Price   Shipped
Sean    $35     Yes
Rocky   $50     No
```

If you've had experience with Google Sheets, then the above should look quite similar. The table has columns for User, Price, and Shipped and two rows that are composed of filled in column values.

A Database is essentially a collection of one or more tables. SQL is a structured database management tool, but quite often (and in this lab) you will be running queries on one or a few tables joined together—not on whole databases.