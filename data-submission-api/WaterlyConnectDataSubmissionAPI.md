# WaterlyConnect API

WaterlyConnect provides 3rd party hardware devices and systems to submit data to be used within the Waterly system.

## Overview

WaterlyConnect is exposed as a REST-based API. The full details are available in the [published OpenAPI documentation](https://waterlyapp.github.io/waterlyconnect-docs/data-submission-api/) for the API.

Companion client libraries and integration examples are available in the [WaterlyConnect integrations index](https://waterlyapp.github.io/waterlyconnect-docs/data-submission-api/clients/).

A few key values will need to be supplied by the Waterly support team, including:

- The value for the `x-waterly-connect-token` request header
- The assigned device id for the device block
- The device type for the device block
