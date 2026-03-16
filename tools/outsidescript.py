import sys
from cryptography.fernet import Fernet
import requests
from pathlib import Path
from datetime import datetime, timedelta, UTC, timezone
from dateutil.parser import isoparse
from time import sleep

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.models import User, Transaction, Party, ExternalApiToken

from src.logging_config import get_logger

logger = get_logger('outsidescript')

def encrypt_token(token, key):
    logger.debug("Token encrypt started")
    fernet = Fernet(key)
    encrypted_token = fernet.encrypt(token.encode())
    logger.debug("Token encrypted")
    return encrypted_token.decode()

def decrypt_token(encrypted_token, key):
    logger.debug("Token decrypt started")
    fernet = Fernet(key)
    token = fernet.decrypt(encrypted_token)
    logger.debug(f"Token decrypted: {token.decode()}")
    return token.decode()

def generate_token(client_id, client_secret):
    logger.debug("Generate token started")
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    link = f'https://account.bog.ge/auth/realms/bog/protocol/openid-connect/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    resp = requests.post(link, headers=header, data=data)
    status_code = resp.status_code
    resp = resp.json()
    token = resp['access_token']
    logger.info(f"Generate token ended response status code: {status_code}")
    return token

def get_today_activities(token, account_number, currency):
    logger.debug("Today activities started")
    header = {'Authorization': 'Bearer ' + token}
    link = f'https://api.businessonline.ge/api/documents/todayactivities/{account_number}/{currency}'
    resp = requests.get(link, headers=header)
    status_code = resp.status_code
    resp = resp.json()
    logger.info(f"Today activities ended status code: {status_code}")
    return resp

def add_transaction_to_db(app):
    with app.app_context():
        try:
            key = app.config['TOKEN_ENCRYPTION_KEY'].encode()  # Ensure the key is bytes
            client_id = app.config['CLIENT_ID']
            client_secret = app.config['CLIENT_SECRET']

            account_number = app.config['ACCOUNT_NUMBER']
            currency = app.config['CURRENCY']
            logger.debug(f"Got configs, account num: {account_number}")
            token_entry = ExternalApiToken.query.first()
            logger.debug("Token query started")
            if not token_entry:
                logger.debug("Token query not found")
                token = generate_token(client_id, client_secret)
                encrypted_token = encrypt_token(token, key)
                new_token = ExternalApiToken(
                    provider="bog",
                    access_token_encrypted=encrypted_token,
                    expires_at=datetime.now(UTC) + timedelta(minutes=30),  # Set appropriate expiration time
                    updated_at=datetime.now(UTC)
                )
                new_token.create()
                logger.info("New token created")
            else:
                logger.debug(f"Token query found, expires_at: {token_entry.expires_at.replace(tzinfo=timezone.utc)}, now: {datetime.now(UTC)}")
                if token_entry.expires_at.replace(tzinfo=timezone.utc) < datetime.now(UTC):
                    logger.debug("Token is being expired")
                    token = generate_token(client_id, client_secret)
                    encrypted_token = encrypt_token(token, key)
                    token_entry.access_token_encrypted = encrypted_token
                    token_entry.expires_at = datetime.now(UTC) + timedelta(minutes=30)  # Update expiration time
                    token_entry.updated_at = datetime.now(UTC)
                    token_entry.save()
                    logger.info("New token generated and saved")
                else:
                    token = decrypt_token(token_entry.access_token_encrypted, key)
                    logger.info(f"Got valid token from entry")
                    
            
            logger.debug(f"Getting today activities")
            today_activity = get_today_activities(token, account_number, currency)
            logger.debug(f"today_activity len {len(today_activity)}")
            if len(today_activity) > 0:
                for activity in today_activity:
                    logger.debug(f"Started for loop")
                    activity_doc_key = activity['DocKey']
                    existing_transaction = Transaction.query.filter_by(doc_key=activity_doc_key).first()
                    logger.debug(f"Existing transaction query")
                    if existing_transaction:
                        logger.debug(f"Existing transaction found, continuing")
                        continue
                    else:
                        logger.debug(f"Sender query")
                        sender = Party.query.filter_by(account_number=activity['Sender']['AccountNumber']).first()
                        if not sender:
                            logger.debug(f"creating new sender")
                            sender = Party(name=activity['Sender']["Name"], inn=activity['Sender']['Inn'],
                                        account_number=activity['Sender']['AccountNumber'],
                                        bank_code=activity['Sender']['BankCode'],bank_name=activity['Sender']['BankName'])
                            sender.create()
                            logger.debug(f"sender created")
                        logger.debug(f"Beneficiary query")
                        beneficiary = Party.query.filter_by(account_number=activity['Beneficiary']['AccountNumber']).first()
                        if not beneficiary:
                            logger.debug(f"creating new beneficiary")
                            beneficiary = Party(name=activity['Beneficiary']["Name"], inn=activity['Beneficiary']['Inn'],
                                                account_number=activity['Beneficiary']['AccountNumber'],
                                                bank_code=activity['Beneficiary']['BankCode'],bank_name=activity['Beneficiary']['BankName'])
                            beneficiary.create()
                            logger.debug(f"Beneficiary created")
                        logger.debug(f"Creating new transaction")
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
                        logger.info(f"New transaction created")


        except Exception as e:
            
            logger.error(f"Racxa cudad wevida {e}")

if __name__ == "__main__":
    from src import create_app
    from src.config import TestConfig

    logger.info("Running outsidescript standalone")
    standalone_app = create_app(TestConfig)
    add_transaction_to_db(standalone_app)