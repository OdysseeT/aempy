from notebook.services.contents.manager import ContentsManager
from .notebook import save_nb, get_nb
from .api_utils import (
    base_directory_model,
    base_model,
    from_b64,
    outside_root_to_404,
    reads_base64,
    to_api_path,
    to_b64,
    writes_base64,
)
import json, ast
from collections import namedtuple
import nbformat
from nbformat.v4 import new_notebook

class AEMContentsManager(ContentsManager):


    def __init__(self, *args, **kwargs):
        super(AEMContentsManager, self).__init__(*args, **kwargs)

    def put(self, path):
        print("NO PUT")

    def get(self, path, content=True, type=None, format=None):
        #print("##### ODY Getting path: {} {} {} {}".format(path, content, type, format))
        record = get_nb(path)
        #print("## record: ",record )
        #record = eval(record.text)
        #print("## record: ",record )
        return self._notebook_model_from_aem(path, record.json(), content)

    def _get_directory(self, path, content, format):
        return super.get(path, content, format)

    def _notebook_model_from_aem(self, path, record, content):
        """
        Build a notebook model from AEM.
        """
        #print("ORIGINAL_RECORD: ",type(record), record)

        path = to_api_path(path)
        model = base_model(path)

        model['name'] = record['jcr:title']
        model['path'] = path
        model['type'] = 'notebook'
        model['writable'] = True
        model['created'] = record['jcr:created']
        model['last_modified'] = record['cq:lastModified']

        if content:
            model['format'] = 'json'

            if 'notebook' in record:
                notebook = record['notebook']#[0]

                notebook = ast.literal_eval(notebook) # String to dict
                content = notebook['content']

                content = reads_base64(json.dumps(content))
                self.mark_trusted_cells(content, path)
                print("CHECKING: ",content)
            else:
                content = new_notebook()
                print("CONTENT: ",content)

            model['content'] = content
            self.validate_notebook_model(model)
        return model

    def save(self, model, path):
        save_nb(path, model)

    def delete_file(self, path):
        super().delete_file(path)

    def rename_file(self, old_path, path):
        super().rename_file(old_path, path)

    def file_exists(self, path):
        print("##### ODY File path",path)
        return "404" not in get_nb(path).text

    def dir_exists(self, path):
        print("##### ODY Dir path",path)
        return True

    def is_hidden(self, path):
        return False

    def exists(self, path):
        print("##### ODY Exists path",path)
        return "404" not in get_nb(path).text

    def guess_type(self, path, allow_directory=True):
        """
        Guess the type of a file.
        If allow_directory is False, don't consider the possibility that the
        file is a directory.
        """
        if path.endswith('.ipynb'):
            return 'notebook'
        elif allow_directory and self.dir_exists(path):
            return 'directory'
        else:
            return 'file'
