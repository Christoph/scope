from scope.models import AgentImap

from . import imap_handler


class Provider(object):
    """docstring for crawler."""

    def __init__(self):
        self.imap = imap_handler.ImapHandler()

    def query_agents(self, agent):
        if type(agent) == AgentImap:
            return self.imap.get_data(agent)

        raise ValueError("No valid agent type")
