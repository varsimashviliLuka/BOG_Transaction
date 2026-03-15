import sys
from cryptography.fernet import Fernet
import requests
from pathlib import Path
from datetime import datetime, timedelta, UTC
from dateutil.parser import isoparse

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src import create_app
from src.models import User, Transaction, Party, ExternalApiToken


def encrypt_token(token, key):
    fernet = Fernet(key)
    encrypted_token = fernet.encrypt(token.encode())
    return encrypted_token.decode()

def decrypt_token(encrypted_token, key):
    fernet = Fernet(key)
    token = fernet.decrypt(encrypted_token)
    return token.decode()

def generate_token(client_id, client_secret):
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    link = f'https://account.bog.ge/auth/realms/bog/protocol/openid-connect/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    resp = requests.post(link, headers=header, data=data).json()
    token = resp['access_token']
    return token

def get_today_activities(token, account_number, currency):
    header = {'Authorization': 'Bearer ' + token}
    link = f'https://api.businessonline.ge/api/documents/todayactivities/{account_number}/{currency}'
    resp = requests.get(link, headers=header)
    resp = resp.json()
    return resp

def add_transaction_to_db():
    app = create_app()
    # app = create_app(TestConfig)
    with app.app_context():
        try:
            key = app.config['TOKEN_ENCRYPTION_KEY'].encode()  # Ensure the key is bytes
            client_id = app.config['CLIENT_ID']
            client_secret = app.config['CLIENT_SECRET']

            account_number = app.config['ACCOUNT_NUMBER']
            currency = app.config['CURRENCY']

            token_entry = ExternalApiToken.query.first()
            if not token_entry:
                token = generate_token(client_id, client_secret)
                encrypted_token = encrypt_token(token, key)
                new_token = ExternalApiToken(
                    provider="bog",
                    access_token_encrypted=encrypted_token,
                    expires_at=datetime.now(UTC) + timedelta(minutes=30),  # Set appropriate expiration time
                    updated_at=datetime.now(UTC)
                )
                new_token.create()
            else:
                if token_entry.expires_at < datetime.now(UTC):
                    token = generate_token(client_id, client_secret)
                    encrypted_token = encrypt_token(token, key)
                    token_entry.access_token_encrypted = encrypted_token
                    token_entry.expires_at = datetime.now(UTC) + timedelta(minutes=30)  # Update expiration time
                    token_entry.updated_at = datetime.now(UTC)
                    token_entry.save()
                else:
                    token = decrypt_token(token_entry.access_token_encrypted, key)
                    
            

            today_activity = get_today_activities(token, account_number, currency)
            if len(today_activity) > 0:
                for activity in today_activity:
                    activity_doc_key = activity['DocKey']
                    existing_transaction = Transaction.query.filter_by(doc_key=activity_doc_key).first()
                    if existing_transaction:
                        continue
                    else:
                        sender = Party.query.filter_by(account_number=activity['Sender']['AccountNumber']).first()
                        if not sender:
                            sender = Party(name=activity['Sender']["Name"], inn=activity['Sender']['Inn'],
                                        account_number=activity['Sender']['AccountNumber'],
                                        bank_code=activity['Sender']['BankCode'],bank_name=activity['Sender']['BankName'])
                            sender.create()
                        beneficiary = Party.query.filter_by(account_number=activity['Beneficiary']['AccountNumber']).first()
                        if not beneficiary:
                            beneficiary = Party(name=activity['Beneficiary']["Name"], inn=activity['Beneficiary']['Inn'],
                                                account_number=activity['Beneficiary']['AccountNumber'],
                                                bank_code=activity['Beneficiary']['BankCode'],bank_name=activity['Beneficiary']['BankName'])
                            beneficiary.create()

                        transaction = Transaction(
                            transaction_id=activity['Id'],
                            doc_key=activity_doc_key,
                            doc_no=activity['DocNo'],
                            post_date=isoparse(activity['PostDate']),
                            value_date=isoparse(activity['ValueDate']),
                            entry_type=activity['EntryType'],
                            entry_comment=activity.get('EntryComment', ''),
                            entry_comment_en=activity.get('EntryCommentEn', ''),
                            nomination=activity.get('Nomination', ''),
                            credit=float(activity.get('Credit', 0)),
                            debit=float(activity.get('Debit', 0)),
                            amount=float(activity.get('Amount', 0)),
                            amount_base=float(activity.get('AmountBase', 0)),
                            payer_name=activity.get('PayerName', ''),
                            payer_inn=activity.get('PayerInn', ''),
                            sender_id=sender.id,
                            beneficiary_id=beneficiary.id
                        )
                        transaction.create()


        except Exception as e:
            # logging.critical(f"სკრიპტის შესრულების დროს შეცდომა: {e}")
            print("Ar mushaobs")

if __name__ == "__main__":
    add_transaction_to_db()