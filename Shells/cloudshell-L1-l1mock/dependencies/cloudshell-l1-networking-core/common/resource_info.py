#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from common.configuration_parser import ConfigurationParser
from helper.system_helper import get_file_path
from xml_wrapper import XMLWrapper


class ResourceInfo:
    def __init__(self):
        self._depth = -1
        self._index = -1
        self._address = -1
        self._serial_number = -1
        self._model_name = ""

        self._map_path = ""

        self._attributes_data = dict()
        self._child_resource_data = OrderedDict()

    def _get_attribute_type(self, value):
        if isinstance(value, basestring):
            return "String"
        elif isinstance(value, int):
            return "Numeric"

        raise Exception("ResourceInfo", "Can't get attribute type from resource '" + str(self._address) + "'!")

    def set_model_name(self, name):
        self._model_name = name

    def set_serial_number(self, number):
        self._serial_number = number

    def set_address(self, address):
        self._address = address

    def set_mapping(self, map_path):
        self._map_path = map_path

    def set_index(self, index):
        self._index = index

    def set_depth(self, depth):
        self._depth = depth

    def add_child(self, key, child_resource):
        self._child_resource_data[key] = child_resource

    def add_attribute(self, name, value):
        self._attributes_data[name] = value

    def get_resource_attribute(self, name, index=None):
        resource_name_template = ConfigurationParser.get('driver_variable', name, self._depth)
        if index is not None:
            resource_name_template = resource_name_template.format(index)
        return resource_name_template

    def convert_to_xml(self, resource_template=None, attribute_template=None, incoming_map_template=None, relative_address=''):
        if resource_template is None:
            resource_template = open(get_file_path(ConfigurationParser.L1_CORE_FOLDER,
                                                   'common/response_template/'
                                                   'resource_template.xml')).read()

        if attribute_template is None:
            attribute_template = open(get_file_path(ConfigurationParser.L1_CORE_FOLDER,
                                                    'common/response_template/'
                                                    'resource_attribute_template.xml')).read()

        if incoming_map_template is None:
            incoming_map_template = open(get_file_path(ConfigurationParser.L1_CORE_FOLDER,
                                                       'common/response_template/'
                                                       'resource_incoming_map_template.xml')).read()

        resource_node = XMLWrapper.parse_xml(resource_template)

        XMLWrapper.set_node_attr(resource_node, "Name",
                                 attr_value=self.get_resource_attribute("resource_name", self._index))
        XMLWrapper.set_node_attr(resource_node, "ResourceFamilyName",
                                 attr_value=self.get_resource_attribute("resource_family_name"))
        XMLWrapper.set_node_attr(resource_node, "ResourceModelName",
                                 attr_value=self.get_resource_attribute("resource_model_name", self._model_name))
        XMLWrapper.set_node_attr(resource_node, "SerialNumber",
                                 attr_value=self._serial_number)

        if self._depth != 0:
            relative_address += "/" + str(self._index)
        else:
            relative_address = self._address

        XMLWrapper.set_node_attr(resource_node, "Address", attr_value=relative_address)

        resource_attributes_node = XMLWrapper.get_child_node(resource_node, "ResourceAttributes")
        for name, value in self._attributes_data.items():
            attribute_node = XMLWrapper.parse_xml(attribute_template)

            type_str = self._get_attribute_type(value)

            XMLWrapper.set_node_attr(attribute_node, "Name", attr_value=name)
            XMLWrapper.set_node_attr(attribute_node, "Type", attr_value=type_str)
            XMLWrapper.set_node_attr(attribute_node, "Value", attr_value=str(value))

            XMLWrapper.append_child(resource_attributes_node, attribute_node)

        if len(self._map_path) > 0:
            incoming_map_node = XMLWrapper.parse_xml(incoming_map_template)
            child_incoming_node = XMLWrapper.get_child_node(incoming_map_node, "IncomingMapping")
            XMLWrapper.set_node_text(child_incoming_node, self._map_path)
            XMLWrapper.append_child(resource_node, incoming_map_node)

        child_resources_node = XMLWrapper.get_child_node(resource_node, "ChildResources")
        for index, value in self._child_resource_data.items():
            child_resource_node = value.convert_to_xml(resource_template, attribute_template, incoming_map_template,
                                                       relative_address)
            XMLWrapper.append_child(child_resources_node, child_resource_node)

        return resource_node
