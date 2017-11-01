#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import os
from thread import start_new_thread
import traceback

from common.configuration_parser import ConfigurationParser
from cloudshell.core.logger.qs_logger import get_qs_logger


class ServerConnection:
    def __init__(self, host, port, request_manager, exe_folder_str):
        def __export_log_path():
            os.environ['LOG_PATH'] = os.path.join(exe_folder_str, '..', 'Logs')

        __export_log_path()
        driver_name = ConfigurationParser.get("common_variable", "driver_name")

        self._xml_logger = get_qs_logger(log_group=driver_name + '_xml',
                                         log_file_prefix=driver_name + '_xml', log_category='XML')

        self._command_logger = get_qs_logger(log_group=driver_name + '_commands',
                                             log_file_prefix=driver_name + '_commands', log_category='COMMANDS')
        print 'Logger created with path {}'.format(self._command_logger.handlers[0]._handler.baseFilename)

        self._command_logger.info("Driver name: " + driver_name)
        self._command_logger.info("Driver host: " + host)
        self._command_logger.info("Driver port: " + str(port))

        self._is_running = True

        self._host = host
        self._port = port

        self._request_manager = request_manager

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._command_logger.debug('New socket created')

        try:
            self._server_socket.bind((self._host, self._port))

        except socket.error as error_object:
            # log will be  here
            self._command_logger.error(str(error_object))
            raise Exception('ServerConnection', 'Can\'t bind host and port: ' + self._host + ':' + self._port + '!')

        self._command_logger.debug('Start listenning ...')
        self._server_socket.listen(100)

    def _get_accept_socket(self):
        return self._server_socket.accept()

    def set_running(self, is_running):

        self._is_running = is_running

    def start_listeninig(self):
        while self._is_running:
            connection_data = self._get_accept_socket()
            self._command_logger.debug("New connection id: " + str(connection_data[0].fileno()))

            if connection_data is not None:
                connection_socket = connection_data[0]
                from threading import Thread
                t = Thread(target=self._request_manager.parse_request, args=(connection_socket, self._xml_logger,
                                                                       self._command_logger,))
                t.start()
                #try:
                #    start_new_thread(self._request_manager.parse_request, (connection_socket, self._xml_logger,
                #                                                       self._command_logger))
#
#
#
                #except Exception, e:
                #    tb = traceback.format_exc()
                #    self._command_logger.critical(tb)
