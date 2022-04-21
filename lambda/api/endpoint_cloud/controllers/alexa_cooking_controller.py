# Copyright 2021 Amazon.com.
# SPDX-License-Identifier: MIT

from .base_controller import BaseController


class AlexaCookingController(BaseController):
    def process(self):
        if self.name == "SetCookingMode":
            return self.alexa_response
