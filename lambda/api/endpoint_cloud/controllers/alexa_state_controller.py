# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
"""Module
"""

from endpoint_cloud.device import device_state
from .base_controller import BaseController, AlexaResponse

DEFAULT_VAL = {
    "Alexa.RangeController": 1,
    "Alexa.PowerController": "OFF",
    "Alexa.ToggleController": "OFF",
}


class AlexaStateController(BaseController):
    def process(self) -> AlexaResponse:
        if self.name == "ReportState":
            capabilities = self.get_capabilities()
            props = []
            for c in capabilities:
                if not "properties" in c:
                    continue
                retrievable = c["properties"].get("retrievable", False)
                if retrievable:
                    props.append(c)

            print(
                "LOG -- AlexaStateController.process: Creating StateReport for",
                self.user_id,
                "on endpoint",
                self.endpoint_id,
                "for properties",
                props,
            )
            self.alexa_response.set_name(name="StateReport")

            for p in props:
                key = p["properties"]["supported"][0]["name"]
                current_state = device_state.get_property_value(
                    endpoint_id=self.endpoint_id,
                    property_name=key,
                    instance=p.get("instance", None),
                    sku=self.get_sku(),
                )
                if not current_state is None:
                    if "instance" in p:
                        self.alexa_response.add_context_property(
                            namespace=p["interface"],
                            name=p["properties"]["supported"][0]["name"],
                            value=current_state,
                            instance=p["instance"],
                        )
                    else:
                        self.alexa_response.add_context_property(
                            namespace=p["interface"],
                            name=p["properties"]["supported"][0]["name"],
                            value=current_state,
                        )
            if len(self.alexa_response.context_properties) > 0:
                return self.alexa_response
            else:
                return self.make_error_response("Cannot get device state")
        return self.make_error_response(f"Name not supported {self.name}")
