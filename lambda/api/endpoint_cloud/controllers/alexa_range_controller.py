# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import json
import typing

from botocore.exceptions import ClientError
from alexa.skills.smarthome import AlexaResponse
from .base_controller import BaseController
from endpoint_cloud.device import range_controller


class AlexaRangeController(BaseController):
    def process(self):
        capabilities = self.get_capabilities()

        for c in capabilities:
            if "instance" in c and c["instance"] == self.instance:
                MIN_VAL = c["configuration"]["supportedRange"]["minimumValue"]
                MAX_VAL = c["configuration"]["supportedRange"]["maximumValue"]
                PRECISION = c["configuration"]["supportedRange"]["precision"]
                break

        value = 0
        if self.name == "AdjustRangeValue":
            range_value_delta = self.directive["payload"]["rangeValueDelta"]
            range_value_delta_default = self.directive["payload"][
                "rangeValueDeltaDefault"
            ]
            # Check to see if we need to use the delta default value (The user did not give a precision)
            if range_value_delta_default:
                range_value_delta = PRECISION

            # Lookup the existing value of the endpoint by endpoint_id and limit ranges as appropriate - for this sample, expecting 1-6
            current_range_value = range_controller.get_value(
                self.endpoint_id, self.instance
            )
            new_range_value = current_range_value + range_value_delta
            value = max(min(new_range_value, MAX_VAL), MIN_VAL)

        if self.name == "SetRangeValue":
            range_value = self.directive["payload"]["rangeValue"]

            value = max(min(range_value, MAX_VAL), MIN_VAL)

        self.alexa_response.add_context_property(
            namespace="Alexa.RangeController",
            name="rangeValue",
            value=value,
            instance=self.instance,
        )

        try:
            range_controller.set_value(self.endpoint_id, self.instance, value)

        except Exception as e:
            return self.make_error_response(e)

        # Send back the response
        return self.alexa_response
