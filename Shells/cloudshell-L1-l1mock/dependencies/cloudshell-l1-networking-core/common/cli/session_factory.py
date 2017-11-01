__author__ = 'g8y3e'

import importlib
from common.configuration_parser import ConfigurationParser


class SessionFactory:
    @staticmethod
    def create(session_type, **kwargs):
        session_data = ConfigurationParser.get('cli_variable', session_type)
        module_name = session_data[0]
        class_name = session_data[1]

        module = importlib.import_module(module_name)
        if hasattr(module, class_name):
            return getattr(module, class_name)(**kwargs)

        return None

