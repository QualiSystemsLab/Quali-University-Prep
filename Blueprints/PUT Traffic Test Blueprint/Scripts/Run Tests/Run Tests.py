import time
import os
from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
import traceback
import cloudshell.helpers.scripts.cloudshell_scripts_helpers as helpers


api = helpers.get_api_session()
res_id = helpers.get_reservation_context_details().id

resource_commands_dict = {'Trafficshell': 'start_traffic',
                          'Putshell': 'health_check'}

for resource in api.GetReservationDetails(res_id).ReservationDescription.Resources:
    _resource = resource.Name
    if '/' in _resource:
        continue

    resource_model = resource.ResourceModelName

    for model in resource_commands_dict:
        if model == resource_model:
            api.WriteMessageToReservationOutput(res_id, "Running Command: \"" + resource_commands_dict[model] +
                                                '" On Resource: \"' + _resource + '"')
            api.ExecuteCommand(res_id, _resource, 'Resource', resource_commands_dict[model])
            break
