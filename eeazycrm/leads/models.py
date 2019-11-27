from datetime import datetime
from eeazycrm import db


class LeadStatus(db.Model):
    id = db.Column(db.Integer, db.Sequence('leadstatus_id_seq'), primary_key=True)
    status_name = db.Column(db.String(40), unique=True, nullable=False)
    leads = db.relationship('Lead', backref='status', lazy=True)

    @staticmethod
    def lead_status_query():
        return LeadStatus.query

    @staticmethod
    def get_by_id(lead_status_id):
        return LeadStatus.query.filter_by(id=lead_status_id).first()

    def __repr__(self):
        return f"LeadStatus('{self.status_name}')"


class LeadSource(db.Model):
    id = db.Column(db.Integer, db.Sequence('leadsource_id_seq'), primary_key=True)
    source_name = db.Column(db.String(40), unique=True, nullable=False)
    leads = db.relationship('Lead', backref='source', lazy=True)

    @staticmethod
    def get_by_id(lead_source_id):
        return LeadSource.query.filter_by(id=lead_source_id).first()

    @staticmethod
    def lead_source_query():
        return LeadSource.query

    def __repr__(self):
        return f"LeadSource('{self.source_name}')"


class Lead(db.Model):
    id = db.Column(db.Integer, db.Sequence('lead_id_seq'), primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(40), nullable=True)
    last_name = db.Column(db.String(40), nullable=False)
    company_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    address_line = db.Column(db.String(40), nullable=True)
    addr_state = db.Column(db.String(40), nullable=True)
    addr_city = db.Column(db.String(40), nullable=True)
    post_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(40), nullable=True)
    notes = db.Column(db.String(200), nullable=True)
    lead_source_id = db.Column(db.Integer, db.ForeignKey('lead_source.id', ondelete='SET NULL'), nullable=True)
    lead_status_id = db.Column(db.Integer, db.ForeignKey('lead_status.id', ondelete='SET NULL'), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @staticmethod
    def get_by_id(lead_id):
        return Lead.query.filter_by(id=lead_id).first()

    def __repr__(self):
        return f"Lead('{self.last_name}', '{self.email}', '{self.company_name}')"

