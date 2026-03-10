# WaterlyConnect Python Client

## Required Values

You will need 3 specific values provided by the Waterly team to proceed:

- `url`: The endpoint URL to submit data to
- `client_token`: The client "secret" for the API client
- `client_device`: A device object with `id` and `type` fields (see `ClientDeviceInfo`)

---

## Prerequisites

- Python 3.12+

### Supported Python Versions

The client is implemented using the Python standard library and is supported on
Python 3.12+.

---

## Installation

This module has no external dependencies. Copy `waterlyconnect_client.py` into your project, or add
`packages/python-client` to your `PYTHONPATH` and import it directly.

---

## Usage

```python
import time

from waterlyconnect_client import (
    ClientDeviceInfo,
    TagDatum,
    WaterlyConnectApiClient,
    WaterlyConnectApiClientConfig,
)

config = WaterlyConnectApiClientConfig(
    url="https://foo.bar/connect/submit",
    client_token="abcpdqxyz123",
    client_device=ClientDeviceInfo(
        id="my-fancy-device",
        type="SCADACo",
    ),
)

client = WaterlyConnectApiClient(config)

tags = [
    # Note that timestamps must be in *seconds* since the epoch, not milliseconds
    TagDatum(
        name="TagName",
        value=123.2,
        last_change_timestamp=int(time.time()),
    )
]

client.submit_data(tags)
```

---

## Looping Example

Use any data source and build tag data in a loop before submitting:

```python
import time

rows = [
    {"name": "TagName", "value": 123.2},
    {"name": "TagTwo", "value": 99.1},
]

tags = []
for row in rows:
    tags.append(
        TagDatum(
            name=row["name"],
            value=row["value"],
            last_change_timestamp=int(time.time()),
        )
    )

client.submit_data(tags)
```

---

## API

### `WaterlyConnectApiClientConfig`

`WaterlyConnectApiClientConfig` is used to configure the API client.

| Property        | Required | Description |
|-----------------|----------|-------------|
| `url`           | `true`   | The endpoint URL for the WaterlyConnect service, provided by the Waterly team. A typical value would end in `/connect/submit`. |
| `client_token`  | `true`   | The unique client secret WaterlyConnect service, provided by the Waterly team. It is usually a 32 character string. Please use secure transmission and storage methods to manage this value. |
| `client_device` | `true`   | See the section describing `ClientDeviceInfo` for more information. |
| `proxy`         | `false`  | If your API client is behind a firewall, it may be configured here. Use a proxy URL string or a dictionary of scheme-to-proxy values. |

### `ClientDeviceInfo`

`ClientDeviceInfo` is used to describe the API client to the WaterlyConnect service.

| Property        | Required | Description |
|-----------------|----------|-------------|
| `id`            | `true`   | An identifier for the API client, assigned by the Waterly team. |
| `type`          | `true`   | A simple string describing the type of system connecting to Waterly Connect. For instance, it may be a device type (e.g., `Ewon Flexy`) or a system name. You are free to choose this value. |
| `lan_ip`        | `false`  | (Optional) The internal IP address of the client device or system. |
| `wan_ip`        | `false`  | (Optional) The external IP address of the client device or system. |
| `serial`        | `false`  | (Optional) A serial number for the client device or system. |
| `uptime_millis` | `false`  | (Optional) A number representing the epoch time, represented in milliseconds that the client device or system has been "up" (or since last boot). |

### `TagDatum`

`TagDatum` represents the actual tagged data to be submitted to WaterlyConnect.

| Property                | Required | Description |
|-------------------------|----------|-------------|
| `name`                  | `true`   | The client-assigned tag name for the value. It may be any string, but must be unique within the submission. |
| `value`                 | `true`   | The actual data value being measured. While WaterlyConnect only accepts numeric values, this value is encoded as a string in the payload. |
| `last_change_timestamp` | `true`   | The timestamp that the value was recorded, measured in **seconds** since the epoch. |
| `type`                  | `false`  | (Optional)(Legacy) A historical value used to track the type of data being submitted. |
| `unit`                  | `false`  | (Optional)(Legacy) Typically unused, this value was used to track the unit type of the submitted data. |

### `WaterlyConnectApiClient.submit_data(tags)`

Submits an array of tag data to WaterlyConnect. This method raises a `WaterlyConnectError` if the submission fails.

You may pass either `TagDatum` instances or dictionaries containing the same keys as `TagDatum`.
