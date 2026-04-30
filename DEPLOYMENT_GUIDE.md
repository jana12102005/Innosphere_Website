# InnoSphere — Render Deployment Guide

## Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "InnoSphere initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/innosphere.git
git push -u origin main
```

> ⚠️ Make sure `.env` is in `.gitignore` — never push real secrets.

---

## Step 2 — Create Web Service on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repo
3. Set these settings:

| Setting | Value |
|---|---|
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Instance Type** | Free |

---

## Step 3 — Add Environment Variables in Render Dashboard

Go to your service → **Environment** tab → Add these:

| Key | Value |
|---|---|
| `SECRET_KEY` | (click Generate) |
| `DEBUG` | `false` |
| `MYSQL_HOST` | `mysql-3dce1d9e-innosphere25-1da9.a.aivencloud.com` |
| `MYSQL_PORT` | `14019` |
| `MYSQL_DB` | `defaultdb` |
| `MYSQL_USER` | `avnadmin` |
| `MYSQL_PASSWORD` | your Aiven password |
| `SMTP_EMAIL` | `innosphere25@gmail.com` |
| `SMTP_PASSWORD` | your Gmail App Password |
| `ADMIN_EMAIL` | `innosphere.admin@gmail.com` |
| `GROQ_API_KEY` | your Groq key |
| `CLOUDINARY_CLOUD_NAME` | `dgd0vqe2i` |
| `CLOUDINARY_API_KEY` | your Cloudinary key |
| `CLOUDINARY_API_SECRET` | your Cloudinary secret |

---

## Step 4 — Deploy

Click **Deploy** — Render will install packages and start the server.  
First deploy takes ~3 minutes. After that, every `git push` auto-deploys.

---

## Important Notes

- **Uploads** — All files go to Cloudinary (not local disk). Render's disk resets on every deploy, so never store uploads locally on Render.
- **Database** — Aiven MySQL is cloud-hosted, so it persists across deploys.
- **Free tier** — Render free tier spins down after 15 minutes of inactivity. First request after sleep takes ~30 seconds.
- **Logs** — View live logs in Render Dashboard → Logs tab.
