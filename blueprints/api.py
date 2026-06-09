from flask import Blueprint, jsonify, request
from extensions import db
from models import Contact, Deal, Note, ActivityLog, log_activity
from auth import login_required
from sqlalchemy import func
from datetime import date as date_type, datetime

api_bp = Blueprint("api", __name__)


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})


# --- CONTACTS ---

@api_bp.route("/contacts", methods=["GET"])
@login_required
def list_contacts():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    query = Contact.query

    if q:
        search = f"%{q}%"
        query = query.filter(
            db.or_(
                Contact.name.ilike(search),
                Contact.email.ilike(search),
                Contact.company.ilike(search),
                Contact.phone.ilike(search),
            )
        )
    if status:
        query = query.filter(Contact.status == status)

    contacts = query.order_by(Contact.created_at.desc()).all()
    return jsonify([c.to_dict() for c in contacts])


@api_bp.route("/contacts", methods=["POST"])
@login_required
def create_contact():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    contact = Contact(
        name=data["name"],
        email=data.get("email"),
        phone=data.get("phone"),
        company=data.get("company"),
        status=data.get("status", "Lead"),
        lead_source=data.get("lead_source", "Other"),
        lead_type=data.get("lead_type", "Buyer"),
        property_interests=data.get("property_interests"),
    )
    db.session.add(contact)
    db.session.flush()
    log_activity("contact_created", f"Created contact: {contact.name}", contact_id=contact.id)
    db.session.commit()
    return jsonify(contact.to_dict()), 201


@api_bp.route("/contacts/<int:contact_id>", methods=["GET"])
@login_required
def get_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = contact.to_dict()
    data["notes"] = [n.to_dict() for n in contact.notes]
    data["deals"] = [d.to_dict() for d in contact.deals]
    return jsonify(data)


@api_bp.route("/contacts/<int:contact_id>", methods=["PUT"])
@login_required
def update_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()

    for field in ["name", "email", "phone", "company", "status",
                  "lead_source", "lead_type", "property_interests"]:
        if field in data:
            setattr(contact, field, data[field])

    log_activity("contact_updated", f"Updated contact: {contact.name}", contact_id=contact.id)
    db.session.commit()
    return jsonify(contact.to_dict())


@api_bp.route("/contacts/<int:contact_id>", methods=["DELETE"])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    name = contact.name
    db.session.delete(contact)
    log_activity("contact_deleted", f"Deleted contact: {name}")
    db.session.commit()
    return jsonify({"message": f"Contact '{name}' deleted"})


# --- NOTES ---

@api_bp.route("/contacts/<int:contact_id>/notes", methods=["GET"])
@login_required
def list_notes(contact_id):
    Contact.query.get_or_404(contact_id)
    notes = Note.query.filter_by(contact_id=contact_id).order_by(Note.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])


