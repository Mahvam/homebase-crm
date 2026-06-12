"""
seed.py — Demo data for HomeBase CRM
==========================================
Seeds a handful of realistic real-estate leads for Danielle, a solo agent in
St. Joseph, MO. Uses her Follow Up Boss pipeline stages and lead sources from
the project brief. Called automatically from app.py on an empty database.
"""

from extensions import db
from models import Contact, Note, ActivityLog
from datetime import datetime, timedelta
import random


def run_seed(drop_tables=False):
    """Seed demo leads. Called from app.py auto-seed or standalone."""
    if drop_tables:
        print("Dropping all tables...")
        db.drop_all()
        print("Recreating all tables...")
        db.create_all()

    print("Seeding Danielle's leads...")

    # name, email, phone, status (stage), lead_source, lead_type, property_interests, days_since_contact (None = never)
    leads_data = [
        ("Sarah Johnson", "sarah.j@gmail.com", "(816) 555-0142", "Warm Nurture", "Zillow", "Buyer",
         "Looking for a 3 bed 2 bath in St. Joseph, budget around $250k. Said 'maybe in the spring.'", 12),
        ("Mike & Tracy Reynolds", "treynolds@yahoo.com", "(816) 555-0188", "Active Buyer", "Referral", "Buyer",
         "Relocating from Kansas City. Want a 4 bedroom with a big yard, pre-approved up to $400k.", 3),
        ("Linda Carter", "lcarter@outlook.com", "(816) 555-0173", "Lead", "Website", "Seller",
         "Wants a home valuation for her place on Faraon St. Thinking about downsizing.", None),
        ("James Whitfield", "jwhitfield@gmail.com", "(816) 555-0119", "Under Contract", "Brokerage", "Buyer",
         "Offer accepted on 2412 Mitchell Ave. Inspection period ends soon, using First American Title.", 1),
        ("Ashley Nguyen", "ashley.nguyen@gmail.com", "(816) 555-0156", "Lead", "DNA", "Seller",
         "Requested a home evaluation via QR code at the open house. Owns a duplex.", None),
        ("Robert & Carol Diaz", "rdiaz@comcast.net", "(816) 555-0134", "Closed", "Referral", "Buyer",
         "Closed on their forever home in March. Great referral source — sent two friends already.", 30),
        ("Megan O'Brien", "mobrien@gmail.com", "(816) 555-0167", "Warm Nurture", "Zillow", "Buyer",
         "First-time buyer, still building credit. Wants a starter home under $180k. Check back in summer.", 21),
        ("Daniel Foster", "dfoster@hotmail.com", "(816) 555-0125", "Active Buyer", "Website", "Buyer",
         "Signed buyer agency agreement. Looking at new construction in the Cook Crossing area.", 5),
    ]

    contacts = []
    now = datetime.utcnow()
    for name, email, phone, status, source, ltype, interests, days in leads_data:
        last_contact = (now - timedelta(days=days)) if days is not None else None
        c = Contact(
            name=name, email=email, phone=phone,
            status=status, lead_source=source, lead_type=ltype,
            property_interests=interests, last_contact_at=last_contact,
            created_at=now - timedelta(days=random.randint(5, 120)),
        )
        db.session.add(c)
        contacts.append(c)
    db.session.flush()
    print(f"  {len(contacts)} leads created")

    # A couple of follow-up notes for texture
    notes_data = [
        (0, "Left a voicemail and sent a Zillow listing for a 3/2 on Ashland Ave. No reply yet."),
        (1, "Toured 3 homes Saturday. They loved the one on Pacific St — writing an offer this week."),
        (3, "Inspection scheduled. Reminded James to send earnest money to the title company."),
        (5, "Sent a thank-you card after closing. Asked for a Google review."),
    ]
    for idx, content in notes_data:
        db.session.add(Note(
            contact_id=contacts[idx].id, content=content,
            created_at=now - timedelta(days=random.randint(1, 20)),
        ))

    for c in contacts:
        db.session.add(ActivityLog(
            action_type="contact_created",
            description=f"Added lead: {c.name}",
            contact_id=c.id,
            created_at=c.created_at,
        ))

    db.session.commit()

    print("\n" + "=" * 50)
    print("SEED COMPLETE")
    print(f"  Leads: {len(contacts)}")
    print(f"  Notes: {len(notes_data)}")
    print("=" * 50)


if __name__ == "__main__":
    from app import app
    with app.app_context():
        run_seed(drop_tables=True)
