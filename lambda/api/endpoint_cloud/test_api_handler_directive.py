# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

import unittest
from unittest.case import TestCase
from unittest.mock import patch, Mock, MagicMock
import json
from endpoint_cloud.controllers.base_controller import BaseController
from endpoint_cloud.api_auth import ApiAuth
from endpoint_cloud.api_handler_directive import ApiHandlerDirective
from endpoint_cloud import device



class TestReportState(unittest.TestCase):
    capabilities = [
        {"type": "AlexaInterface", "interface": "Alexa", "version": "3"},
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
        BaseController.get_capabilities = Mock(return_value=self.capabilities)
        device.device_state.get_state = Mock(return_value={"powerState": "ON"})
        request = {
            "directive": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ReportState",
                    "messageId": "123",
                    "correlationToken": "123",
                    "payloadVersion": "3",
                },
                "endpoint": {
                    "scope": {"type": "BearerToken", "token": "abcToken"},
                    "endpointId": "endpointId",
                    "cookie": {},
                },
                "payload": {},
            }
        }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )
        self.assertDictContainsSubset({
                            "namespace": "Alexa.PowerController",
                            "name": "powerState",
                            "value": "ON",
                            "uncertaintyInMilliseconds": 0,
                        }, r["context"]["properties"][0]
            
        )

class TestDiscovery(unittest.TestCase):
    def test_discovery_directory(self):
        ApiAuth.get_user_id = Mock(
            return_value=json.dumps({"user_id": {}}).encode("utf8")
        )
        request = {
            "directive": {
                "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover",
                "messageId": "324",
                "payloadVersion": "3"
                },
                "payload": {
                "scope": {
                    "type": "BearerToken",
                    "token": "atoken"
                }
                }
            }
        }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )
        #print(r)

class TestPowerController(TestCase):
    def test_power_controller_on(self):
        device.power_controller.set_state = Mock(return_value="ON")
        request = {
            "directive": {
                "header": {
                "namespace": "Alexa.PowerController",
                "name": "TurnOn",
                "messageId": "<message id>",
                "correlationToken": "<an opaque correlation token>",
                "payloadVersion": "3"
                },
                "endpoint": {
                "scope": {
                    "type": "BearerToken",
                    "token": "<an OAuth2 bearer token>"
                },
                "endpointId": "<endpoint id>",
                "cookie": {}
                },
                "payload": {}
            }
            }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )
        self.assertDictContainsSubset({'namespace': 'Alexa.PowerController', 'name': 'powerState', 'value': 'ON'}, r["context"]["properties"][0])
    
    def test_power_controller_off(self):
        device.power_controller.set_state = Mock(return_value="OFF")
        request = {
            "directive": {
                "header": {
                "namespace": "Alexa.PowerController",
                "name": "TurnOff",
                "messageId": "<message id>",
                "correlationToken": "<an opaque correlation token>",
                "payloadVersion": "3"
                },
                "endpoint": {
                "scope": {
                    "type": "BearerToken",
                    "token": "<an OAuth2 bearer token>"
                },
                "endpointId": "<endpoint id>",
                "cookie": {}
                },
                "payload": {}
            }
            }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )
        self.assertDictContainsSubset({'namespace': 'Alexa.PowerController', 'name': 'powerState', 'value': 'OFF'}, r["context"]["properties"][0])

class TestToggleController(TestCase):
    def test_toggle_on(self):
        device.toggle_controller.set_state = Mock(return_value="ON")
        request = {
            "directive": {
                "header": {
                "namespace": "Alexa.ToggleController",
                "instance": "Oven.Light",
                "name": "TurnOn",
                "messageId": "<message id>",
                "correlationToken": "<an opaque correlation token>",
                "payloadVersion": "3"
                },
                "endpoint": {
                "scope": {
                    "type": "BearerToken",
                    "token": "<an OAuth2 bearer token>"
                },
                "endpointId": "<endpoint id>",
                "cookie": {}
                },
                "payload": {}
            }
            }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )
        self.assertDictContainsSubset({
        "namespace": "Alexa.ToggleController",
        "instance": "Oven.Light",
        "name": "toggleState",
        "value": "ON"}, r["context"]["properties"][0])
    
    def test_toggle_off(self):
        device.toggle_controller.set_state = Mock(return_value="OFF")
        request = {
            "directive": {
                "header": {
                "namespace": "Alexa.ToggleController",
                "instance": "Oven.Light",
                "name": "TurnOff",
                "messageId": "<message id>",
                "correlationToken": "<an opaque correlation token>",
                "payloadVersion": "3"
                },
                "endpoint": {
                "scope": {
                    "type": "BearerToken",
                    "token": "<an OAuth2 bearer token>"
                },
                "endpointId": "<endpoint id>",
                "cookie": {}
                },
                "payload": {}
            }
            }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )
        self.assertDictContainsSubset({
        "namespace": "Alexa.ToggleController",
        "instance": "Oven.Light",
        "name": "toggleState",
        "value": "OFF"}, r["context"]["properties"][0])

