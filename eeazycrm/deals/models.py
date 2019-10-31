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

    @staticmethod
    def deal_stage_list_query():
        return DealStage.query

    @staticmethod
    def get_label(deal_stage):
        return deal_stage.stage_name

    def __repr__(self):
        return f"DealStage('{self.stage_name}')"


class Deal(db.Model):
    id = db.Column(db.Integer, db.Sequence('deal_id_seq'), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    expected_close_price = db.Column(db.Float, nullable=False)
    expected_close_date = db.Column(db.DateTime)
    deal_stage_id = db.Column(db.Integer, db.ForeignKey('deal_stage.id', ondelete='SET NULL'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='cascade'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='SET NULL'), nullable=True)
    deal_closed_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    notes = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Deal('{self.account_id}')"
