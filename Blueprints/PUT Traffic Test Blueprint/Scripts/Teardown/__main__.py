from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.teardown.default_teardown_orchestrator import DefaultTeardownWorkflow

def custom_function(sandbox, components):
    """
    :param Sandbox sandbox:
    """
    for resource in components:
        if '/' in resource:
            continue
        sandbox.automation_api.SetResourceLiveStatus(resource, 'Offline')

    pass


sandbox = Sandbox()

DefaultTeardownWorkflow().register(sandbox)

resources = sandbox.components.resources

sandbox.workflow.add_to_teardown(custom_function, resources)

sandbox.execute_teardown()
