# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import logging
from .base_controller import BaseController
from endpoint_cloud.device import power_controller

logger = logging.getLogger(__name__)

class AlexaPowerController(BaseController):
    def process(self):
        try:
            state = "ON" if self.name == "TurnOn" else "OFF"
            power_state_value = power_controller.set_state(
                endpoint_id=self.endpoint_id, state=state, sku=self.get_sku()
            )
            self.alexa_response.add_context_property(
                namespace="Alexa.PowerController",
                name="powerState",
                value=power_state_value,
            )

        except Exception as ex:
            logger.error(
                "api_handler_directive.process.power_controller Exception: ClientError: %s", ex
            )
            return self.make_error_response(ex)
        return self.alexa_response
