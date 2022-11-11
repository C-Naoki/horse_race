import dataclasses
import os
import requests
from dotenv import load_dotenv

load_dotenv()


@dataclasses.dataclass(frozen=True)
class Netkeiba:
    USER = os.environ['private_gmail']
    PASS = os.environ['netkeiba_pass']

    LOGIN_URL = "https://regist.netkeiba.com/account/?pid=login&action=auth"
    PAYLOAD = {
        'login_id': USER,
        'pswd': PASS
    }

    SESSION = requests.Session()
    SESSION.post(LOGIN_URL, data=PAYLOAD)
