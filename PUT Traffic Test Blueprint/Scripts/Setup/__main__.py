from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow

def custom_function(sandbox, components):
    """
    :param Sandbox sandbox:
    """
    for resource in components:
        if '/' in resource:
            continue
        sandbox.automation_api.SetResourceLiveStatus(resource, 'Online')

    res = sandbox.automation_api.GetReservationDetails(sandbox.id)

    for route in res.ReservationDescription.RequestedRoutesInfo:
        sandbox.automation_api.ConnectRoutesInReservation(sandbox.id, endpoints=[route.Source, route.Target],
                                                          mappingType=route.RouteType)
    pass

sandbox = Sandbox()

DefaultSetupWorkflow().register(sandbox)

resources = sandbox.components.resources

sandbox.workflow.on_connectivity_ended(custom_function, resources)

sandbox.execute_setup()
