from .query import query_get, query_builder, query_post
import pandas as pd
from PIL import Image
from io import BytesIO
import requests, datetime, time
import urllib.request

DEFAULT_HOST="localhost"
DEFAULT_PORT=4502
DEFAULT_USER="admin"
DEFAULT_PASSWORD="admin"

class AEM():
    system_info = {
        "productinfo":"/system/console/status-productinfo.json",
    }

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

    def info(self):
        response = self._query_get(AEM.system_info['productinfo'])
        return AEM.ProductInfo(response)

    def _query_get(self, request, format="json"):
        response = query_get(request)
        if format is "json":
            return response.json()
        else:
            return response

    class ProductInfo():
        def __init__(self, obj):
            self.customer = obj[1].strip()
            self.downloadID = obj[2].strip()
            self.product = obj[3].strip()

            self.version = obj[6].strip()


class Assets(AEM):

    def __init__(self, **kwds):
        super().__init__(**kwds)


    def get_asset(self, path):
        response = query_get("{}.infinity.json".format(path))
        return response.json()

    def get_assets(self, path, limit=5):
        path = "{}".format(path)
        properties = "1_property=jcr:primaryType&1_property.value=dam:Asset&1_property.operation=like&orderby=path&p.limit="+str(limit)

        data = query_builder(path, properties)
        return [img['path'] for img in data['hits']]

    def display(self, img, dampath="/content/dam/"):
        img_content = img['jcr:content']
        if 'dam:relativePath' in img_content:
            path = "{}{}".format(dampath, img_content['dam:relativePath'])
        elif 'cq:name' in img_content:
            path = "{}/{}".format(img_content['cq:parentPath'], img_content['cq:name'])

        response = query_get(path)
        return Image.open(BytesIO(response.content))

class QueryBuilder(AEM):

    def __init__(self, path, **kwds):
        super().__init__(**kwds)
        self.query = "/bin/querybuilder.json?path={}".format(path)
        self.prop_idx = 0

    def like(self, name, value):
        return self.add_prop(name, value, operation="like")

    def add_prop(self, name, value, operation):
        # 1_property=jcr:primaryType&1_property.value=dam:Asset
        prop = "&{0}_property={1}&{0}_property.value={2}&{0}_property.operation={3}".format(self.prop_idx, name, value, operation)
        self.query += prop
        self.prop_idx +=1
        return prop

    def limit(self, limit=5):
        self.query += "&p.limit="+str(limit)

    def orderby(self, order="path"):
        self.query += "&orderby="+order

    def exec(self):

        if "p.limit" not in self.query:
            self.limit()
        if "orderby" not in self.query:
            self.orderby()

        return self._query_get(self.query)


class System(AEM):
    log_file = {
        "error":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/error.log",
        "request":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/request.log",
        "history":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/history.log",
        "auditlog":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/auditlog.log",
        "access":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/access.log",
        "upgrade":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/upgrade.log",
    }

    def __init__(self, **kwds):
        super().__init__(**kwds)

    def _get_log(self, name, qty):
        logfile = System.log_file[name]
        logfile = logfile.format(qty)
        response = query_get(logfile)
        return response.text.split("\n")

    def log_error(self, qty=10000):
        return self._get_log('error', qty)

    def log_request(self, qty=10000):
        return self._get_log('request', qty)

    def log_history(self, qty=10000):
        return self._get_log('history', qty)

    def log_audilog(self, qty=10000):
        return self._get_log('audilog', qty)

    def log_access(self, qty=10000):
        return self._get_log('access', qty)

    def log_upgrade(self, qty=10000):
        return self._get_log('upgrade', qty)

    def log_to_pandas(self, log):
        column_names = ["date", "level", "class", "message"]
        df = pd.DataFrame(columns = column_names)

        for i in range(len(log)):
            words = log[i].split(" ")
            if len(words)<4: continue
            ldate = datetime.datetime.strptime((words[0]+" "+words[1]).strip(), '%d.%m.%Y %H:%M:%S.%f')
            llevel = words[2].strip().replace("*","")
            if llevel is "ERROR":
                # TODO Need to parse the class correctly
                lclass = words[3].strip().replace("[","").replace("]","")
            else:
                lclass = words[3].strip().replace("[","").replace("]","")
            lmessage = words[4:]
            df.loc[i] = [ldate, llevel, lclass, lmessage]
        return df
