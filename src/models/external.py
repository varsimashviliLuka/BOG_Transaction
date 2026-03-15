from src.extensions import db
from src.models.base import BaseModel

class ExternalApiToken(db.Model, BaseModel):
    __tablename__ = "usexternal_api_tokensers"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), unique=True, nullable=False, index=True)
    access_token_encrypted = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<ExternalApiToken {self.updated_at}>"