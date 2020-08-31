#from aempy.query import query_get, query_post
from urllib.parse import quote
from .api_utils import writes_base64
import requests
import urllib.request

CSP_PATH = "/content/csprojects"


class AEMNotebookManager():

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.session = requests.Session()
        self.session.auth = (user, password)


    def get_nb(self, path):
        nb_query = "{}/{}/jcr:content.infinity.json".format(CSP_PATH, path.strip("/"))
        print("Requesting Notebook: ", nb_query)
        return self.__query_get(nb_query)

    #def save_nb(path, content):
    #    nb_query = "{}/{}/jcr:content".format(CSP_PATH, path.strip("/"))
    #    print("Save Notebook: ", nb_query)
    #    return query_post(nb_query, "content={}".format(content))

    def delete_cells(self, path, content):
        nb_query = "{}/{}/jcr:content/cells".format(CSP_PATH, path.strip("/"))
        print("Delete Cells: ", nb_query)

        content = ":operation=delete".format(content)
        return self.__query_post(nb_query, content)

    def save_nb(self, path, content):
        nb_query = "{}/{}/jcr:content".format(CSP_PATH, path.strip("/"))
        print("Save Notebook: ", nb_query)

        # Encode Content
        content = writes_base64(content)
        #print("BASE64: ", content)
        content = quote(content, safe='') # Need extra encoding for character like sharp
        #print("SAFE: ", content)
        content = ":operation=import&:contentType=json&:content={}".format(content)

        return self.__query_post(nb_query, content)


    def __query_get(self, query):
        full_query = "http://{}:{}{}".format(self.host, self.port, query)
        print("Request: {}".format(full_query))

        #sess = get_session()
        return self.session.get(full_query)

    def __query_post(self, path, content):
        full_query = "http://{}:{}{}".format(self.host, self.port, path)
        print("Request: {}".format(full_query))
        print("\tData: {}".format(content))

        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        return self.session.post(full_query, data=content)
