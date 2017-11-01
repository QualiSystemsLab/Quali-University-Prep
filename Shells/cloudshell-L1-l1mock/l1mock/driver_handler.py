from common.driver_handler_base import DriverHandlerBase
from common.configuration_parser import ConfigurationParser
from common.resource_info import ResourceInfo
import time


class L1mockDriverHandler(DriverHandlerBase):

    def __init__(self):
        DriverHandlerBase.__init__(self)
        self._switch_model = "L1Mock"
        self._blade_model = "L1Mock Blade"
        self._port_model = "L1Mock Port"


    def login(self, address, username, password, command_logger=None):
        """Perform login operation on the device

        :param address: (str) address attribute from the CloudShell portal
        :param username: (str) username to login on the device
        :param password: (str) password for username
        :param command_logger: logging.Logger instance
        :return: None

        Example:
        self._session.connect(host, username, password, re_string=self._prompt)
        command = 'login {} {}'.format(username, password)
        error_map = OrderedDict([
            ("[Aa]ccess [Dd]enied", "Invalid username/password for login"),
        ])
        self._session.send_command(command, re_string=self._prompt, error_map=error_map)
        """
        pass

    def get_resource_description(self, address, command_logger=None):
        """Auto-load function to retrieve all information from the device

        :param address: (str) address attribute from the CloudShell portal
        :param command_logger: logging.Logger instance
        :return: xml.etree.ElementTree.Element instance with all switch sub-resources (blades, ports)
        """

        number_of_blades = ConfigurationParser.get("driver_variable", "number_of_blades")
        ports_per_blade = ConfigurationParser.get("driver_variable", "ports_per_blade")

        # Step 1. Create root element (switch):
        depth = 0
        resource_info = ResourceInfo()
        resource_info.set_depth(depth)
        resource_info.set_address(address)
        resource_info.set_index("L1Mock")

        # Step 2. Create child resources for the root element (blades):
        for blade_no in xrange(number_of_blades):
            blade_resource = ResourceInfo()
            blade_resource.set_depth(depth + 1)
            blade_resource.set_index(str(blade_no+1))
            resource_info.add_child(blade_no+1, blade_resource)

            # Step 3. Create child resources for each root sub-resource (ports in blades)
            for port_no in xrange(ports_per_blade):
                port_resource = ResourceInfo()
                port_resource.set_depth(depth + 2)
                port_resource.set_index("%03d" % (port_no+1))
                blade_resource.add_child(port_no+1, port_resource)

        return resource_info.convert_to_xml()

    def _fake_operation_duration(self, command_logger):
        try:
            operation_duration = ConfigurationParser.get("driver_variable", "operation_duration_sec")
            command_logger.info("operation_duration_sec: %d" % operation_duration)
        except Exception as ex:
            command_logger.info("operation_duration_sec failed: " + ex.message)
            operation_duration = 5

        time.sleep(operation_duration)

    def map_bidi(self, src_port, dst_port, command_logger):
        """Create a bidirectional connection between source and destination ports

        :param src_port: (list) source port in format ["<address>", "<blade>", "<port>"]
        :param dst_port: (list) destination port in format ["<address>", "<blade>", "<port>"]
        :param command_logger: logging.Logger instance
        :return: None

        Example:
        error_map = OrderedDict([
            ("error|ERROR", "Failed to perform command"),
        ])
        command = "connect duplex {} to {}".format(src_port, dst_port)
        return self._session.send_command(command, re_string=self._prompt, error_map=error_map)
        """
        self._fake_operation_duration(command_logger)
        pass

    def map_uni(self, src_port, dst_port, command_logger):
        """Create a unidirectional connection between source and destination ports

        :param src_port: (list) source port in format ["<address>", "<blade>", "<port>"]
        :param dst_port: (list) destination port in format ["<address>", "<blade>", "<port>"]
        :param command_logger: logging.Logger instance
        :return: None

        Example:
        error_map = OrderedDict([
            ("error|ERROR", "Failed to perform command"),
        ])
        command = "connect simplex {} to {}".format(src_port, dst_port)
        self._session.send_command(command, re_string=self._prompt, error_map=error_map)
        """
        self._fake_operation_duration(command_logger)
        pass

    def map_clear_to(self, src_port, dst_port, command_logger):
        """Remove simplex/multi-cast/duplex connection ending on the destination port

        :param src_port: (list) source port in format ["<address>", "<blade>", "<port>"]
        :param dst_port: (list) destination port in format ["<address>", "<blade>", "<port>"]
        :param command_logger: logging.Logger instance
        :return: None

        Example:
        error_map = OrderedDict([
            ("error|ERROR", "Failed to perform command"),
        ])
        command = "disconnect simplex {} from {}".format(src_port, dst_port)
        self._session.send_command(command, re_string=self._prompt, error_map=error_map)
        """
        self._fake_operation_duration(command_logger)
        pass

    def map_clear(self, src_port, dst_port, command_logger):
        """Remove simplex/multi-cast/duplex connection ending on the destination port

        :param src_port: (list) source port in format ["<address>", "<blade>", "<port>"]
        :param dst_port: (list) destination port in format ["<address>", "<blade>", "<port>"]
        :param command_logger: logging.Logger instance
        :return: None

        Example:
        error_map = OrderedDict([
            ("error|ERROR", "Failed to perform command"),
        ])
        command = "disconnect duplex {} from {}".format(src_port, dst_port)
        self._session.send_command(command, re_string=self._prompt, error_map=error_map)
        """
        self._fake_operation_duration(command_logger)
        pass

    def set_speed_manual(self, command_logger):
        """Set speed manual - legacy command, do not delete, no need to change

        :param command_logger: logging.Logger instance
        :return: None
        """
        pass
