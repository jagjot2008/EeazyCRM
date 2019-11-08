from datetime import datetime
from eeazycrm import db


class LeadStatus(db.Model):
    id = db.Column(db.Integer, db.Sequence('leadstatus_id_seq'), primary_key=True)
    status_name = db.Column(db.String(40), unique=True, nullable=False)
    leads = db.relationship('Lead', backref='status', lazy=True)

    @staticmethod
    def lead_status_query():
        return LeadStatus.query

    def __repr__(self):
        return f"LeadStatus('{self.status_name}')"


class LeadSource(db.Model):
    id = db.Column(db.Integer, db.Sequence('leadsource_id_seq'), primary_key=True)
    source_name = db.Column(db.String(40), unique=True, nullable=False)
    leads = db.relationship('Lead', backref='source', lazy=True)

    @staticmethod
    def lead_source_query():
        return LeadSource.query

    def __repr__(self):
        return f"LeadSource('{self.source_name}')"


class Lead(db.Model):
    id = db.Column(db.Integer, db.Sequence('lead_id_seq'), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address_line = db.Column(db.String(40))
    addr_state = db.Column(db.String(20))
    addr_city = db.Column(db.String(20))
    post_code = db.Column(db.String(20))
    country = db.Column(db.String(20))
    company_name = db.Column(db.String(40))
    notes = db.Column(db.String(200))
    lead_source_id = db.Column(db.Integer, db.ForeignKey('lead_source.id', ondelete='SET NULL'), nullable=True)
    lead_status_id = db.Column(db.Integer, db.ForeignKey('lead_status.id', ondelete='SET NULL'), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Lead('{self.last_name}', '{self.email}', '{self.company_name}')"
