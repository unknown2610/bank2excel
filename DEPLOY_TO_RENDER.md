# How to Deploy Backend to Render

This guide will help you deploy your Python FastAPI backend to Render.com.

## Prerequisites

1.  A [GitHub](https://github.com/) account.
2.  A [Render](https://render.com/) account.
3.  Your code pushed to a GitHub repository.

## Step 1: Prepare the Code

I have already created a `Dockerfile` in your `backend/` folder. This file tells Render how to build your application and installs necessary dependencies like **Tesseract OCR**.

**Action Required**:
-   Commit and push the new `backend/Dockerfile` to your GitHub repository.

## Step 2: Create a New Web Service on Render

1.  Log in to your [Render Dashboard](https://dashboard.render.com/).
2.  Click the **New +** button in the top right corner.
3.  Select **Web Service**.
4.  Connect your GitHub account if you haven't already.
5.  Find your `Bank2Excel` repository in the list and click **Connect**.

## Step 3: Configure the Service

Fill in the details as follows:

*   **Name**: `bank2excel-backend` (or any name you like).
*   **Region**: Choose the region closest to you (e.g., Oregon, Frankfurt).
*   **Branch**: `main` (or `master`, whichever is your default).
*   **Root Directory**: `backend`
    *   **IMPORTANT**: You MUST set this to `backend` because your Dockerfile is inside that folder.
*   **Runtime**: **Docker**
    *   Render should automatically detect this if you set the Root Directory correctly, but make sure "Docker" is selected.
*   **Instance Type**: Select **Free** (if available) or **Starter**.

## Step 4: Deploy

1.  Scroll down and click **Create Web Service**.
2.  Render will start building your app. You can watch the logs.
    *   It will install Python, Tesseract, and all your dependencies.
3.  Once the build finishes, you will see a green "Live" badge.
4.  Your backend URL will be displayed at the top (e.g., `https://bank2excel-backend.onrender.com`).

## Step 5: Test the Backend

You can test if it's working by visiting the docs URL:
`https://<YOUR-APP-URL>.onrender.com/docs`

You should see the Swagger UI for your FastAPI app.

## Troubleshooting

*   **Build Failed**: Check the logs. If it says "file not found", ensure "Root Directory" is set to `backend`.
*   **Tesseract Error**: If you see errors related to Tesseract, ensure the `Dockerfile` was successfully built and that you selected "Docker" as the runtime, not "Python 3".
