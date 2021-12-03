# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT
'''Module
'''

from endpoint_cloud.device import device_state
from .base_controller import BaseController, AlexaResponse

DEFAULT_VAL = {
    "Alexa.RangeController": 1, 
    "Alexa.PowerController": "OFF", 
    "Alexa.ToggleController": "OFF"
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

            state = device_state.get_state(self.endpoint_id)

            print(
                "Sending StateReport for",
                self.user_id,
                "on endpoint",
                self.endpoint_id,
            )
            self.alexa_response.set_name(name='StateReport')

            for p in props:
                key = p["properties"]["supported"][0]["name"]
                if "instance" in p:
                    key = p["instance"] + "." + key
                current_state = state.get(key, DEFAULT_VAL[p["interface"]])
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

            return self.alexa_response
        return self.make_error_response(f"Name not supported {self.name}")