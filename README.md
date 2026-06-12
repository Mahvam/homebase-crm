# 🏠 HomeBase CRM

> An AI-powered CRM that helps solo real estate agents turn leads into closings — without the busywork.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Railway-Deployed-0B0D0E?logo=railway&logoColor=white" alt="Railway">
  <img src="https://img.shields.io/badge/AI-OpenRouter%20%2F%20Claude-C7A35A" alt="AI">
</p>

<p align="center">
  <a href="https://web-production-29528.up.railway.app"><strong>🔗 Live Demo</strong></a>
  ·
  <a href="#-features">Features</a>
  ·
  <a href="#-tech-stack">Tech Stack</a>
  ·
  <a href="#-getting-started">Getting Started</a>
</p>

---

## 📋 Overview

**HomeBase CRM** is a lightweight, AI-powered CRM built for solo real estate agents who are drowning in manual follow-up work. Instead of replacing an agent's existing pipeline, it layers automation on top of it — generating personalized follow-up emails in the agent's own voice, surfacing leads that need attention, and providing a conversational AI assistant that can manage the CRM through plain English.

The app is a full-stack Flask application with a modular blueprint architecture, server-rendered UI, and integrations across several third-party services. It's deployed to production on Railway with a PostgreSQL database and Cloudflare R2 object storage.

> **Built to demonstrate:** end-to-end product development — data modeling, REST API design, third-party API integration (LLMs, OAuth, object storage), production deployment, and a clean, responsive UI.

---

## 🎬 Live Demo

**▶️ [web-production-29528.up.railway.app](https://web-production-29528.up.railway.app)**

Sign in with the demo account:

| Field | Value |
|---|---|
| **Username** | `demo` |
| **Password** | `DemoAccess2025` |

---

## 📸 Screenshots

<!-- Replace the placeholder below with a real screenshot, e.g. docs/screenshot-dashboard.png -->
<p align="center">
  <img src="docs/screenshot-dashboard.png" alt="HomeBase CRM dashboard" width="100%">
  <br>
  <em>HomeBase CRM — lead dashboard &amp; AI follow-up email generator</em>
</p>

> _Screenshot placeholder — drop your image at `docs/screenshot-dashboard.png` (or update the path above)._

---

## ✨ Features

### 🤖 AI Follow-Up Email Generator
Enter a lead's details — name, source, type, and pipeline stage — and the app generates a warm, personalized follow-up email in the agent's voice using a Claude model via OpenRouter. Emails are short, natural, and ready to send. A deterministic post-processor enforces a clean, human style (no dashes, no bullet lists), keeping output consistent even when the model drifts.

### 💬 Jackie — Conversational AI Assistant
A built-in AI assistant that manages the CRM through natural language. Ask it to *"add a lead named Sarah Johnson"*, *"show me everyone in the Active Buyer stage"*, or *"how many leads came from Zillow?"* and it reads and writes to the database directly. Supports both text chat and live voice (via the OpenAI Realtime API).

### 👥 Lead Management
A full lead intake and tracking system with real estate–specific pipeline stages (Lead → Warm Nurture → Active Buyer → Under Contract → Closed), lead sourcing (Website, Zillow, Referral, etc.), buyer/seller typing, property-interest notes, and last-contact tracking. Each lead is one click away from a tailored follow-up email.

### 📊 Dashboard
An at-a-glance command center showing total leads, pipeline breakdown by stage, recent activity, and key metrics — so the agent always knows what needs attention next.

### 📧 Gmail Integration (OAuth)
Connect a Gmail account via OAuth 2.0 and send generated emails directly from the app — no copy/paste. Uses the least-privilege `gmail.send` scope; refresh tokens are stored securely server-side.

### 🎨 Custom Branding
A self-serve branding page to set primary/accent colors and upload a logo or profile photo. Changes are persisted to the database and applied dynamically across the entire app via CSS custom properties — no redeploy required.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.9+ |
| **Backend** | Flask (blueprint architecture) + SQLAlchemy ORM |
| **Database** | PostgreSQL (production) · SQLite (local dev) |
| **Frontend** | Server-rendered Jinja2 · Tailwind CSS · Alpine.js |
| **AI / LLM** | OpenRouter API (Claude / GPT models) · OpenAI Realtime API (voice) |
| **Auth** | Session-based admin auth · Google OAuth 2.0 (Gmail) |
| **File Storage** | Cloudflare R2 (S3-compatible object storage) |
| **Deployment** | Railway (PostgreSQL plugin + auto-deploy) · Gunicorn |

---

## 🏗 Architecture Highlights

- **Modular blueprints** — each feature area (leads API, admin UI, AI email, Jackie, branding, Gmail) is an isolated Flask blueprint, registered behind feature toggles.
- **Service layer** — third-party integrations (OpenRouter, Gmail, Cloudflare R2) are wrapped in dedicated, framework-agnostic service modules.
- **Resilient config** — API keys resolve from the environment first (authoritative in production) and fall back to database-stored settings, with whitespace hardening to prevent malformed auth headers across multi-worker deployments.
- **Graceful degradation** — every external integration has a demo/fallback mode, so the app stays functional even without keys configured.

---

## 🚀 Getting Started

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd homebase-crm

# 2. Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env             # then fill in your keys

# 4. Run the app
python app.py                    # http://localhost:8000
```

The database auto-creates its tables and seeds demo data on first run.

### Key environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL URL (defaults to local SQLite) |
| `OPENROUTER_API_KEY` | Powers the AI email generator and Jackie |
| `GMAIL_CLIENT_ID` / `GMAIL_CLIENT_SECRET` | Google OAuth for sending email |
| `R2_*` | Cloudflare R2 credentials for uploads |
| `BUSINESS_NAME` | Branding shown across the UI |

---

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

---

## ☁️ Deployment

Deployed on **Railway** with a PostgreSQL plugin. The `railway.toml` and `Procfile` handle the build and Gunicorn start command; environment variables are configured in the Railway dashboard. The app automatically rewrites legacy `postgres://` URLs to `postgresql://` for SQLAlchemy compatibility.

---

## 📂 Project Structure

```
app.py                  # Flask app factory — registers blueprints
models.py               # SQLAlchemy models (Contact, Setting, etc.)
blueprints/             # Feature areas (admin UI, API, Jackie, Gmail, ...)
services/               # Third-party API wrappers
  ai_email.py           #   AI follow-up email generation
  openrouter.py         #   LLM text generation
  gmail.py              #   Gmail OAuth + send
  r2_storage.py         #   Cloudflare R2 uploads
templates/              # Jinja2 templates
static/                 # CSS, JS, images
tests/                  # pytest suite
```

---

## 👤 Author

Built as a portfolio project demonstrating full-stack development, AI integration, and production deployment.

<p align="center"><em>HomeBase CRM — turn leads into closings, automatically.</em></p>
