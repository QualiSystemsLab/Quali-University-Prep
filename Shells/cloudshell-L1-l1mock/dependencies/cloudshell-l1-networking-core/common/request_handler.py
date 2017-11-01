#!/usr/bin/python
# -*- coding: utf-8 -*-

import importlib

from common.configuration_parser import ConfigurationParser
from common.xml_wrapper import XMLWrapper
from helper.system_helper import get_file_path


class RequestHandler:
    def __init__(self):
        self._driver_handler = None
        self._state_id = '-1'

        self._device_address = None
        self._device_user = None
        self._device_password = None

        self._state_id_template = open(get_file_path(ConfigurationParser.L1_CORE_FOLDER,
                                                     'common/response_template/'
                                                     'state_id_template.xml')).read()
        self.init_driver_handler()

    def init_driver_handler(self):
        driver_module_data = ConfigurationParser.get('common_variable', 'driver_module')
        driver_module_name = driver_module_data[0]
        driver_class_name = driver_module_data[1]

        module = importlib.import_module(driver_module_name)
        if hasattr(module, driver_class_name):
            self._driver_handler = getattr(module, driver_class_name)()
            return

        raise Exception('RequestHandler', 'Can\'t found class in package!')

    def login(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="Login" CommandId="567f4dc1-e2e5-4980-b726-a5d906c8679b">
                <Parameters xsi:type="LoginCommandParameters">
                    <Address>192.168.28.223</Address>00
                    <User>root</User>
                    <Password>root</Password>
                </Parameters>
            </Command>
        </Commands>

        :param command_node:
        :return:
        """
        command_logger.info("Begin")
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))

        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)
        address_node = XMLWrapper.get_child_node(parameters_node, 'Address', xs_prefix)
        user_node = XMLWrapper.get_child_node(parameters_node, 'User', xs_prefix)
        password_node = XMLWrapper.get_child_node(parameters_node, 'Password', xs_prefix)

        address_str = XMLWrapper.get_node_text(address_node)
        user_str = XMLWrapper.get_node_text(user_node)
        password_str = XMLWrapper.get_node_text(password_node)

        response_node = None
        if self._device_address != address_str or self._device_user != user_str or \
                        self._device_password != password_str:
            response_node = self._driver_handler.login(address_str, user_str, password_str, command_logger)

        self._device_address = address_str
        self._device_user = user_str
        self._device_password = password_str

        command_logger.info(XMLWrapper.get_string_from_xml(response_node))
        command_logger.info("end")

        return response_node

    def get_resource_description(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="GetResourceDescription" CommandId="0d7000f2-dc20-401a-bdc6-09a2e1cb1f02">
                <Parameters xsi:type="GetResourceDescriptionParameters">
                    <Address>192.168.28.223</Address>
                </Parameters>
            </Command>
        </Commands>

        :param command_node:
        :return:
        """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        address_node = XMLWrapper.get_child_node(parameters_node, 'Address', xs_prefix)
        address_str = XMLWrapper.get_node_text(address_node)

        xml_description = self._driver_handler.get_resource_description(address_str, command_logger)
        command_logger.info(XMLWrapper.get_string_from_xml(xml_description))

        return xml_description

    def set_state_id(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="SetStateId" CommandId="29d2dd21-0a18-4c94-a43c-0f0e8f355151">
                <Parameters xsi:type="SetStateCommandParameters">
                    <StateId>635896045076120729</StateId>
                </Parameters>
            </Command>
        </Commands>

        :param command_node:
        :param xs_prefix:
        :return:
        """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)
        state_node = XMLWrapper.get_child_node(parameters_node, 'StateId', xs_prefix)

        self._state_id = XMLWrapper.get_node_text(state_node)

        return None

    def get_state_id(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="GetStateId" CommandId="9d75a6b5-3d1d-4e65-b3ba-42d7344adaef">
                <Parameters xsi:type="GetStateCommandParameters"/>
            </Command>
        </Commands>

        :param command_node:
        :param xs_prefix:
        :return:
        """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        state_id_node = XMLWrapper.parse_xml(self._state_id_template)
        XMLWrapper.set_node_text(state_id_node, '-1')

        return state_id_node

    def map_bidi(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="MapBidi" CommandId="c2a37eca-472f-4492-810e-cdc237a7c33a">
                <Parameters xsi:type="BiMappingCommandParameters">
                    <MapPort_A>192.168.28.223/91</MapPort_A>
                    <MapPort_B>192.168.28.223/10</MapPort_B>
                    <MappingGroupName/>
                </Parameters>
            </Command>
        </Commands>

        :param command_node:
        :param xs_prefix:
        :return:
        """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        src_port_node = XMLWrapper.get_child_node(parameters_node, 'MapPort_A', xs_prefix)
        dst_port_node = XMLWrapper.get_child_node(parameters_node, 'MapPort_B', xs_prefix)

        src_port_str = XMLWrapper.get_node_text(src_port_node)
        dst_port_str = XMLWrapper.get_node_text(dst_port_node)

        response = self._driver_handler.map_bidi(src_port_str.split('/'), dst_port_str.split('/'), command_logger)
        command_logger.info(XMLWrapper.get_string_from_xml(response))
        return response

    def map_clear_to(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="MapClearTo" CommandId="09cc9080-386b-4143-aaa0-a7211370304b">
                <Parameters xsi:type="MapClearToCommandParameters">
                    <SrcPort>192.168.28.223/2</SrcPort>
                    <DstPort>192.168.28.223/49</DstPort>
                </Parameters>
            </Command>
        </Commands>

       :param command_node:
       :param xs_prefix:
       :return:
       """

        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        src_port_node = XMLWrapper.get_child_node(parameters_node, 'SrcPort', xs_prefix)
        dst_port_node = XMLWrapper.get_child_node(parameters_node, 'DstPort', xs_prefix)

        src_port_str = XMLWrapper.get_node_text(src_port_node)
        dst_port_str = XMLWrapper.get_node_text(dst_port_node)

        response = self._driver_handler.map_clear_to(src_port_str.split('/'), dst_port_str.split('/'), command_logger)
        command_logger.info(XMLWrapper.get_string_from_xml(response))
        return response

    def map_clear(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="MapClear" CommandId="4fa3d6d9-e5b2-446a-9c39-6bfb12842d6c">
                <Parameters xsi:type="MapClearParameters">
                  <MapPort>192.168.28.223/88</MapPort>
                  <MapPort>192.168.28.223/13</MapPort>
                </Parameters>
            </Command>
        </Commands>

       :param command_node:
       :param xs_prefix:
       :return:
       """

        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        map_ports = XMLWrapper.get_all_child_node(parameters_node, 'MapPort', xs_prefix)

        src_port_str = XMLWrapper.get_node_text(map_ports[0])
        dst_port_str = XMLWrapper.get_node_text(map_ports[1])

        response = self._driver_handler.map_clear(src_port_str.split('/'), dst_port_str.split('/'), command_logger)
        command_logger.info(XMLWrapper.get_string_from_xml(response))
        return response

    def map_uni(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="MapUni" CommandId="09cc9080-386b-4143-aaa0-a7211370304b">
                <Parameters xsi:type="MapUniCommandParameters">
                    <SrcPort>192.168.28.223/2</SrcPort>
                    <DstPort>192.168.28.223/49</DstPort>
                </Parameters>
            </Command>
        </Commands>

       :param command_node:
       :param xs_prefix:
       :return:
       """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))

        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        src_port_node = XMLWrapper.get_child_node(parameters_node, 'SrcPort', xs_prefix)
        dst_port_node = XMLWrapper.get_child_node(parameters_node, 'DstPort', xs_prefix)

        src_port_str = XMLWrapper.get_node_text(src_port_node)
        dst_port_str = XMLWrapper.get_node_text(dst_port_node)

        response = self._driver_handler.map_uni(src_port_str.split('/'), dst_port_str.split('/'), command_logger)
        command_logger.info(XMLWrapper.get_string_from_xml(response))
        return response

    def map_tap(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="MapTap" CommandId="09cc9080-386b-4143-aaa0-a7211370304b">
                <Parameters xsi:type="MapTapCommandParameters">
                    <SrcPort>192.168.28.223/2</SrcPort>
                    <DstPort>192.168.28.223/49</DstPort>
                </Parameters>
            </Command>
        </Commands>

        :param command_node:
        :param xs_prefix:
        :return:
        """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))

        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        src_port_node = XMLWrapper.get_child_node(parameters_node, 'SrcPort', xs_prefix)
        dst_port_node = XMLWrapper.get_child_node(parameters_node, 'DstPort', xs_prefix)

        src_port_str = XMLWrapper.get_node_text(src_port_node)
        dst_port_str = XMLWrapper.get_node_text(dst_port_node)

        response = self._driver_handler.map_tap(src_port_str.split('/'), dst_port_str.split('/'), command_logger)
        command_logger.info(XMLWrapper.get_string_from_xml(response))
        return response

    def set_speed_manual(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="SetSpeedManual" CommandId="d361b400-75bc-4029-a697-7cf67e8e9d0c">
                <Parameters xsi:type="SetSpeedManualCommandParameters">
                  <SrcPort>192.168.2.41/12-12</SrcPort>
                  <DstPort>192.168.2.41/11-11</DstPort>
                  <Speed />
                  <Duplex />
                </Parameters>
          </Command>
        </Commands>

       :param command_node:
       :param xs_prefix:
       :return:
       """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        src_port  = XMLWrapper.get_node_text(XMLWrapper.get_child_node(parameters_node, 'SrcPort', xs_prefix))
        dst_port = XMLWrapper.get_node_text(XMLWrapper.get_child_node(parameters_node, 'DstPort', xs_prefix))
        speed = XMLWrapper.get_node_text(XMLWrapper.get_child_node(parameters_node, 'Speed', xs_prefix))
        duplex = XMLWrapper.get_node_text(XMLWrapper.get_child_node(parameters_node, 'Duplex', xs_prefix))

        # return self._driver_handler.set_speed_manual(src_port.split('/'), dst_port.split('/'), speed, duplex, command_logger)
        return self._driver_handler.set_speed_manual(command_logger)

    def get_attribute_value(self, command_node, xs_prefix='', command_logger=None):
        """
        <Commands xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/ResourceManagement/DriverCommands.xsd">
            <Command CommandName="GetAttributeValue" CommandId="c2a37eca-472f-4492-810e-cdc237a7c33a">
                <Parameters xsi:type="??????">
                    <Address>192.168.28.223/91</Address>
                    <Attribute>Serial Number</Attribute>
                </Parameters>
            </Command>
        </Commands>
        :param command_node:
        :param xs_prefix:
        :return:
        """
        command_logger.info(XMLWrapper.get_string_from_xml(command_node))
        parameters_node = XMLWrapper.get_child_node(command_node, 'Parameters', xs_prefix)

        address  = XMLWrapper.get_node_text(XMLWrapper.get_child_node(parameters_node, 'Address', xs_prefix))
        attr_name = XMLWrapper.get_node_text(XMLWrapper.get_child_node(parameters_node, 'Attribute', xs_prefix))

        # return self._driver_handler.get_attribute_value(address, attr_name, command_logger)
        return XMLWrapper.parse_xml('<Attribute Name="' + attr_name + '" Type="String" Value="fake_value"/>')

