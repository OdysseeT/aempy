import requests
import urllib.request


user="admin"
password = "admin"

session = None
def init():
    global session
    #session = requests.session(auth=HTTPBasicAuth('admin', 'admin'))
    session = requests.Session()
    session.auth = (user, password)

def get_session():
    global session
    if not session:
        init()
    return session
