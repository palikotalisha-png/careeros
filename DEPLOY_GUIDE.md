# Deploying CareerOS — Step-by-Step Guide (Vercel + Vercel)

This gets your app a real, shareable link, using only accounts you already have:
**GitHub** (stores your code) and **Vercel** (runs both the website and the backend).

You'll create **two separate Vercel projects** from the same GitHub repo — one for the
frontend (the website), one for the backend (the engine behind it). That's normal and
expected, not a mistake.

Keep this guide open in one window and follow along in another. Takes about 10-15 minutes.

---

## Part 1 — Put your code on GitHub

1. Go to [github.com/new](https://github.com/new) and create a new repository.
   - Name it `careeros` (or anything you like)
   - Leave it **empty** — don't check "Add a README"
   - Click **Create repository**

2. Open a terminal on your computer, go to your LaunchPath folder, and run these one at a
   time:

   ```
   cd path/to/LaunchPath
   git init
   git add .
   git commit -m "CareerOS app"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/careeros.git
   git push -u origin main
   ```

   Replace `YOUR-USERNAME` with your GitHub username and `path/to/LaunchPath` with the real
   folder path on your computer.

3. Refresh the GitHub page — you should see all your files there. ✅

---

## Part 2 — Deploy the backend (Vercel project #1)

The backend is the "engine" — logins, resume analysis, the database, everything behind the
scenes.

1. Go to [vercel.com/new](https://vercel.com/new) and import your `careeros` GitHub repo.
2. Before deploying, click **Edit** next to "Root Directory" and set it to **`backend`**.
3. Expand **Environment Variables** and add:

   | Name | Value |
   |---|---|
   | `SECRET_KEY` | any random string, e.g. `careeros-super-secret-2026` |
   | `FRONTEND_ORIGIN` | `http://localhost:3000` (you'll fix this in Part 5) |
   | `ENABLED_ADAPTERS` | `sample` |

   Leave `OPENAI_API_KEY` out — the app runs fully on its built-in mock AI without it.

4. Click **Deploy**. It will likely **fail or error on first load** — that's expected, because
   there's no database connected yet. Continue to the next step regardless.

5. Once the project exists, go to its dashboard → **Storage** tab → **Create Database** →
   choose **Neon** (Postgres) → follow the prompts to create and connect it. Vercel will
   automatically add a database connection variable to your project.

6. Go to **Settings** → **Environment Variables** and check what got added by the database
   step. Find the variable holding the connection string (commonly `DATABASE_URL` or
   `POSTGRES_URL`) and copy its value into a variable literally named **`DATABASE_URL`** if
   one doesn't already exist with that exact name — the app specifically looks for
   `DATABASE_URL`.

7. Go to **Deployments** → click the **⋯** menu on the latest deployment → **Redeploy**.

8. Once it succeeds, copy the project's URL from the top of the dashboard
   (e.g. `careeros-backend.vercel.app`) — **you'll need this in Part 3.**

---

## Part 3 — Deploy the frontend (Vercel project #2)

1. Go to [vercel.com/new](https://vercel.com/new) again and import the **same** `careeros`
   GitHub repo a second time.
2. Set root directory to **`frontend`**.
3. Expand **Environment Variables** and add:

   | Name | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | your backend URL from Part 2, step 8 (include `https://`) |

4. Click **Deploy**. Wait about a minute.
5. When it finishes, copy the resulting URL (e.g. `careeros.vercel.app`) —
   **this is your app's link.** 🎉

---

## Part 4 — Connect them (fix CORS)

Right now the backend only trusts requests from `localhost`, so the live site won't fully
work yet.

1. Go to your **backend** Vercel project → **Settings** → **Environment Variables**.
2. Edit `FRONTEND_ORIGIN` and change it to your frontend URL from Part 3
   (e.g. `https://careeros.vercel.app`).
3. Go to **Deployments** → **⋯** → **Redeploy** on the backend project.

---

## Part 5 — Try it out

1. Open your frontend URL (from Part 3) in a browser.
2. Click **Sign up** and create an account with any email/password.
3. Upload a resume, paste a job description, and try **Analyze Job**.

If something doesn't load: the most common cause is a mismatch between the two URLs — check
Part 2 step 8 and Part 4 step 2 match exactly (`https://`, no trailing slash), and confirm
`DATABASE_URL` is actually set on the backend project (Part 2, step 6).

---

## If you get stuck

Tell me exactly which step you're on and what error or screen you're seeing, and I'll help
you debug it.
