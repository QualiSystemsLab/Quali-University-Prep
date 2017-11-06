import json
from urllib2 import HTTPError
from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import ShellNotFoundException, FeatureUnavailable
from cloudshell.helpers.scripts.cloudshell_scripts_helpers import ConnectivityContextDetails

def install_shells(connectivity, shells):
    """
    :param ConnectivityContextDetails connectivity: connection details
    :param list[str] shells: path to the shells
    :return:
    """
    client = _open_connection_to_quali_server(connectivity.server_address,
                                              connectivity.admin_user,
                                              connectivity.admin_pass,
                                              9000,
                                              'Global')

    success = ''
    for shell in shells:
        success += _add_new_shell(client, shell)

    return success


def _open_connection_to_quali_server(host, user, password, port, domain, retry=3):
    if retry == 0:
        raise Exception("Connection to CloudShell Server failed. Please make sure it is up and running properly.")

    try:
        client = PackagingRestApiClient(ip=host,
                                        username=user,
                                        port=port,
                                        domain=domain,
                                        password=password)
        return client
    except HTTPError as e:
        if e.code == 401:
            raise Exception(u"Login to CloudShell failed. Please verify the credentials in the config")
        raise Exception("Connection to CloudShell Server failed. Please make sure it is up and running properly.")
    except:
        return _open_connection_to_quali_server(host, user, password, port, domain, retry - 1)


def _add_new_shell(client, package_full_path):
    try:
        client.add_shell(package_full_path)
        return package_full_path + ' installed\n'
    except Exception as e:
        if 'already exists' in e.message:
            return package_full_path + ' already installed\n'
        else:
            # raise Exception(_parse_installation_error("Failed to add new shell", e))
            return package_full_path + ' failed to install: ' + _parse_installation_error("Failed to add new shell", e)


def _parse_installation_error(base_message, error):
    cs_message = json.loads(error.message)["Message"]
    return "{}. CloudShell responded with: '{}'\n".format(base_message, cs_message)
