from rest_api_ext import PackagingRestApiClientExt
from urllib2 import HTTPError


def import_package(connectivity, domain, package_path):
    """

    :param ConnectivityContextDetails connectivity: connection details
    :param str domain: domain name
    :param str package_path: path to the package
    """

    client = _open_connection_to_quali_server(connectivity.server_address,
                                              connectivity.admin_user,
                                              connectivity.admin_pass,
                                              9000,
                                              domain)
    client.import_package(package_path)


def _open_connection_to_quali_server(host, user, password, port, domain, retry=3):
    if retry == 0:
        raise Exception("Connection to CloudShell Server failed. Please make sure it is up and running properly.")

    try:
        client = PackagingRestApiClientExt(ip=host,
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



