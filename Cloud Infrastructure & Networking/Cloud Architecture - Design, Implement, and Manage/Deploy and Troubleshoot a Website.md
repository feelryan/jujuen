# Deploy and Troubleshoot a Website

https://www.skills.google/course_templates/640/labs/613296

## Challenge scenario
Your company is ready to launch a brand new product! Because you are entering a totally new space, you have decided to deploy a new website as part of the product launch. The new site is complete, but the person who built the new site left the company before they could deploy it.

### Your challenge
Your challenge is to deploy the site in the public cloud by completing the tasks below. You will use a simple Apache web server as a placeholder for the new site in this exercise. Good luck!

### Running a basic Apache web server
A virtual machine instance on Compute Engine can be controlled like any standard Linux server. Deploy a simple Apache web server (a placeholder for the new product site) to learn the basics of running a server on a virtual machine instance.

## Task 1. Create a Linux VM instance
Create a Linux virtual machine, name it [tst-eng-7rp] and specify the zone as [us-central1-a].

## Task 2. Enable public access to VM instance
While creating the Linux instance, make sure to apply the appropriate firewall rules so that potential customers can find your new product.

## Task 3. Running a basic Apache Web Server
A virtual machine instance on Compute Engine can be controlled like any standard Linux server.

- Deploy a simple Apache web server (a placeholder for the new product site) to learn the basics of running a server on a virtual machine instance.

## Task 4. Test your server
- Test that your instance is serving traffic on its external IP.
You should see the "Hello World!" page (a placeholder for the new product site).

## Troubleshooting
- Receiving a Connection Refused error:
- Your VM instance is not publicly accessible because the VM instance does not have the proper tag that allows Compute Engine to apply the appropriate firewall rules, or your project does not have a firewall rule that allows traffic to your instance's external IP address.
- You are trying to access the VM using an https address. Check that your URL is http:// EXTERNAL_IP and not https:// EXTERNAL_IP.

## Solution

> gcloud compute instances create tst-eng-7rp --zone=us-central1-a

```
gcloud compute firewall-rules create allow-http \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server
```[ 1 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY0cibRQzif1VhMn9dBbQlyxnbi8obwtuNl4Id_SfSWT907VvLoklitDvkybDGXpPdUFAWznZTkWIIkm34IbmOsXYYDJpEHoDvi0dtb3lcp0GgCsyzHBi5mgu4qG4VDRiYBBsp5Nk=)][ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb7KvJgxoqIEu0lb6By5Q2FYdYN-GdpR1mbcRUt1P3jXewX8XLQajHOI8Ao8PKT8z3fRgZ9CMZoqeZc4edmN_lQGMJoU3gtyam0oERnjvRa8dfvCrJdZjRsjRTzQ6p3X6e6wEn0tiSOvDKNdGEqKoc4nW4qyWXtjpZjxCb5I2_TFEGj9fPSHRSLL_xPedcIqh3DR9LOd6y-veRXg==)]

### 2. Add the tag to your VM
This command adds the `http-server` tag to your existing `tst-eng-7rp` instance so the firewall rule applies to it.[ 1 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY0cibRQzif1VhMn9dBbQlyxnbi8obwtuNl4Id_SfSWT907VvLoklitDvkybDGXpPdUFAWznZTkWIIkm34IbmOsXYYDJpEHoDvi0dtb3lcp0GgCsyzHBi5mgu4qG4VDRiYBBsp5Nk=)][ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb7KvJgxoqIEu0lb6By5Q2FYdYN-GdpR1mbcRUt1P3jXewX8XLQajHOI8Ao8PKT8z3fRgZ9CMZoqeZc4edmN_lQGMJoU3gtyam0oERnjvRa8dfvCrJdZjRsjRTzQ6p3X6e6wEn0tiSOvDKNdGEqKoc4nW4qyWXtjpZjxCb5I2_TFEGj9fPSHRSLL_xPedcIqh3DR9LOd6y-veRXg==)]

```bash
gcloud compute instances add-tags tst-eng-7rp --tags=http-server --zone=us-central1-a
```[ 1 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY0cibRQzif1VhMn9dBbQlyxnbi8obwtuNl4Id_SfSWT907VvLoklitDvkybDGXpPdUFAWznZTkWIIkm34IbmOsXYYDJpEHoDvi0dtb3lcp0GgCsyzHBi5mgu4qG4VDRiYBBsp5Nk=)][ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb7KvJgxoqIEu0lb6By5Q2FYdYN-GdpR1mbcRUt1P3jXewX8XLQajHOI8Ao8PKT8z3fRgZ9CMZoqeZc4edmN_lQGMJoU3gtyam0oERnjvRa8dfvCrJdZjRsjRTzQ6p3X6e6wEn0tiSOvDKNdGEqKoc4nW4qyWXtjpZjxCb5I2_TFEGj9fPSHRSLL_xPedcIqh3DR9LOd6y-veRXg==)]

gcloud compute ssh tst-eng-7rp --zone=us-central1-a
```[ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOmpQwE4o5XzNFXpDPTZBPH8FGAMLC0wwJOcPtWb2TUFvjADkiiRd8-Fm_LlIT8ZNdBWRghq9XWhtfYf9lcDmPgUuvQoxa8gf9IHi9Ft2xUtVemcHXxm4-fAuZN-WzLGBCVtsfUwM=)]

### 2. Install Apache
Once you are logged in (your command prompt will change to `student-ID@tst-eng-7rp:~$`), run these standard Linux commands to update your package manager and install Apache:

```bash
sudo apt-get update
sudo apt-get install apache2 -y
```[ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOmpQwE4o5XzNFXpDPTZBPH8FGAMLC0wwJOcPtWb2TUFvjADkiiRd8-Fm_LlIT8ZNdBWRghq9XWhtfYf9lcDmPgUuvQoxa8gf9IHi9Ft2xUtVemcHXxm4-fAuZN-WzLGBCVtsfUwM=)][ 3 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6sKut1snQYUHaZvAkS4ZSAeDlbz0aKytpgrt89nkMOi1u5yBZtTpTRc5tIAO9DoyJPvBS9V6cvVEmmEVdZRgeTJgmLROh_Rxd-gVL1aaC5F5Nks5O6XwYRif3IcYqWmF0UBVcQJqcDnwMkj6gB0ecHBY76t4vklw55cyM-8XXsu2TKH3Gitu-bzZBprRPvNn75w==)]

### 3. Verify and Exit
Apache usually starts automatically.[ 1 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGPM9168szZ_CpcMKEiuZtBgQkakodPFJVlWn4xgNB1eoKn08OkU8ncl9Z79sk4FcIaTwc9N5Zy2s_pSCI0ae45F19W0T1jIOS8W74rRvDF63d7pmu-6aHeNT4l_Wvby-eWGtuLbjV2CMoO_4twtKqE6UX231-GYzpTjqJUAqGtgKY6TS7WA==)][ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOmpQwE4o5XzNFXpDPTZBPH8FGAMLC0wwJOcPtWb2TUFvjADkiiRd8-Fm_LlIT8ZNdBWRghq9XWhtfYf9lcDmPgUuvQoxa8gf9IHi9Ft2xUtVemcHXxm4-fAuZN-WzLGBCVtsfUwM=)] You can verify it is active with `sudo service apache2 status` (press `q` to quit the status view).[ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOmpQwE4o5XzNFXpDPTZBPH8FGAMLC0wwJOcPtWb2TUFvjADkiiRd8-Fm_LlIT8ZNdBWRghq9XWhtfYf9lcDmPgUuvQoxa8gf9IHi9Ft2xUtVemcHXxm4-fAuZN-WzLGBCVtsfUwM=)] 

To leave the VM and return to the main Cloud Shell, type:
```bash
exit
```[ 2 (https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOmpQwE4o5XzNFXpDPTZBPH8FGAMLC0wwJOcPtWb2TUFvjADkiiRd8-Fm_LlIT8ZNdBWRghq9XWhtfYf9lcDmPgUuvQoxa8gf9IHi9Ft2xUtVemcHXxm4-fAuZN-WzLGBCVtsfUwM=)]