@api_bp.route("/contacts/<int:contact_id>/notes", methods=["POST"])
@login_required
def create_note(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    if not data or not data.get("content"):
        return jsonify({"error": "Content is required"}), 400

    note = Note(contact_id=contact_id, content=data["content"])
    db.session.add(note)
    log_activity("note_added", f"Added note to {contact.name}", contact_id=contact_id)
    db.session.commit()
    return jsonify(note.to_dict()), 201


# --- DEALS ---

@api_bp.route("/deals", methods=["GET"])
@login_required
def list_deals():
    stage = request.args.get("stage", "").strip()
    query = Deal.query
    if stage:
        query = query.filter(Deal.stage == stage)
    deals = query.order_by(Deal.created_at.desc()).all()
    return jsonify([d.to_dict() for d in deals])


@api_bp.route("/deals", methods=["POST"])
@login_required
def create_deal():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    close_date = data.get("expected_close_date")
    if close_date and isinstance(close_date, str):
        close_date = date_type.fromisoformat(close_date)

    deal = Deal(
        title=data["title"],
        contact_id=data.get("contact_id"),
        value=data.get("value", 0),
        stage=data.get("stage", "New Lead"),
        expected_close_date=close_date,
    )
    db.session.add(deal)
    db.session.flush()

    contact_name = deal.contact.name if deal.contact else "No contact"
    log_activity("deal_created", f"Created deal: {deal.title} ({contact_name})", contact_id=deal.contact_id, deal_id=deal.id)
    db.session.commit()
    return jsonify(deal.to_dict()), 201


@api_bp.route("/deals/<int:deal_id>", methods=["PUT"])
@login_required
def update_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    data = request.get_json()

    if "title" in data:
        deal.title = data["title"]
    if "contact_id" in data:
        deal.contact_id = data["contact_id"]
    if "value" in data:
        deal.value = data["value"]
    if "stage" in data:
        old_stage = deal.stage
        deal.stage = data["stage"]
        if old_stage != deal.stage:
            log_activity("deal_moved", f"Moved '{deal.title}' from {old_stage} to {deal.stage}", contact_id=deal.contact_id, deal_id=deal.id)
    if "expected_close_date" in data:
        close_date = data["expected_close_date"]
        if close_date and isinstance(close_date, str):
            close_date = date_type.fromisoformat(close_date)
        deal.expected_close_date = close_date
    if "won_lost_reason" in data:
        deal.won_lost_reason = data["won_lost_reason"]

    db.session.commit()
    return jsonify(deal.to_dict())


@api_bp.route("/deals/<int:deal_id>", methods=["DELETE"])
@login_required
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    title = deal.title
    db.session.delete(deal)
    log_activity("deal_deleted", f"Deleted deal: {title}")
    db.session.commit()
    return jsonify({"message": f"Deal '{title}' deleted"})


@api_bp.route("/deals/<int:deal_id>/stage", methods=["PATCH"])
@login_required
def move_deal_stage(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    data = request.get_json()
    new_stage = data.get("stage")

    valid_stages = ["New Lead", "Contacted", "Proposal", "Negotiation", "Won", "Lost"]
    if new_stage not in valid_stages:
        return jsonify({"error": f"Invalid stage. Must be one of: {valid_stages}"}), 400

    old_stage = deal.stage
    deal.stage = new_stage
    log_activity("deal_moved", f"Moved '{deal.title}' from {old_stage} to {new_stage}", contact_id=deal.contact_id, deal_id=deal.id)
    db.session.commit()
    return jsonify(deal.to_dict())


# --- DASHBOARD STATS ---

@api_bp.route("/dashboard-stats", methods=["GET"])
@login_required
def dashboard_stats():
    total_contacts = Contact.query.count()
    total_leads = Contact.query.filter(Contact.status == "Lead").count()

    pipeline_value = db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
        Deal.stage.notin_(["Won", "Lost"])
    ).scalar()

    total_revenue = db.session.query(func.coalesce(func.sum(Deal.value), 0)).filter(
        Deal.stage == "Won"
    ).scalar()

    stages = ["New Lead", "Contacted", "Proposal", "Negotiation", "Won", "Lost"]
    deals_by_stage = {}
    for stage in stages:
        deals_by_stage[stage] = Deal.query.filter(Deal.stage == stage).count()

    recent = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()

    return jsonify({
        "total_contacts": total_contacts,
        "total_leads": total_leads,
        "pipeline_value": float(pipeline_value),
        "total_revenue": float(total_revenue),
        "deals_by_stage": deals_by_stage,
        "recent_activity": [a.to_dict() for a in recent],
    })


# --- AI CHATBOT ---

@api_bp.route("/chat", methods=["POST"])
@login_required
def chat_endpoint():
    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"error": "Message is required"}), 400

    from chatbot import chat
    result = chat(
        user_message=data["message"],
        history=data.get("history", []),
    )
    return jsonify(result)


# --- AI FOLLOW-UP EMAIL GENERATOR (Feature 1) ---

