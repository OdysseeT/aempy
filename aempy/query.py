
from .session import get_session

hostname = "localhost"
port = 4502

QUERY_BUILDER_URL = "/bin/querybuilder.json"

def query_builder(path, properties):
    req = "{}?path={}&{}".format(QUERY_BUILDER_URL, path, properties)
    return query_get(req).json()

def query_get(query):
    full_query = "http://{}:{}{}".format(hostname, port, query)
    print("Request: {}".format(full_query))

    sess = get_session()
    return sess.get(full_query)

def query_post(path, content):
    full_query = "http://{}:{}{}?{}".format(hostname, port, path, content)
    print("Request: {}".format(full_query))

    sess = get_session()
    return sess.post(full_query)

import requests
from requests.auth import HTTPBasicAuth
#from IPython.display import Image

def infer(url):
    session = get_session()
    return session.get("http://127.0.0.1:5000/infer?data="+url)

def deploy(model):
    return
