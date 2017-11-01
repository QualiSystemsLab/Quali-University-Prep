#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import re
from datetime import datetime
import traceback
import time

from xml_wrapper import XMLWrapper
from helper.system_helper import get_file_path
from configuration_parser import ConfigurationParser


class RequestManager:
    def __init__(self, buffer_size=2048):
        self._buffer_size = buffer_size
        self._connection_socket = None
        self._request_handler = None

        self._server_socket_timeout = ConfigurationParser.get("common_variable", "server_timeout")
        self._commands_dict = dict()

        self._re_command_end = r'</Commands>'
        self._end_command = '\r\n'

        self._parsing_error_xml = XMLWrapper.parse_xml_from_file(get_file_path(ConfigurationParser.L1_CORE_FOLDER,
                                                                               'common/response_template/'
                                                                               'parsing_error.xml'))

        self._command_response_data = open(get_file_path(ConfigurationParser.L1_CORE_FOLDER,
                                                         'common/response_template/'
                                                         'command_response_template.xml')).read()

        self._responses_data = open(get_file_path(ConfigurationParser.L1_CORE_FOLDER,
                                                  'common/response_template/'
                                                  'responses_template.xml')).read()

    def set_request_handler(self, request_handler):
        self._request_handler = request_handler

    def bind_command(self, command_name, callback_tuple):
        self._commands_dict[command_name] = callback_tuple

    def _set_response_error(self, responses_node, error_code, error_text, xs_prefix=None):
        XMLWrapper.set_node_attr(responses_node, 'Success', attr_value='false')

        if xs_prefix is None:
            xs_prefix = '{http://schemas.qualisystems.com/ResourceManagement/DriverCommandResult.xsd}'

        error_node = XMLWrapper.get_child_node(responses_node, 'ErrorCode', xs_prefix)
        XMLWrapper.set_node_text(error_node, error_code)

        log_node = XMLWrapper.get_child_node(responses_node, 'Log', xs_prefix)
        XMLWrapper.set_node_text(log_node, error_text)

        return responses_node

    def parse_request(self, connection_socket, xml_logger, command_logger):
        self._connection_socket = connection_socket
        self._connection_socket.settimeout(self._server_socket_timeout)

        current_output = ''
        while True:
            try:
                input_buffer = self._connection_socket.recv(self._buffer_size)
                current_output += input_buffer.strip()
                if not current_output:
                    time.sleep(0.2)
                    continue
                #command_logger.debug('GOT: {}'.format(current_output))
            except socket.timeout:
                continue
            except Exception as error_object:
                tb = traceback.format_exc()
                command_logger.critical(tb)
                raise error_object

            match_result = re.search(self._re_command_end, current_output)
            if match_result:
                responses_node = XMLWrapper.parse_xml(self._responses_data)
                # temp = current_output.replace('\r', '') + "\n\n"
                # xml_logger.info(current_output.replace('\r', '') + "\n\n")

                try:

                    request_node = XMLWrapper.parse_xml(current_output)
                    current_output = ''
                except Exception as error_object:
                    tb = traceback.format_exc()
                    command_logger.critical(tb)
                    responses_node = self._set_response_error(responses_node, '0',
                                                              'Failed to parse the xml')

                    responses_str = XMLWrapper.get_string_from_xml(responses_node)
                    xml_logger.info(responses_str.replace('\r', '') + "\n\n")
                    self._connection_socket.send(responses_str + self._end_command)

                    current_output = ''
                    continue

                xs_prefix = XMLWrapper.get_node_prefix(request_node, 'xsi')

                for command_node in request_node:
                    # get commands list
                    command_name = XMLWrapper.get_node_attr(command_node, 'CommandName')
                    command_id = XMLWrapper.get_node_attr(command_node, 'CommandId')

                    if command_name is not None:
                        command_name_lower = command_name.lower()
                        command_logger.info('\n\n----------------------------\nGot command {0}\n>>>\n'.format(command_name ))
                        if not command_name_lower in self._commands_dict:
                            command_logger.info('{} Not implemented, skip'.format(command_name))
                        if command_name_lower in self._commands_dict:
                            command_logger.info('Start command {0}'.format(command_name_lower ))
                            callback_tuple = self._commands_dict[command_name_lower]

                            command_response_node = XMLWrapper.parse_xml(self._command_response_data)

                            XMLWrapper.set_node_attr(command_response_node, 'CommandName', attr_value=command_name)
                            XMLWrapper.set_node_attr(command_response_node, 'CommandId', attr_value=command_id)

                            timestamp_node = XMLWrapper.get_child_node(command_response_node, 'Timestamp')
                            #dd.mm.yyyy hh:mm:ss  , time.gmtime()
                            XMLWrapper.set_node_text(timestamp_node, datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

                            return_state = True
                            responce_info = None
                            try:
                                responce_info = callback_tuple[0](callback_tuple[1], command_node, xs_prefix,
                                                                  command_logger)
                            except Exception as error_object:
                                tb = traceback.format_exc()
                                command_logger.critical(tb)
                                return_state = False
                                command_logger.error(str(error_object))
                                self._set_response_error(responses_node, '0', str(error_object))

                            XMLWrapper.set_node_attr(command_response_node, 'Success',
                                                     attr_value=str(return_state).lower())

                            if responce_info is not None:
                                responses_info_node = XMLWrapper.get_child_node(command_response_node, "ResponseInfo")
                                XMLWrapper.append_child(responses_info_node, responce_info)

                                # exception for method GetStateID
                                if command_name_lower == 'getstateid':
                                    attr_prefix = 'http://www.w3.org/2001/XMLSchema-instance'
                                    #XMLWrapper.set_node_attr(responses_info_node, 'xmlns:xsi', attr_value=attr_prefix)
                                    XMLWrapper.set_node_attr(responses_info_node, 'type',
                                                             '{' + attr_prefix + '}', attr_value ='StateInfo')

                                # exception for method GetAttributeValue
                                if command_name_lower == 'getattributevalue':
                                    attr_prefix = 'http://www.w3.org/2001/XMLSchema-instance'
                                    #XMLWrapper.set_node_attr(responses_info_node, 'xmlns:xsi', attr_value=attr_prefix)
                                    XMLWrapper.set_node_attr(responses_info_node, 'type',
                                                             '{' + attr_prefix + '}', attr_value ='AttributeInfoResponse')

                            XMLWrapper.append_child(responses_node, command_response_node)
                        else:
                            responses_node = self._set_response_error(responses_node, '404',
                                                                      'Command not found!')
                responce_str = XMLWrapper.get_string_from_xml(responses_node)
                xml_logger.info(responce_str.replace('\r', '') + "\n")
                self._connection_socket.send(responce_str + self._end_command)
