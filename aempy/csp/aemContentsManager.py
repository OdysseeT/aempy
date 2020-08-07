from notebook.services.contents.manager import ContentsManager
from tornado import web
from tornado.web import HTTPError
import nbformat
from nbformat.v4 import new_notebook

from traitlets import default
import json, ast
from collections import namedtuple

from .notebook import save_nb, get_nb
from .utils.ipycompat import Bool, ContentsManager, from_dict
from .checkpoints import AEMCheckpoints

from .api_utils import (
    base_directory_model,
    base_model,
    #from_b64,
    #outside_root_to_404,
    reads_base64,
    to_api_path,
    #to_b64,
    writes_base64,
)
from .error import (
    CorruptedFile,
    DirectoryExists,
    DirectoryNotEmpty,
    FileExists,
    FileTooLarge,
    NoSuchDirectory,
    NoSuchFile,
    PathOutsideRoot,
    RenameRoot,
)



class AEMContentsManager(ContentsManager):


    def __init__(self, *args, **kwargs):
        super(AEMContentsManager, self).__init__(*args, **kwargs)

    @default('checkpoints_class')
    def _default_checkpoints_class(self):
        return AEMCheckpoints

    def get(self, path, content=True, type='notebook', format=None):

        try:
            return self._get_notebook(path=path, content=content, format=format)
        except CorruptedFile as e:
            self.log.error(
                u'Corrupted file encountered at path %r. %s',
                path, e, exc_info=True,
            )
            raise HTTPError(500, "Unable to read stored content at path %r." % path)

    def _get_notebook(self, path, content, format):
        """
        Get a notebook from AEM.
        """
        try:
            record = get_nb(path).json()
        except NoSuchFile:
            self.no_such_entity(path)

        return self._notebook_model_from_aem(path, record, content)

    def _notebook_model_from_aem(self, path, record, content):
        """
        Build a notebook model from AEM.
        """

        path = to_api_path(path)
        model = base_model(path)

        model['name'] = record['jcr:title']
        model['path'] = path
        model['type'] = 'notebook'
        #model['writable'] = True
        model['created'] = record['jcr:created']
        model['last_modified'] = record['cq:lastModified']

        if content:

            if 'content' in record:
                content = reads_base64(record['content'])
                self.mark_trusted_cells(content, path)
            else:
                content = new_notebook()

            model['format'] = 'json'
            model['content'] = content
            self.validate_notebook_model(model)
        return model

    def save(self, model, path):
        #save_nb(path, model)
        #return self.get(path)

        if 'type' not in model:
            raise web.HTTPError(400, u'No model type provided')
        if 'content' not in model and model['type'] != 'directory':
            raise web.HTTPError(400, u'No file content provided')

        path = path.strip('/')

        # Almost all of this is duplicated with FileContentsManager :(.
        self.log.debug("Saving %s", path)
        if model['type'] not in ('file', 'directory', 'notebook'):
            #self.do_400("Unhandled contents type: %s" % model['type'])
            raise HTTPError(400, "Unhandled contents type: %s" % model['type'])
        try:
            if model['type'] == 'notebook':
                validation_message = self._save_notebook(model, path)
            #elif model['type'] == 'file':
            #    validation_message = self._save_file(db, model, path)
            #else:
            #    validation_message = self._save_directory(db, path)
        except (web.HTTPError, PathOutsideRoot):
            raise
        except FileTooLarge:
            self.file_too_large(path)
        except Exception as e:
            self.log.error(u'Error while saving file: %s %s',
                           path, e, exc_info=True)
            #self.do_500(
            #    u'Unexpected error while saving file: %s %s' % (path, e)
            #)
            raise HTTPError(500, u'Unexpected error while saving file: %s %s' % (path, e))

        # TODO: Consider not round-tripping to the database again here.
        model = self.get(path, type=model['type'], content=False)
        if validation_message is not None:
            model['message'] = validation_message
        return model

    def _save_notebook(self, model, path):
        """
        Save a notebook.
        Returns a validation message.
        """
        nb_contents = from_dict(model['content'])
        self.check_and_sign(nb_contents, path)
        save_nb(path, writes_base64(nb_contents))

        # It's awkward that this writes to the model instead of returning.
        self.validate_notebook_model(model)
        return model.get('message')

    def delete_file(self, path):
        super().delete_file(path)

    def rename_file(self, old_path, path):
        super().rename_file(old_path, path)

    def file_exists(self, path):
        file = get_nb(path)
        return file is not None

    def dir_exists(self, path):
        return False # TODO not necessary

    def is_hidden(self, path):
        return False # TODO not necessary

    def exists(self, path):
        file = get_nb(path)
        return file is not None

    def _get_directory(self, path, content, format):
        return None # TODO not necessary
