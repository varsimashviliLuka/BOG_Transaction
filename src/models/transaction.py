from src.extensions import db
from src.models.base import BaseModel

class Transaction(db.Model, BaseModel):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(70), unique=True, nullable=False)
    doc_key = db.Column(db.String(70), unique=True, nullable=False)
    doc_no = db.Column(db.String(70), nullable=False)
    post_date = db.Column(db.DateTime)
    value_date = db.Column(db.DateTime)
    entry_type = db.Column(db.String(5))
    entry_comment = db.Column(db.String(350))
    entry_comment_en = db.Column(db.String(350))
    nomination = db.Column(db.String(100))
    credit = db.Column(db.Float)
    debit = db.Column(db.Float)
    amount = db.Column(db.Float)
    amount_base = db.Column(db.Float)
    payer_name = db.Column(db.String(50))
    payer_inn = db.Column(db.String(20))

    sender_id = db.Column(db.Integer, db.ForeignKey("parties.id"))
    beneficiary_id = db.Column(db.Integer, db.ForeignKey("parties.id"))

    sender = db.relationship("Party", foreign_keys=[sender_id])
    beneficiary = db.relationship("Party", foreign_keys=[beneficiary_id])

    def generateJson(self):
        return {
            "id": self.id,
            "doc_key": self.doc_key,
            "doc_no": self.doc_no,
            "post_date": self.post_date,
            "value_date": self.value_date,
            "entry_type": self.entry_type,
            "entry_comment": self.entry_comment,
            "entry_comment_en": self.entry_comment_en,
            "nomination": self.nomination,
            "credit": self.credit,
            "debit": self.debit,
            "amount": self.amount,
            "amount_base": self.amount_base,
            "payer_name": self.payer_name,
            "payer_inn": self.payer_inn,
            "sender": self.sender.generateJson() if self.sender else None,
            "beneficiary": self.beneficiary.generateJson() if self.beneficiary else None
        }

    def __repr__(self):
        return f"{self.generateJson()}"


class Party(db.Model, BaseModel):
    __tablename__ = "parties"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255))
    inn = db.Column(db.String(50))
    account_number = db.Column(db.String(50))
    bank_code = db.Column(db.String(50))
    bank_name = db.Column(db.String(255))

    def generateJson(self):
        return {
            "name": self.name,
            "inn": self.inn,
            "account_number": self.account_number,
            "bank_code": self.bank_code,
            "bank_name": self.bank_name
        }

    def __repr__(self):
        return f"{self.generateJson()}"