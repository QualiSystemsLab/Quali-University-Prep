import urllib2
import os
from requests import post
from cloudshell.rest.api import PackagingRestApiClient


class PackagingRestApiClientExt(PackagingRestApiClient):
    def import_package(self, package_path):
        url = 'http://{0}:{1}/API/Package/ImportPackage'.format(self.ip, self.port)
        response = post(url,
                        files={os.path.basename(package_path): open(package_path, 'rb')},
                        headers={'Authorization': 'Basic ' + self.token})

        if response.status_code != 200:
            raise Exception(response.text)
