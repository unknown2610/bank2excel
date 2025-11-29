# How to Deploy Backend to Google Cloud Run

This guide will help you deploy your Python FastAPI backend to **Google Cloud Run**.

## Prerequisites

1.  A [Google Cloud Platform (GCP)](https://console.cloud.google.com/) account.
2.  A Project created in GCP.
3.  [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install) installed on your machine.

## Step 1: Login and Configure gcloud

Open your terminal (PowerShell or Command Prompt) and run:

```bash
# Login to your Google account
gcloud auth login

# Set your project ID (replace YOUR_PROJECT_ID with your actual project ID)
gcloud config set project YOUR_PROJECT_ID
```

## Step 2: Enable Required Services

Enable the Cloud Run and Container Registry APIs:

```bash
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
```

## Step 3: Deploy

Run the following command from the root of your project (where `backend/` folder is):

```bash
# Submit the build to Cloud Build and deploy to Cloud Run
gcloud run deploy bank2excel-backend --source ./backend --platform managed --region us-central1 --allow-unauthenticated
```

**Explanation of flags:**
*   `--source ./backend`: Tells gcloud to look for the `Dockerfile` in the `backend` folder.
*   `--platform managed`: Uses the fully managed Cloud Run platform.
*   `--region us-central1`: Deploys to the US Central region (you can change this).
*   `--allow-unauthenticated`: Makes your API public so your frontend can access it.

## Step 4: Get Your URL

Once the deployment finishes, you will see a URL like:
`https://bank2excel-backend-xyz123-uc.a.run.app`

## Step 5: Update Frontend

1.  Copy the URL from Step 4.
2.  Open `frontend/src/App.jsx`.
3.  Update the `API_URL` (or wherever you define the backend URL) to point to your new Cloud Run URL.
    *   Example: `const API_URL = "https://bank2excel-backend-xyz123-uc.a.run.app";`
4.  Re-deploy your frontend (to Vercel or wherever it is hosted).

## Troubleshooting

*   **"Permission denied"**: Ensure you are logged in (`gcloud auth login`) and have the "Cloud Run Admin" and "Service Account User" roles.
*   **"PSSecurityException" / "running scripts is disabled"**: This is a Windows PowerShell restriction.
    *   **Solution 1**: Run the command in **Command Prompt (cmd)** instead of PowerShell.
    *   **Solution 2**: Try running `gcloud.cmd` instead of just `gcloud`.
    *   **Solution 3**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell to allow scripts.
*   **"Container failed to start"**: Check the logs in the Google Cloud Console. It might be a missing dependency or a crash on startup.
