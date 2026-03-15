
import requests

client_id="x"
client_secret='x'

from time import sleep
from datetime import datetime

def get_token():
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
    with open("test.txt",'w') as f:
        f.write(token)

def et_activity():
    with open("test.txt", 'r') as f:
        token = f.read()
    try:
        header = {'Authorization': 'Bearer ' + token}
        link = 'https://api.businessonline.ge/api/documents/todayactivities/GE63BG0000000593949785/GEL'
        resp = requests.get(link, headers=header)
        print(resp.status_code)
        resp = resp.json()
        print(resp)
        with open("log.txt",'a') as f:
            f.write(f"{datetime.now()} gaishva tokenit {resp} token: {token}\n")
    except:
        with open("log.txt",'a') as f:
            f.write(f"{datetime.now()} axali tokeni dagenerirda\n")
        get_token()
        et_activity()

while True:
    et_activity()
    sleep(60)