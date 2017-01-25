'''
Helper function for learning data aquisition.
'''

from scope.methods.dataprovider import er_handler
from scope.models import AgentEventRegistry


def get_er_data(keywords, timespan, number):
    agent = AgentEventRegistry(
        user="christoph.kralj@gmail.com",
        pwd="XzbiyLnpeh8MBtC{$4hv",
        lang="eng",
        concepts=keywords,
        locations="")

    er = er_handler.EventRegistryHandler(agent)

    data = er.get_data(timespan, number)

    return data
