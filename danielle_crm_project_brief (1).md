# Danielle's AI CRM — Project Brief

## What We're Building
A lightweight AI-powered CRM tool built on top of Danielle's existing Follow Up Boss workflow. The goal is to **add an AI layer** that automates the manual tasks that are eating up her time as a solo real estate agent.

We are NOT replacing Follow Up Boss. We are building a companion tool that makes her existing process smarter and faster.

---

## Who This Is For
- **Danielle** — solo real estate agent based in St. Joseph, MO
- Not very technical, so the UI must be simple and clean
- Her biggest pain: everything is manual and she doesn't have time

---

## Her Current Tools
| Tool | What She Uses It For |
|---|---|
| Follow Up Boss | Main CRM — tracks leads, pipeline stages, drip campaigns |
| Minichat | Automates DMs on social media |
| Sierra Interactive | Brokerage website CRM (she doesn't control this one) |
| Gmail | Linked to Follow Up Boss for lead capture |
| Vidyard | Screen recording |
| athomeinstjoe.com | Her personal website — newsletter signups live here |

---

## Her Lead Sources
1. **Her website** — newsletter signups and contact forms
2. **Zillow** — old cold leads she imported into Follow Up Boss
3. **DNA leads** — home evaluation requests via QR code
4. **Brokerage site** — Sierra Interactive leads forwarded to her manually by Christie
5. **Referrals / direct** — people she knows, added manually

---

## Her Pipeline Stages (in Follow Up Boss)
1. **Lead** — brand new, just came in
2. **Warm Nurture** — showed some interest
3. **Active Buyer** — signed buyer agency agreement
4. **Under Contract** — offer accepted, custom fields filled in (address, contract date, inspection period, title company)
5. **Closed** — deal done

---

## What's Currently Manual (Her Pain Points)
- Tagging new leads (buyer vs seller, lead source)
- Sending the initial intro/welcome email when a lead comes in
- Sending welcome email when someone signs up for her newsletter
- Updating the weekly events page on her website
- Copying/pasting events into her Friday newsletter email
- Moving leads between pipeline stages
- Minichat is NOT yet connected to Follow Up Boss

---

## Phase 1 — What We're Building First
Start small. Nail one thing really well before expanding.

### Feature 1: AI Follow-Up Email Generator
A simple web interface where Danielle can:
1. Enter or paste basic lead info (name, lead source, what they're looking for)
2. Select the pipeline stage (Lead, Warm Nurture, Active Buyer, etc.)
3. Click a button → AI generates a personalized follow-up email in her voice
4. She reviews, edits if needed, and copies it to send

**Why this first?** It's the most immediate time saver and doesn't require any integration to be useful on day one.

---

### Feature 2: Lead Intake Form
A simple form that captures:
- Lead name
- Contact info (email, phone)
- Lead source (Website, Zillow, DNA, Referral, Brokerage)
- Lead type (Buyer or Seller)
- Pipeline stage
- Notes / property interests

Saves to a local database (SQLite to start).

---

### Feature 3: Lead Dashboard
A simple table/list view showing:
- All leads
- Their pipeline stage
- Last contact date
- A button to generate a follow-up email for each one

---

## Tech Stack (Beginner Friendly)
| Layer | Tool |
|---|---|
| Frontend | HTML + CSS + JavaScript (keep it simple) |
| Backend | Python with Flask |
| Database | SQLite (simple, no setup needed) |
| AI | Anthropic Claude API (claude-sonnet-4-20250514) |
| Environment | Warp terminal + Claude Code |

---

## AI Email Generation — System Prompt Direction
When generating follow-up emails, the AI should:
- Write in a warm, friendly, conversational tone (not corporate)
- Sound like a real person, not a template
- Reference specific details about the lead (name, what they're looking for)
- Keep emails short — 3 to 5 sentences max
- End with a soft call to action (not pushy)
- Sign off as Danielle

**Example context to pass to the AI:**
```
Lead name: Sarah
Lead source: Zillow
Lead type: Buyer
Pipeline stage: Warm Nurture
Notes: Looking for a 3 bed 2 bath in Olathe, budget around $350k, said not right now in January
```

---

## Folder Structure to Create
```
danielle-crm/
├── app.py               # Flask backend
├── database.py          # SQLite database setup
├── ai_email.py          # Claude API email generation logic
├── templates/
│   ├── index.html       # Lead dashboard
│   ├── add_lead.html    # Lead intake form
│   └── email_gen.html   # Email generator view
├── static/
│   └── style.css        # Basic styling
├── .env                 # API keys (never commit this)
├── requirements.txt     # Python dependencies
└── README.md            # Project notes
```

---

## First Prompt to Run in Claude Code
Once you open Claude Code in your project folder, start with this:

> "I am building a simple AI-powered CRM for a real estate agent. Please set up a basic Flask app with SQLite that has a lead intake form, a lead dashboard, and an AI email generator using the Anthropic API. Use the project brief in this folder as your guide. Start with the folder structure and requirements.txt."

---

## Future Features (Phase 2 — Do Not Build Yet)
- Follow Up Boss API integration (read/write leads directly)
- Minichat → Follow Up Boss connection
- Automated weekly newsletter email builder
- DNA lead auto-response
- Cold lead re-engagement scheduler

---

## Notes for the Builder (Mahva)
- Get Danielle's screen recording walkthrough before Phase 2
- Get a sample follow-up email from Danielle to fine-tune the AI voice
- Keep the UI dead simple — Danielle is not technical
- Build in public so Danielle can see progress and stay engaged
- Every feature should eliminate at least one manual step for her