class TestRangeController(TestCase):
    capabilities = [
            {
              "type": "AlexaInterface",
              "interface": "Alexa.RangeController",
              "instance": "Fan.Speed",
              "version": "3",
              "properties": {
                "supported": [
                  {
                    "name": "rangeValue"
                  }
                ],
                "proactivelyReported": True,
                "retrievable": True,
                "nonControllable": True
              },
              "capabilityResources": {
                "friendlyNames": [
                  {
                    "@type": "asset",
                    "value": {
                      "assetId": "Alexa.Setting.FanSpeed"
                    }
                  },
                  {
                    "@type": "text",
                    "value": {
                      "text": "Speed",
                      "locale": "en-US"
                    }
                  },
                  {
                    "@type": "text",
                    "value": {
                      "text": "Velocidad",
                      "locale": "es-MX"
                    }
                  },
                  {
                    "@type": "text",
                    "value": {
                      "text": "Vitesse",
                      "locale": "fr-CA"
                    }
                  }
                ]
              },
              "configuration": {
                "supportedRange": {
                  "minimumValue": 1,
                  "maximumValue": 10,
                  "precision": 1
                },
                "presets": [
                  {
                    "rangeValue": 10,
                    "presetResources": {
                      "friendlyNames": [
                        {
                          "@type": "asset",
                          "value": {
                            "assetId": "Alexa.Value.Maximum"
                          }
                        },
                        {
                          "@type": "asset",
                          "value": {
                            "assetId": "Alexa.Value.High"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Highest",
                            "locale": "en-US"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Fast",
                            "locale": "en-US"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Alta",
                            "locale": "es-MX"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Élevée",
                            "locale": "fr-CA"
                          }
                        }
                      ]
                    }
                  },
                  {
                    "rangeValue": 1,
                    "presetResources": {
                      "friendlyNames": [
                        {
                          "@type": "asset",
                          "value": {
                            "assetId": "Alexa.Value.Minimum"
                          }
                        },
                        {
                          "@type": "asset",
                          "value": {
                            "assetId": "Alexa.Value.Low"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Lowest",
                            "locale": "en-US"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Slow",
                            "locale": "en-US"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Baja",
                            "locale": "es-MX"
                          }
                        },
                        {
                          "@type": "text",
                          "value": {
                            "text": "Faible",
                            "locale": "fr-CA"
                          }
                        }
                      ]
                    }
                  }
                ]
              }
            },
            {
              "type": "AlexaInterface",
              "interface": "Alexa.PowerController",
              "version": "3",
              "properties": {
                "supported": [
                  {
                    "name": "powerState"
                  }
                ],
                "proactivelyReported": True,
                "retrievable": True
              }
            },
            {
              "type": "AlexaInterface",
              "interface": "Alexa",
              "version": "3"
            }
          ]
    def test_set_value(self):
        BaseController.get_capabilities = Mock(return_value=self.capabilities)
        device.range_controller.set_value = Mock(return_value=7)
        device.range_controller.get_value = Mock(return_value=7)
        request = {
            "directive": {
                "header": {
                "namespace": "Alexa.RangeController",
                "instance": "Fan.Speed",
                "name": "SetRangeValue",
                "messageId": "<message id>",
                "correlationToken": "<an opaque correlation token>",
                "payloadVersion": "3"
                },
                "endpoint": {
                "scope": {
                    "type": "BearerToken",
                    "token": "<an OAuth2 bearer token>"
                },
                "endpointId": "<endpoint id>",
                "cookie": {}
                },
                "payload": {
                "rangeValue": 7
                }
            }
            }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )   
        self.assertDictContainsSubset({
        "namespace": "Alexa.RangeController",
        "instance": "Fan.Speed",
        "name": "rangeValue",
        "value": 7}, r["context"]["properties"][0])

    def test__value(self):
        BaseController.get_capabilities = Mock(return_value=self.capabilities)
        device.range_controller.set_value = Mock(return_value=4)
        device.range_controller.get_value = Mock(return_value=7)
        request = {
            "directive": {
                "header": {
                "namespace": "Alexa.RangeController",
                "instance": "Fan.Speed",
                "name": "AdjustRangeValue",
                "messageId": "<message id>",
                "correlationToken": "<an opaque correlation token>",
                "payloadVersion": "3"
                },
                "endpoint": {
                "scope": {
                    "type": "BearerToken",
                    "token": "<an OAuth2 bearer token>"
                },
                "endpointId": "<endpoint id>",
                "cookie": {}
                },
                "payload": {
                "rangeValueDelta": -3,
                "rangeValueDeltaDefault": False
                }
            }
            }
        r = ApiHandlerDirective().process(
            request={"body": json.dumps(request)},
            client_id="test",
            client_secret="test",
            redirect_uri="http://redirect",
        )   
        self.assertDictContainsSubset({
        "namespace": "Alexa.RangeController",
        "instance": "Fan.Speed",
        "name": "rangeValue",
        "value": 4}, r["context"]["properties"][0])

if __name__ == "__main__":
    unittest.main()