@api_bp.route("/generate-email", methods=["POST"])
@login_required
def generate_email():
    """Generate a personalized follow-up email in Danielle's voice.

    Accepts either an existing contact_id (details are pulled from the DB and
    last_contact_at is stamped) or raw lead fields typed into the form.
    """
    from services.ai_email import generate_followup_email

    data = request.get_json() or {}
    contact = None

    if data.get("contact_id"):
        contact = Contact.query.get_or_404(data["contact_id"])
        name = contact.name
        lead_source = contact.lead_source
        lead_type = contact.lead_type
        # Form may override the lead's stored stage/notes for this email
        stage = data.get("stage") or contact.status
        notes = data.get("notes") if data.get("notes") is not None else contact.property_interests
    else:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "A lead name is required"}), 400
        lead_source = data.get("lead_source")
        lead_type = data.get("lead_type")
        stage = data.get("stage") or "Lead"
        notes = data.get("notes")

    try:
        result = generate_followup_email(
            name=name, lead_source=lead_source, lead_type=lead_type,
            stage=stage, notes=notes,
        )
    except Exception as e:
        return jsonify({"error": f"AI generation failed: {e}"}), 500

    # Stamp last contact + log activity when generating for a saved lead
    if contact and not result.get("demo"):
        contact.last_contact_at = datetime.utcnow()
        log_activity("email_generated", f"Generated follow-up email for {contact.name}", contact_id=contact.id)
        db.session.commit()

    return jsonify(result)


# --- SEND EMAIL VIA GMAIL ---

@api_bp.route("/send-email", methods=["POST"])
@login_required
def send_email_endpoint():
    """Send a generated follow-up email directly from the connected Gmail."""
    from services import gmail
    from models import EmailLog

    data = request.get_json() or {}
    to = (data.get("to") or "").strip()
    subject = (data.get("subject") or "").strip()
    body = (data.get("body") or "").strip()

    if not to or not body:
        return jsonify({"error": "A recipient email and a message body are required"}), 400
    if not gmail.is_connected():
        return jsonify({"error": "Gmail is not connected. Click 'Connect Gmail' first."}), 400

    try:
        msg_id = gmail.send_email(to, subject or "(no subject)", body)
    except Exception as e:
        return jsonify({"error": f"Send failed: {e}"}), 500

    contact = Contact.query.get(data["contact_id"]) if data.get("contact_id") else None
    db.session.add(EmailLog(
        contact_id=(contact.id if contact else None),
        to_email=to, subject=subject or "(no subject)", status="sent",
    ))
    if contact:
        contact.last_contact_at = datetime.utcnow()
        log_activity("email_sent", f"Sent email to {contact.name} via Gmail", contact_id=contact.id)
    db.session.commit()

    return jsonify({"status": "sent", "id": msg_id})


@api_bp.route("/upload-headshot", methods=["POST"])
@login_required
def upload_headshot():
    """Upload a headshot photo for reference image generation."""
    from models import Setting
    from services.r2_storage import upload_headshot as r2_upload_headshot, is_configured as r2_configured

    if "headshot" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["headshot"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    file_data = file.read()
    filename = file.filename

    if r2_configured():
        try:
            result = r2_upload_headshot(file_data, filename)
            url = result.get("url", "")
            Setting.set("HEADSHOT_URL", url)
            return jsonify({"url": url})
        except Exception as e:
            return jsonify({"error": f"R2 upload failed: {str(e)}"}), 500
    else:
        # Save locally if R2 not configured
        import os, uuid
        ext = os.path.splitext(filename)[1] or ".jpg"
        local_name = f"headshot-{uuid.uuid4().hex[:8]}{ext}"
        local_path = os.path.join("static", "uploads", local_name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(file_data)
        url = f"/static/uploads/{local_name}"
        Setting.set("HEADSHOT_URL", url)
        return jsonify({"url": url})
