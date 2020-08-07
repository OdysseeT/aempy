from .query import query_get, query_builder, query_post
from PIL import Image
from io import BytesIO
import requests
import urllib.request

DEFAULT_HOST="localhost"
DEFAULT_PORT=4502
DEFAULT_USER="admin"
DEFAULT_PASSWORD="admin"

class AEM():

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, user=DEFAULT_USER, password=DEFAULT_PASSWORD):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.session = requests.Session()
        self.session.auth = (user, password)

    def __init_session():
        self.session = requests.Session()
        self.session.auth = (user, password)

    def get_session(self):
        if not self.session:
            __init_session()
        return self.session

class Assets(AEM):

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, user=DEFAULT_USER, password=DEFAULT_PASSWORD):
        super().__init__(host, port, user, password)


    def get_asset(self, path):
        response = query_get("{}.infinity.json".format(path))
        return response.json()

    def get_assets(self, path, limit=5):
        path = "{}".format(path)
        properties = "1_property=jcr:primaryType&1_property.value=dam:Asset&1_property.operation=like&orderby=path&p.limit="+str(limit)

        data = query_builder(path, properties)
        img_list = [img['path'] for img in data['hits']]
        #for img in data['hits']:
        #    img_list.append(img['path'])
        return img_list

    def display(self, img, dampath="/content/dam/"):
        path = "{}{}".format(dampath, img['jcr:content']['dam:relativePath'])
        response = query_get(path)
        return Image.open(BytesIO(response.content))


class System(AEM):
    log_file = {
        "error":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/error.log",
    }

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, user=DEFAULT_USER, password=DEFAULT_PASSWORD):
        super().__init__(host, port, user, password)

    def _get_log(self, name, qty):
        logfile = System.log_file[name]
        logfile = logfile.format(qty)
        response = query_get(logfile)
        return response.text.split("\n")

    def get_errorlog(self, qty=10000):
        return self._get_log('error', qty)
