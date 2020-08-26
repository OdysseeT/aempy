from aempy.query import query_get, query_post
from urllib.parse import quote
from .api_utils import writes_base64

CSP_PATH = "/content/csprojects"

def get_nb(path):
    nb_query = "{}/{}/jcr:content.json".format(CSP_PATH, path.strip("/"))
    print("Requesting Notebook: ", nb_query)
    return query_get(nb_query)

#def save_nb(path, content):
#    nb_query = "{}/{}/jcr:content".format(CSP_PATH, path.strip("/"))
#    print("Save Notebook: ", nb_query)
#    return query_post(nb_query, "content={}".format(content))

def save_nb(path, content):
    nb_query = "{}/{}/jcr:content".format(CSP_PATH, path.strip("/"))
    print("Save Notebook: ", nb_query)

    # Encode Content
    content = writes_base64(content)
    content = quote(content, safe='') # Need extra encoding for character like sharp
    content = ":operation=import&:contentType=json&:content={}".format(content)

    return query_post(nb_query, content)
