from datetime import datetime
from eeazycrm import db


class DealStage(db.Model):
    id = db.Column(db.Integer, db.Sequence('deal_stage_id_seq'), primary_key=True)
    stage_name = db.Column(db.String(20), nullable=False)
    display_order = db.Column(db.Integer, nullable=False)
    deals = db.relationship(
        'Deal',
        backref='dealstage',
        lazy=True
    )

    @staticmethod
    def deal_stage_list_query():
        return DealStage.query

    @staticmethod
    def get_label(deal_stage):
        return deal_stage.stage_name

    @staticmethod
    def get_deal_stage(deal_stage_id):
        return DealStage.query.filter_by(id=deal_stage_id).first()

    def __repr__(self):
        return f"DealStage('{self.stage_name}')"


class Deal(db.Model):
    id = db.Column(db.Integer, db.Sequence('deal_id_seq'), primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    expected_close_price = db.Column(db.Float, nullable=False)
    expected_close_date = db.Column(db.DateTime, nullable=True)
    deal_stage_id = db.Column(db.Integer, db.ForeignKey('deal_stage.id', ondelete='SET NULL'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='cascade'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='SET NULL'), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    notes = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deal_stage = db.relationship(
        'DealStage',
        backref='deal',
        uselist=False,
        lazy=True
    )
    owner = db.relationship(
        'User',
        backref='deal',
        uselist=False,
        lazy=True
    )

    def is_expired(self):
        today = datetime.today()
        if self.expected_close_date < today:
            return True
        return False

    def __repr__(self):
        return f"Deal('{self.title}', '{self.deal_stage_id}', '{self.account_id}', '{self.contact_id}', '{self.owner_id}')"
