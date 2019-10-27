from datetime import datetime
from eeazycrm import db


class DealStage(db.Model):
    id = db.Column(db.Integer, db.Sequence('deal_stage_id_seq'), primary_key=True)
    stage_name = db.Column(db.String(20), nullable=False)
    display_order = db.Column(db.Integer, nullable=False)
    deals = db.relationship(
        'Deal',
        uselist=False,
        backref='dealstage',
        lazy=True
    )


class Deal(db.Model):
    id = db.Column(db.Integer, db.Sequence('deal_id_seq'), primary_key=True)
    expected_close_price = db.Column(db.Float)
    expected_close_date = db.Column(db.DateTime)
    deal_stage_id = db.Column(db.Integer, db.ForeignKey('deal_stage.id', ondelete='SET NULL'), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='SET NULL'), nullable=True)
    is_won = db.Column(db.Boolean, default=False)
    deal_closed_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
