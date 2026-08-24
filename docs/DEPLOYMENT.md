# Urja Setu Deployment Guide

Follow these steps to host your Solar Power Prediction Dashboard online for free.

## Phase 1: Uploading to GitHub
1. Create a new repository on [GitHub](https://github.com/new).
2. Open your terminal in the project folder and run:
   ```bash
   git init
   git add .
   git commit -m "prepping for deployment"
   git branch -M main
   git remote add origin YOUR_REPOSITORY_URL
   git push -u origin main
   ```

## Phase 2: Deploying the Backend (Render.com)
1. Sign up/Log in to [Render.com](https://render.com/).
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository.
4. Set the following:
   - **Name**: `urja-setu-backend`
   - **Environment**: `Python`
   - **Root Directory**: `backend`
   - **Build Command**: `pip insta  ll -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**.
6. **Note your Service URL** (e.g., `https://urja-setu-backend.onrender.com`).

## Phase 3: Deploying the Frontend (Netlify)
1. Sign up/Log in to [Netlify](https://www.netlify.com/).
2. Click **Add new site** > **Import an existing project**.
3. Select GitHub and pick the `ML_and_DL_modeled_application` repository.
4. Set the following:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
5. Click **Add Environment Variables**:
   - **Key**: `VITE_API_URL`
   - **Value**: Your Render Backend URL (e.g., `https://urja-setu-backend.onrender.com`)
6. Click **Deploy Site**.

## Success!
Your dashboard is now live. Anyone with the Netlify URL can view your solar power analysis.

> [!WARNING]
> Render's free tier spins down after 15 minutes of inactivity. The first person to visit your site each day may experience a ~40 second delay while the backend wakes up.
