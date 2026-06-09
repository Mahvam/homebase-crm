"""
services/ai_email.py — AI Follow-Up Email Generator
====================================================
Feature 1 from Danielle's CRM brief.

Generates a personalized, warm follow-up email in Danielle's voice based on a
lead's details (name, source, type, pipeline stage, and what they're looking
for). Uses OpenRouter (same pattern as services/openrouter.py) routed to a
Claude model, so it works with the OPENROUTER_API_KEY the rest of the app
already uses.

Falls back to a friendly demo email when no API key is configured, so the page
always works during a live demo.
"""

import os
import re
from openai import OpenAI

# Claude via OpenRouter. The brief asked for Claude (claude-sonnet-4); on
# OpenRouter that model id is "anthropic/claude-sonnet-4".
DEFAULT_MODEL = "anthropic/claude-sonnet-4"

# What each pipeline stage means, so the AI knows the right tone/intent.
STAGE_GUIDANCE = {
    "Lead": "This is a brand-new lead who just came in. Introduce yourself warmly, thank them for reaching out, and offer to help with no pressure.",
    "Warm Nurture": "This lead has shown some interest but isn't ready yet. Stay top-of-mind, be helpful, and gently keep the door open.",
    "Active Buyer": "This person has signed a buyer agency agreement and is actively looking. Be proactive and concrete about next steps.",
    "Under Contract": "This deal is under contract. Reassure them, keep them informed, and check in on next milestones (inspection, title, closing).",
    "Closed": "This deal has closed. Congratulate them, thank them sincerely, and softly invite referrals or a future review.",
}


def _get_client():
    """OpenAI client pointed at OpenRouter, or None if no key is set."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
            "X-Title": "Danielle's AI CRM",
        },
    )


def _clean_email(text):
    """Safety net enforcing 'no dashes, no bullets' even if the model slips.

    Danielle wants emails that read as plain, natural paragraphs. This strips
    any list markers and removes every kind of dash (em, en, hyphen) without
    touching paragraph breaks.
    """
    lines = [re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", ln) for ln in text.split("\n")]
    text = "\n".join(lines)
    text = text.replace("—", ", ").replace("–", ", ")  # em / en dash -> comma
    text = re.sub(r"(?<=\w)-(?=\w)", " ", text)                  # compound-word hyphen -> space
    text = text.replace("-", " ")                                # any leftover hyphen
    text = re.sub(r"[ \t]{2,}", " ", text)                       # collapse spaces (keep newlines)
    text = re.sub(r" +([,.!?])", r"\1", text)                    # tidy space before punctuation
    text = re.sub(r",\s*,", ", ", text)                          # tidy doubled commas
    return text.strip()


def _demo_email(name):
    """Friendly placeholder shown when no OpenRouter key is configured."""
    first = (name or "there").split()[0]
    return {
        "email": (
            f"Hi {first},\n\n"
            "It was so nice connecting with you! I'd love to help you find the "
            "right home here in St. Joseph — no pressure at all, just here whenever "
            "you're ready.\n\n"
            "Want to grab a quick call this week to chat about what you're looking for?\n\n"
            "Warmly,\nDanielle\n\n"
            "— — —\n"
            "(Demo mode: add your OpenRouter API key in Settings to generate real, "
            "personalized emails in Danielle's voice.)"
        ),
        "model": "demo",
        "demo": True,
    }


def generate_followup_email(name, lead_source=None, lead_type=None,
                            stage="Lead", notes=None):
    """
    Generate a personalized follow-up email for a lead.

    Args:
        name:        Lead's name
        lead_source: Where they came from (Website, Zillow, DNA, Referral, Brokerage)
        lead_type:   Buyer or Seller
        stage:       Pipeline stage (Lead, Warm Nurture, Active Buyer, Under Contract, Closed)
        notes:       What they're looking for / any context

    Returns:
        dict with: email (text), model, demo (bool)
    """
    client = _get_client()
    if not client:
        return _demo_email(name)

    stage_note = STAGE_GUIDANCE.get(stage, STAGE_GUIDANCE["Lead"])

    system_prompt = (
        "You are Danielle, a warm and friendly solo real estate agent based in "
        "St. Joseph, Missouri. You are writing a follow-up email to a lead.\n\n"
        "RULES:\n"
        "- Write in a warm, friendly, conversational tone, never corporate or salesy.\n"
        "- Sound like a real person, not a template.\n"
        "- Reference the specific details you're given (name, what they're looking for).\n"
        "- Keep it SHORT: 3 to 5 sentences max.\n"
        "- End with a soft, low-pressure call to action.\n"
        "- Sign off as Danielle.\n"
        "- NEVER use dashes of any kind: no em dashes, no en dashes, and no hyphens "
        "even in compound words (write 'four bedroom home', not 'four-bedroom home'; "
        "write 'pre approved', not 'pre-approved'). Rephrase to avoid them entirely.\n"
        "- NEVER use bullet points, numbered lists, or any list formatting. Write "
        "everything as natural flowing sentences and paragraphs only.\n\n"
        "OUTPUT FORMAT: Return ONLY the email body text (a greeting, the message, "
        "and the sign-off). No subject line, no explanations, no preamble."
    )

    details = [f"Lead name: {name}"]
    if lead_source:
        details.append(f"Lead source: {lead_source}")
    if lead_type:
        details.append(f"Lead type: {lead_type}")
    if stage:
        details.append(f"Pipeline stage: {stage}")
    if notes:
        details.append(f"Notes: {notes}")

    user_prompt = (
        "Write a follow-up email for this lead.\n\n"
        + "\n".join(details)
        + f"\n\nContext for this stage: {stage_note}"
    )

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        temperature=0.8,
    )

    text = _clean_email(response.choices[0].message.content.strip())
    return {"email": text, "model": DEFAULT_MODEL, "demo": False}
