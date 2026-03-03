# 🚀 Deployment Guide

## Step 1 — Push to GitHub

### Option A: GitHub CLI (easiest)
```bash
# Install GitHub CLI if needed: https://cli.github.com
gh auth login
gh repo create solar-yield-india --public --source=. --remote=origin --push
```

### Option B: Manual via GitHub website
1. Go to https://github.com/new
2. Repository name: `solar-yield-india`
3. Set to **Public**
4. **Do NOT** initialize with README (we already have one)
5. Click **Create repository**
6. Then run these commands in your terminal:

```bash
git remote add origin https://github.com/YOUR-USERNAME/solar-yield-india.git
git push -u origin main
```

---

## Step 2 — Deploy Online (pick one)

### 🟢 GitHub Pages (Free — recommended)
After pushing to GitHub:
1. Go to your repo on GitHub
2. Click **Settings** → **Pages** (left sidebar)
3. Under "Source" → select **GitHub Actions**
4. That's it! Your site will be live at:
   `https://YOUR-USERNAME.github.io/solar-yield-india`

The `.github/workflows/deploy.yml` file automatically deploys on every push.

---

### 🟣 Netlify (Free — easiest, custom domain)

**Option A — Drag & Drop (30 seconds):**
1. Go to https://app.netlify.com/drop
2. Drag the entire `solar-yield-india` folder onto the page
3. Get instant URL like `https://random-name.netlify.app`
4. Optionally add custom domain in site settings

**Option B — Git integration (auto-deploys on push):**
1. Go to https://app.netlify.com → "Add new site" → "Import from Git"
2. Connect GitHub → select `solar-yield-india` repo
3. Build command: *(leave empty)*
4. Publish directory: `.`
5. Click **Deploy site**

---

### 🔵 Vercel (Free — fastest CDN)
```bash
npm install -g vercel
cd solar-yield-india
vercel --yes
```
Follow the prompts. Your app will be live at `https://solar-yield-india.vercel.app`

---

## Step 3 — Update your live site

Whenever you make changes:
```bash
git add .
git commit -m "Update: describe your changes"
git push
```
GitHub Pages and Netlify/Vercel will **auto-redeploy** within 1-2 minutes.

---

## 📌 Quick Reference

| Platform | URL Pattern | Auto-deploy | Custom Domain |
|---|---|---|---|
| GitHub Pages | `username.github.io/repo-name` | ✅ Yes | ✅ Yes (free) |
| Netlify | `app-name.netlify.app` | ✅ Yes | ✅ Yes (free) |
| Vercel | `app-name.vercel.app` | ✅ Yes | ✅ Yes (free) |

