
from cloudshell.networking.apply_connectivity.apply_connectivity_operation import apply_connectivity_changes
from cloudshell.networking.apply_connectivity.models.connectivity_result import ConnectivitySuccessResponse
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext


#from data_model import *  # run 'shellfoundry generate' to generate data model classes

class L2MockswitchDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    # <editor-fold desc="Connectivity Provider Interface (Optional)">

    # The ApplyConnectivityChanges function is intended to be used for using switches as connectivity providers
    # for other devices. If the Switch shell is intended to be used a DUT only there is no need to implement it

    def ApplyConnectivityChanges(self, context, request):
        """
        Configures VLANs on multiple ports or port-channels
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str request: A JSON object with the list of requested connectivity changes
        :return: a json object with the list of connectivity changes which were carried out by the switch
        :rtype: str
        """

        return apply_connectivity_changes(request=request,
                                          add_vlan_action=lambda x: ConnectivitySuccessResponse(x,'Success'),
                                          remove_vlan_action=lambda x: ConnectivitySuccessResponse(x,'Success'))

    # </editor-fold>

    # <editor-fold desc="Discovery">

    # def get_inventory(self, context):
    #     """
    #     Discovers the resource structure and attributes.
    #     :param AutoLoadCommandContext context: the context the command runs on
    #     :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
    #     :rtype: AutoLoadDetails
    #     """
    #
    #     # See below some example code demonstrating how to return the resource structure and attributes
    #     # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
    #     # run 'shellfoundry generate' in order to create classes that represent your data model
    #
    #     '''
    #     resource = L2Mockswitch.create_from_context(context)
    #     resource.vendor = 'specify the shell vendor'
    #     resource.model = 'specify the shell model'
    #
    #     chassis1 = GenericChassis('Chassis 1')
    #     chassis1.model = 'WS-X4232-GB-RJ'
    #     chassis1.serial_number = 'JAE053002JD'
    #     resource.add_sub_resource('1', chassis1)
    #
    #     module1 = GenericModule('Module 1')
    #     module1.model = 'WS-X5561-GB-AB'
    #     module1.serial_number = 'TGA053972JD'
    #     chassis1.add_sub_resource('1', module1)
    #
    #     port1 = GenericPort('Port 1')
    #     port1.mac_address = 'fe80::e10c:f055:f7f1:bb7t16'
    #     port1.ipv4_address = '192.168.10.7'
    #     module1.add_sub_resource('1', port1)
    #
    #     return resource.create_autoload_details()
    #     '''
    #     return AutoLoadDetails([], [])
    #
    # # </editor-fold>



    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass