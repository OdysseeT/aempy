from .query import query_get, query_post
from PIL import Image
from io import BytesIO

DAM_PATH = "/content/dam"

def get_image(path):
    response = query_get(path)
    return Image.open(BytesIO(response.content))

def get_images(path, limit=5):
    path = "{}{}".format(DAM_PATH,path)
    properties = "1_property=jcr:primaryType&1_property.value=dam:Asset&1_property.operation=like&orderby=path&p.limit="+str(limit)

    data = query_builder(path, properties)
    img_list = []
    for img in data['hits']:
        img_list.append(img['path'])
    return img_list
