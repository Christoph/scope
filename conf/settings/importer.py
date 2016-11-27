"""Base import class."""
from django.core.exceptions import ImproperlyConfigured
import os


class ImportGlobal(object):
    """docstring for variable import."""

    def get_env_variable(self, var_name):
        """Get Variable."""
        try:
            return os.environ[var_name]
        except KeyError:
            error_msg = "Set the %s environment variable" % var_name
            raise ImproperlyConfigured(error_msg)
