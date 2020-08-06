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
import nbformat

class AEMContentsManager(ContentsManager):


    def __init__(self, *args, **kwargs):
        super(AEMContentsManager, self).__init__(*args, **kwargs)

    def get(self, path, content=True, type=None, format=None):
        print("##### ODY Getting path: {} {} {} {}".format(path, content, type, format))
        record = get_nb(path)
        print("## record: ",record )
        return self._notebook_model_from_aem(path, record, content)

    def _get_directory(self, path, content, format):
        return super.get(path, content, format)

    def _notebook_model_from_aem(self, path, record, content):
        """
        Build a notebook model from AEM.
        """
        path = to_api_path(path)
        model = base_model(path)

        model['name'] = record['jcr:title']
        model['path'] = path
        model['type'] = 'notebook'
        model['writable'] = True
        model['created'] = record['jcr:created']
        model['last_modified'] = record['cq:lastModified']
        model['mimetype'] = 'json'
        model['format'] = 'json'

        if content:
            nb = nbformat.from_dict(record['notebook'])
            #print("MY NOTEBOOK: ",nb)
            nb = reads_base64(nb)
            self.mark_trusted_cells(nb, path)
            model['content'] = nb
            model['format'] = 'json'
            self.validate_notebook_model(model)
        return model

    def save(self, model, path):
        #print(model)
        #print(path)
        save_nb(path, model)
        #super().save(model, path)

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
