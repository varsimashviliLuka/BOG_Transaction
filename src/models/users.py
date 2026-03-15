import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions import db
from src.models.base import BaseModel

class User(db.Model, BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(db.String(255), unique=True, default=lambda: str(uuid.uuid4()))

    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column(db.String(255), nullable=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def generateJson(self):
        result = {'email': self.email,
                  'id': self.id,
                  'uuid': self.uuid}
        return result


    def __repr__(self):
        return f'{self.generateJson()}'