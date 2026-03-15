import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src import create_app
from src.models import User, Transaction, Party

import requests

client_id = 'd'
client_secret = '7'

def update_temporary_db():
    app = create_app()
    # app = create_app(TestConfig)
    with app.app_context():
        try:
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            link = f'https://account.bog.ge/auth/realms/bog/protocol/openid-connect/token'
            data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
            resp = requests.post(link, headers=header, data=data).json()
            token = resp['access_token']
            print(token)
            header = {'Authorization': 'Bearer ' + token}
            link = 'https://api.businessonline.ge/api/documents/todayactivities/GE63BG0000000593949785/GEL'
            resp = requests.get(link, headers=header)
            print(resp.status_code)
            resp = resp.json()
            print(resp)
        except Exception as e:
            # logging.critical(f"სკრიპტის შესრულების დროს შეცდომა: {e}")
            print("Ar mushaobs")

if __name__ == "__main__":
    update_temporary_db()