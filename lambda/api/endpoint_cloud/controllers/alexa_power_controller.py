# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import json

from botocore.exceptions import ClientError
from alexa.skills.smarthome import AlexaResponse
from .base_controller import BaseController
from endpoint_cloud.device import power_controller

class AlexaPowerController(BaseController):
    def process(self):
        # Convert to a local stored state
        try:
            power_state_value = power_controller.set_state(self.endpoint_id, self.instance, self.name == "TurnOn")
            self.alexa_response.add_context_property(namespace='Alexa.PowerController', name='powerState', value=power_state_value)

        except Exception as e:
            print('ERR api_handler_directive.process.power_controller Exception:ClientError:', e)
            return  self.make_error_response(e)
        return self.alexa_response
