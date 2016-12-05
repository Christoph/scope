
from . import ImapHandler
from scope.models import AgentImap


class Provider(object):
    """docstring for crawler."""

    def __init__(self):
        self.imap = ImapHandler()

    def query_source(self, source):
        if type(source) == AgentImap:
            return self.imap.get_data(source)

        raise ValueError("No valid source type")
