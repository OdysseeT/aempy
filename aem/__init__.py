import requests
from requests.auth import HTTPBasicAuth
#from IPython.display import Image
from PIL import Image
import urllib.request
from io import BytesIO

aem_server = "http://localhost:4502"
dam = "/content/dam"
session = None
def init():
    global session
    #session = requests.session(auth=HTTPBasicAuth('admin', 'admin'))
    session = requests.Session()
    session.auth = ('admin', 'admin')

def get_session():
    global session
    if not session:
        init()
    return session
    
def get_image(path):
    url = aem_server+dam+path
    response = session.get(url)
    return Image.open(BytesIO(response.content))
#    return Image.open(urllib.request.urlopen(url, auth=HTTPBasicAuth('admin', 'admin')))

def get_images(path, limit=5):
    
    query = aem_server+"/bin/querybuilder.json?path="+dam+path+"&1_property=jcr:primaryType&1_property.value=dam:Asset&1_property.operation=like&orderby=path&p.limit="+str(limit)

    req = aem_server+"/bin/querybuilder.json?path="+dam+path+"&1_property=jcr:primaryType&1_property.value=dam:Asset&1_property.operation=like&orderby=path&p.limit="+str(limit)
    r = requests.get(url = req, auth=HTTPBasicAuth('admin', 'admin'))

    data = r.json()
    img_list = []
    for img in data['hits']:
        img_list.append(img['path'])
    return img_list

def infer(url):
    session = get_session()
    return session.get("http://127.0.0.1:5000/infer?data="+url)

def deploy(model):
    return