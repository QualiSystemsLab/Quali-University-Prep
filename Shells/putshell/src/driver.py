from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from data_model import *
from cloudshell.api.cloudshell_api import CloudShellAPISession as Cs_Api, \
    ResourceAttributesUpdateRequest, AttributeNameValue
from cloudshell.core.logger.qs_logger import get_qs_logger
import random
import time


class PutshellDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self._logger = None
        self._api_session = None
        self.cs_api = Cs_Api
        self.cloudshell_server = None
        self.admin_token = None
        self.reservation_id = None
        self.cs_domain = 'Global'
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        # See below some example code demonstrating how to return the resource structure and attributes
        # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
        # run 'shellfoundry generate' in order to create classes that represent your data model
        self._logger = self._get_logger(context)

        resource = Putshell.create_from_context(context)
        resource.vendor = 'Big Vendor'
        resource.model = 'Model 1'

        port = ResourcePort('Port 1')
        resource.add_sub_resource('1', port)
        port = ResourcePort('Port 2')
        resource.add_sub_resource('2', port)
        port = ResourcePort('Port 3')
        resource.add_sub_resource('3', port)
        port = ResourcePort('Port 4')
        resource.add_sub_resource('4', port)

        autoload_details = resource.create_autoload_details()
        self._logger.info('autoload attributes: ' + ','.join([str(vars(x)) for x in autoload_details.attributes]))
        self._logger.info('autoload resources: ' + ','.join([str(vars(x)) for x in autoload_details.resources]))
        return autoload_details

    # </editor-fold>

    # <editor-fold desc="Commands">

    def health_check(self, context):
        """
        :type context: ResourceCommandContext
        """
        self._logger = self._get_logger(context)
        self._api_session = self._get_api_session(context)

        self._write_message_to_reservation_console("Starting Health Check on: \"" + context.resource.name + '"')
        time.sleep(5)
        cpu_load = random.randrange(0, 100)
        memory_load = random.randrange(0, 100)
        hdd_load = random.randrange(0, 100)
        self._write_message_to_reservation_console("CPU Load is: " + str(cpu_load))
        self._write_message_to_reservation_console("Memory Load is: " + str(memory_load))
        self._write_message_to_reservation_console("HDD Load is: " + str(hdd_load))
        self._api_session.SetAttributesValues([ResourceAttributesUpdateRequest(context.resource.fullname,
                                                                          [AttributeNameValue('Putshell.CPU Load',
                                                                                              str(cpu_load)),
                                                                           AttributeNameValue('Putshell.Memory Load',
                                                                                              str(memory_load)),
                                                                           AttributeNameValue('Putshell.HDD Load',
                                                                                              str(hdd_load))])])
        self._api_session.SetResourceLiveStatus(context.resource.fullname, 'Online', '')


    # </editor-fold>

    # private functions

    def _get_api_session(self, context):
        try:
            self._get_cloudshell_session(context)
            self._api_session = self.cs_api(host=self.cloudshell_server, token_id=self.admin_token,
                                            domain=self.cs_domain)
            self._log_message("Successfully got CS API Session")
        except Exception, expt:
            self._log_message("Failed to get CS API Session, Error: \"" + str(expt) + "\"")
            raise Exception("Failed to get CS API Session, Error: \"" + str(expt) + "\"")

        return self._api_session

    def _get_logger(self, context):
        """
        returns a logger
        :param context:
        :return: the logger object
        :rtype: logging.Logger
        """
        try:
            try:
                res_id = context.reservation.reservation_id
            except:
                res_id = 'out-of-reservation'
            try:
                resource_name = context.resource.fullname
            except:
                resource_name = 'no-resource'
            logger = get_qs_logger(res_id, 'PutShellDriver', resource_name)
            return logger
        except Exception as e:
            return None

    def _get_cloudshell_session(self, context):
        """
        :type context: ResourceCommandContext
        """
        self.admin_token = context.connectivity.admin_auth_token
        self.cloudshell_server = context.connectivity.server_address
        self.reservation_id = context.reservation.reservation_id

    def _log_message(self, message):

        if self._logger:
            try:
                time.strptime(message[:19], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                message = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + message

            if not (message.endswith('\r\n')) or not (message.endswith('\n')):
                message += '\r\n'

            self._logger.info(message)

    def _write_message_to_reservation_console(self, message):
        self._log_message("Sending Reservation Message: \"" + message + '"')
        self._api_session.WriteMessageToReservationOutput(self.reservation_id, message)
