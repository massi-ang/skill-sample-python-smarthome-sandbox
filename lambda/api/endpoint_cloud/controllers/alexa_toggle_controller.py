# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
'''Module
'''
from endpoint_cloud.device import toggle_controller
from .base_controller import BaseController

class AlexaToggleController(BaseController):
    '''AlexaToggleController
    '''
    def process(self):
        try:
            toggle_state_value = toggle_controller.set_state(endpoint_id=self.endpoint_id, instance=self.instance, op=self.name)

            self.alexa_response.add_context_property(
                namespace='Alexa.ToggleController',
                name='toggleState',
                instance=self.instance,
                value=toggle_state_value)
            self.alexa_response.add_context_property()
            
        except Exception as e:
            print('ERR api_handler_directive.process.toggle_controller Exception:ClientError:', e)
            return self.make_error_response(e)
        
        return self.alexa_response
