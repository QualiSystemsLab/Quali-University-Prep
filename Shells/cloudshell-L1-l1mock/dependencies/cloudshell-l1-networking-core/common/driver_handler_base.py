#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractmethod

from configuration_parser import ConfigurationParser
from cli.session_factory import SessionFactory


class DriverHandlerBase:
    def __init__(self):
        connection_type = ConfigurationParser.get("common_variable", "connection_type")
        connection_timeout = ConfigurationParser.get("common_variable", "server_timeout")

        self._session = SessionFactory.create(connection_type, timeout=connection_timeout)
        self._prompt = ConfigurationParser.get("common_variable", "device_prompt")

    @abstractmethod
    def login(self, address, username, password):
        pass

    @abstractmethod
    def get_resource_description(self, address):
        pass

    @abstractmethod
    def map_bidi(self, src_port, dst_port):
        pass

    @abstractmethod
    def map_clear_to(self, src_port, dst_port):
        pass

    @abstractmethod
    def map_clear(self, src_port, dst_port):
        pass

    # @abstractmethod
    # def set_speed_manual(self, src_port, dst_port, speed, duplex):
    #     pass
    #
    # @abstractmethod
    # def get_attribute_value(self, address, attribute_name):
    #     pass
