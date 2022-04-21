# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

from logging import captureWarnings
import unittest
from unittest.mock import Mock
import json
from endpoint_cloud.controllers.alexa_state_controller import AlexaStateController
from endpoint_cloud.api_auth import ApiAuth


class StateReport(unittest.TestCase):
    capabilities = [
        {
            "type": "AlexaInterface",
            "interface": "Alexa.PowerController",
            "version": "3",
            "properties": {
                "supported": [{"name": "powerState"}],
                "proactivelyReported": True,
                "retrievable": True,
            },
        },
    ]

    def test_report_state(self):

        ApiAuth.get_user_id = Mock(
            return_value=json.dumps({"user_id": {}}).encode("utf8")
        )

        msg = {
            "directive": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ReportState",
                    "payloadVersion": "3",
                    "messageId": "b85fa90f-d311-44aa-b63e-ec0f38b58d53",
                    "correlationToken": "AAAA",
                },
                "endpoint": {
                    "scope": {"type": "BearerToken", "token": "Atza"},
                    "endpointId": "SAMPLE_ENDPOINT_3GKABU9O",
                    "cookie": {},
                },
                "payload": {},
            }
        }
        controller = AlexaStateController(msg["directive"])
        controller.get_endpoint = Mock(
            return_value={
                "Capabilities": json.dumps(self.capabilities),
                "SKU": "LI00-PARTICLE",
            }
        )
        response = controller.process()
        print(response)
