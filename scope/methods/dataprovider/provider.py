
from .imap_handler import ImapHandler
from scope.models import AgentImap


class Provider(object):
    """docstring for crawler."""

    def __init__(self):
        self.imap = ImapHandler()

    def query_source(self, agent):
        if type(agent) == AgentImap:
            return self.imap.get_data(agent)

        raise ValueError("No valid agent type")
