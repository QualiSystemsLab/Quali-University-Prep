import os.path
import string
import random
import zipfile
import tempfile
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.api.cloudshell_api import ResourceInfoDto, PhysicalConnectionUpdateRequest
from shell_installer import *
from import_packages import *

debug_res_id = 'dbdda917-71d0-4110-a50a-1b1cbc8dd96b'
dev_helpers.attach_to_cloudshell_as('admin','admin','Global',debug_res_id)
res_id = ''

def execute():
    api = helpers.get_api_session()

    inputs = helpers.get_reservation_context_details().parameters.global_inputs
    res_id = helpers.get_reservation_context_details().id
    connectivity = helpers.get_connectivity_context_details()
    tempdir = tempfile.gettempdir()

    # install mock shells
    try:
        with zipfile.ZipFile(os.path.dirname(__file__), "r") as z:
            z.extractall(tempdir)

        shells = [tempdir + "\\Trafficshell.zip",
                  tempdir + "\\Putshell.zip",
                  tempdir + "\\L2Mockswitch.zip"]

        success = install_shells(connectivity, shells)
        api.WriteMessageToReservationOutput(reservationId=res_id, message='Shells installation results:\n' + success)
    except Exception as e:
        print e.message

    # get user/admin counts to create
    admins_count = 0
    if 'Number of Sys Admins' in inputs:
        admins_count = int(inputs['Number of Sys Admins'])

    users_count = 0
    if 'Number of Users' in inputs:
        users_count = int(inputs['Number of Users'])

    domain_admins_count = 0
    if 'Number of Domain Admins' in inputs:
        domain_admins_count = int(inputs['Number of Domain Admins'])

    # create domains and assign users group to them
    # first create users group
    try:
        api.AddNewGroup(groupName='Users Group', groupRole='Regular')
    except CloudShellAPIError as ex:
        pass  # probably group exists already

    # then create domain admins group
    try:
        api.AddNewGroup(groupName='Domain Admins', groupRole='DomainAdmin')
    except CloudShellAPIError as ex:
        pass  # probably group exists already

    # now create domains and assign the group to it
    domains_created = []
    for domain in ['Test Team NY', 'Test Team Calif', 'Consulting Phili']:
        try:
            api.AddNewDomain(domainName=domain)
            api.AddGroupsToDomain(domainName=domain, groupNames=['Users Group'])
            domains_created.append(domain)
            # assign networking service category to the new domains
            import_package(connectivity, domain, tempdir + "\\Networking Service Category.zip")
            api.AddGroupsToDomain(domainName=domain, groupNames=['Domain Admins'])
            if domain == 'Test Team NY':
                import_package(connectivity, domain, tempdir + "\\Apps for testing service category.zip")
        except CloudShellAPIError as ex:
            pass  # probably domain exists already
    api.WriteMessageToReservationOutput(res_id, 'Domains created: ' + ','.join(domains_created))

    # import the put blueprint
    try:
        api.WriteMessageToReservationOutput(res_id, 'Importing "PUT Traffic Test Blueprint"')
        import_package(connectivity, 'Test Team NY', tempdir + "\\PUT Traffic Test Blueprint.zip")
        api.WriteMessageToReservationOutput(res_id, 'Importing "PUT Traffic Test Blueprint" complete')
    except Exception as ex:
        api.WriteMessageToReservationOutput(res_id, 'Importing "PUT Traffic Test Blueprint" failed')
        pass

    # create users/admins
    groups = None
    if admins_count > 0:
        groups = api.GetGroupsDetails()
        sysadmin_group = [g for g in groups.Groups if g.Name == "System Administrators"][0]
        a = len(sysadmin_group.Users) + 1
        added_count = 0
        admins_created = []
        while added_count < admins_count:
            try:
                api.AddNewUser('admin' + str(a), 'admin' + str(a), '', isActive=True, isAdmin=True)
                added_count += 1
                admins_created.append('admin' + str(a))
            except:
                pass
            a += 1
        api.WriteMessageToReservationOutput(res_id, 'Admins created: ' + ','.join(admins_created))

    if domain_admins_count > 0:
        if groups is None:
            groups = api.GetGroupsDetails()
        dom_admin_group = [g for g in groups.Groups if g.Name == "Domain Admins"][0]
        a = len(dom_admin_group.Users) + 1
        added_count = 0
        dom_admins_created = []
        while added_count < domain_admins_count:
            try:
                api.AddNewUser('dadmin' + str(a), 'dadmin' + str(a), '', isActive=True, isAdmin=False)
                api.AddUsersToGroup(['dadmin' + str(a)], 'Domain Admins')
                added_count += 1
                dom_admins_created.append('dadmin' + str(a))
            except:
                pass
            a += 1
        api.WriteMessageToReservationOutput(res_id, 'Domain Admins created: ' + ','.join(dom_admins_created))

    if users_count > 0:
        api.WriteMessageToReservationOutput(res_id, 'Creating users and resources, this might take a while...')
        if groups is None:
            groups = api.GetGroupsDetails()
        users_group = [g for g in groups.Groups if g.Name == "Users Group"][0]
        a = len(users_group.Users) + 1
        added_count = 0
        users_created = []
        l2_resource_created = False
        while added_count < users_count:
            try:
                api.AddNewUser('user' + str(a), 'user' + str(a), '', isActive=True, isAdmin=False)
                api.AddUsersToGroup(['user' + str(a)], 'Users Group')
                added_count += 1
                users_created.append('user' + str(a))
            except:
                pass
            a += 1

            # create resources for this user (PUT+Traffic)
            try:
                api.CreateFolder('PUTs')
                #postfix_rn = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                postfix_rn = str(a-1)
                resource_name = 'Product Under Test - ' + postfix_rn
                api.CreateResource('CS_GenericResource', 'Putshell', resource_name, '10.10.10.' + str(a), 'PUTs', '',
                                   'A fake resource for training')
                api.UpdateResourceDriver(resource_name, 'Putshell')
                api.AutoLoad(resource_name)
                api.AddResourcesToDomain('Test Team NY', [resource_name], True)

                api.CreateFolder('Traffic Generators')
                #postfix_tg = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                postfix_tg = str(a-1)
                traffic_name = 'Traffic Generator 2.0 - ' + postfix_tg
                api.CreateResource('CS_GenericResource', 'Trafficshell', traffic_name, '10.10.11.' + str(a), 'Traffic Generators', '',
                                   'A fake resource for training')
                api.UpdateResourceDriver(traffic_name, 'Trafficshell')
                api.AutoLoad(traffic_name)
                api.AddResourcesToDomain('Test Team NY', [traffic_name], True)

                # connect devices to the patch panel
                patch_name = 'Patch Panel - Training'
                api.CreateResources([
                    ResourceInfoDto('Panel Jack', 'Generic Jack', 'Port 1 - PUT' + postfix_rn, '1', '', patch_name, ''),
                    ResourceInfoDto('Panel Jack', 'Generic Jack', 'Port 2 - PUT' + postfix_rn, '2', '',
                                    patch_name, ''),
                    ResourceInfoDto('Panel Jack', 'Generic Jack', 'Port 1 - TG' + postfix_tg, '1', '',
                                    patch_name, ''),
                    ResourceInfoDto('Panel Jack', 'Generic Jack', 'Port 2 - TG' + postfix_tg, '2', '',
                                    patch_name, '')
                ])
                api.AddResourcesToDomain('Test Team NY', [patch_name], True)
                api.UpdatePhysicalConnections([
                    PhysicalConnectionUpdateRequest(resource_name + '/Port 1', patch_name + '/Port 1 - PUT' + postfix_rn, 10),
                    PhysicalConnectionUpdateRequest(resource_name + '/Port 2', patch_name + '/Port 2 - PUT' + postfix_rn, 10),
                    PhysicalConnectionUpdateRequest(traffic_name + '/Port 1', patch_name + '/Port 1 - TG' + postfix_tg, 10),
                    PhysicalConnectionUpdateRequest(traffic_name + '/Port 2', patch_name + '/Port 2 - TG' + postfix_tg, 10)
                ])

                # create L2 mock switch if needed
                l2_training = 'L2 Mock Switch - Training'
                try:
                    if l2_resource_created == False:
                        try:
                            l2 = api.GetResourceDetails(l2_training)
                            l2_resource_created = True
                        except:
                            pass

                    if l2_resource_created == False:
                        api.CreateResource(resourceFamily='CS_Switch', resourceModel='L2Mockswitch',
                                           resourceName=l2_training, resourceAddress='1.2.3.4',
                                           folderFullPath='', parentResourceFullPath='',
                                           resourceDescription='A fake resource for training')
                        api.UpdateResourceDriver(l2_training, 'L2Mockswitch')
                        api.CreateResource(resourceFamily='CS_Chassis', resourceModel='L2Mockswitch.GenericChassis',
                                           resourceName='Chassis1', resourceAddress='1',
                                           folderFullPath='', parentResourceFullPath=l2_training,
                                           resourceDescription='')
                except Exception as ex:
                    api.WriteMessageToReservationOutput(res_id, ex.message)
                    pass # resource probably exists already

                # add L2 ports and connect to PUT
                chassis_name = l2_training + '/Chassis1'
                api.CreateResources([
                    ResourceInfoDto('CS_Port', 'L2Mockswitch.GenericPort', 'Port 3 - PUT' + postfix_rn, '3', '',
                                    chassis_name, ''),
                    ResourceInfoDto('CS_Port', 'L2Mockswitch.GenericPort', 'Port 4 - PUT' + postfix_rn, '4', '',
                                    chassis_name, '')
                ])
                api.AddResourcesToDomain('Test Team NY', [l2_training], True)
                api.UpdatePhysicalConnections([
                    PhysicalConnectionUpdateRequest(resource_name + '/Port 3', chassis_name + '/Port 3 - PUT' + postfix_rn, 10),
                    PhysicalConnectionUpdateRequest(resource_name + '/Port 4', chassis_name + '/Port 4 - PUT' + postfix_rn, 10)
                ])

            except Exception as ex:
                api.WriteMessageToReservationOutput(res_id, ex.message)
                pass

        # try:
        #     api.AddTopologiesToDomain('Test Team NY', ['PUT Traffic Test'])
        # except:
        #     pass

        api.WriteMessageToReservationOutput(res_id, 'Users created: ' + ','.join(users_created))

    # place instruction files
    instructions_exists = os.path.isdir("C:\Program Files (x86)\QualiSystems\CloudShell\Portal\PUTInstructionsFiles")
    if not instructions_exists:
        tempdir = tempfile.gettempdir()

        with zipfile.ZipFile(os.path.dirname(__file__), "r") as z:
            z.extractall(tempdir)

        # extract the inner zip to site-packages
        with zipfile.ZipFile((tempdir + "\\PUTInstructionsFiles.zip"), "r") as z:
            z.extractall("C:\Program Files (x86)\QualiSystems\CloudShell\Portal")



    print 'done'

