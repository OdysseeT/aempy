from __future__ import unicode_literals

from .api_utils import (
    _decode_unknown_from_base64,
    outside_root_to_404,
    reads_base64,
    to_b64,
    writes_base64,
)

from .utils.ipycompat import Checkpoints, GenericCheckpointsMixin


class AEMCheckpoints(GenericCheckpointsMixin,
                          Checkpoints):
    """
    A Checkpoints implementation that saves checkpoints to a remote AEM.
    """

    @outside_root_to_404
    def create_notebook_checkpoint(self, nb, path):
        """Create a checkpoint of the current state of a notebook
        Returns a checkpoint_id for the new checkpoint.
        """
        b64_content = writes_base64(nb)
        #TODO

    @outside_root_to_404
    def create_file_checkpoint(self, content, format, path):
        """Create a checkpoint of the current state of a file
        Returns a checkpoint_id for the new checkpoint.
        """
        try:
            b64_content = to_b64(content, format)
        except ValueError as e:
            self.do_400(str(e))
        #TODO
        return 123 # Fake Checkpoint ID

    @outside_root_to_404
    def delete_checkpoint(self, checkpoint_id, path):
        """delete a checkpoint for a file"""
        #TODO

    def get_checkpoint_content(self, checkpoint_id, path):
        """Get the content of a checkpoint."""
        #TODO

    @outside_root_to_404
    def get_notebook_checkpoint(self, checkpoint_id, path):
        b64_content = self.get_checkpoint_content(checkpoint_id, path)
        return {
            'type': 'notebook',
            'content': reads_base64(b64_content),
        }

    @outside_root_to_404
    def get_file_checkpoint(self, checkpoint_id, path):
        b64_content = self.get_checkpoint_content(checkpoint_id, path)
        content, format = _decode_unknown_from_base64(path, b64_content)
        return {
            'type': 'file',
            'content': content,
            'format': format,
        }

    @outside_root_to_404
    def list_checkpoints(self, path):
        """Return a list of checkpoints for a given file"""
        #TODO
        return []

    @outside_root_to_404
    def rename_all_checkpoints(self, old_path, new_path):
        """Rename all checkpoints for old_path to new_path."""
        #TODO

    @outside_root_to_404
    def delete_all_checkpoints(self, path):
        """Delete all checkpoints for the given path."""
        #TODO
