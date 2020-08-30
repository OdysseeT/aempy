from .query import query_builder #, query_post, query_get
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

    def _query_get(self, request, format=None):
        response = self.__query_get(request)
        if format is "json":
            return response.json()
        else:
            return response

    def __query_get(self, query):
        formatted_url = self.__format_url(self.host)
        full_query = "{}:{}{}".format(formatted_url, self.port, query)
        print("Request: {}".format(full_query))
        return self.session.get(full_query)

    def __format_url(self, host):
        url = ""
        if host.startswith("https") or host.startswith("http"):
            url = host
        else:
            url = "http://{}".format(host)
        return url

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
        response = self._query_get("{}.infinity.json".format(path))
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

        response = self._query_get(path)
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

    log_url = "/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/{}"

    #log_file = {
    #    "error":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/error.log",
    #    "request":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/request.log",
    #    "history":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/history.log",
    #    "auditlog":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/auditlog.log",
    #    "access":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/access.log",
    #    "upgrade":"/system/console/slinglog/tailer.txt?tail={}&grep=*&name=/logs/upgrade.log",
    #}

    def __init__(self, **kwds):
        super().__init__(**kwds)

    def get_log(self, name, qty=10000):
        #logfile = System.log_file[name]
        logfile = System.log_url.format(qty, name)
        response = self._query_get(logfile)
        return response.text.split("\n")

    def log_error(self, qty=10000, to_df=True):
        return self.get_log('error.log', qty)

    def log_request(self, qty=10000):
        return self.get_log('request.log', qty)

    def log_history(self, qty=10000):
        return self.get_log('history.log', qty)

    def log_audilog(self, qty=10000):
        return self.get_log('audilog.log', qty)

    def log_access(self, qty=10000):
        return self.get_log('access.log', qty)

    def log_upgrade(self, qty=10000):
        return self.get_log('upgrade.log', qty)

    def error_logfile_to_df(self, log):
        logile = open(log, "r")
        logs = logile.readlines()
        return self.error_log_to_df(logs)

    def error_log_to_df(self, log):
        column_names = ["date", "level", "class", "message"]
        df = pd.DataFrame(columns = column_names)

        for i in range(len(log)):
            words = log[i].split(" ")
            if len(words)<4: continue
            try:
                ldate = datetime.datetime.strptime((words[0]+" "+words[1]).strip(), '%d.%m.%Y %H:%M:%S.%f')
                llevel = words[2].strip().replace("*","")
                if llevel is "ERROR":
                    # TODO Need to parse the class correctly
                    lclass = words[3].strip().replace("[","").replace("]","")
                else:
                    lclass = words[3].strip().replace("[","").replace("]","")
                lmessage = words[4:]
                df.loc[i] = [ldate, llevel, lclass, lmessage]
            except:
                pass
        return df

    def plot(self, df, freq="1min"):
        try:
            t = (df.assign(counter = 1)
             .set_index('date')
             .groupby([pd.Grouper(freq=freq), 'level']).sum()
             .squeeze()
             .unstack())

            t.plot(figsize=(15,4))
        except AttributeError:
            print("Error: Frequency is too large.")
