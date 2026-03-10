# WaterlyConnect NodeJS Client

## Required Values

You will need 3 specific values provided by the Waterly team to proceed:

- `url`: The endpoint URL to submit data to
- `clientToken`: The client "secret" for the API client
- `clientDeviceId`: A unique identifier for the API client

---

## Installation

```
yarn add @waterclick/waterlyconnect-nodejs-client
```

---

## Usage

```typescript
import {
  TagDatum,
  WaterlyConnectApiClient,
  WaterlyConnectApiClientConfig
} from "@waterclick/waterlyconnect-nodejs-client";

const config: WaterlyConnectApiClientConfig = {
  url: "https://foo.bar/connect/submit",
  clientToken: "abcpdqxyz123",
  clientDevice: {
    id: "my-fancy-device",
    type: "SCADACo",
  },
};

const c = new WaterlyConnectApiClient(config);

const data: TagDatum[] = [
  // Note that timestamps must be in *seconds* since the epoch, not milliseconds
  { name: "TagName", value: "123.2", last_change_timestamp: Math.floor(new Date().getTime() / 1000) },
];

c.submitData(data)
  .then(() => console.log("Success!"))
  .catch((err) => console.error("Failed to submit data", err));

```

---

## API

### WaterlyConnectApiClient

#### `constructor`

The `WaterlyConnectApiClient` constructor requires one argument: an object of `WaterlyConnectApiClientConfig`. Please see the type
documentation below for specifics of how it may be configured.

#### `submitData`

`submitData` is an async method with a `Promise<void>` return value. You must resolve calls to function with either `then()/catch()`
syntax or `async/await`.

This function will **throw an error** that you must catch in your code if data was unable to be accepted by the
WaterlyConnect service for any reason, or will complete silently when successful.

---

## Types

### WaterlyConnectApiClientConfig

`WaterlyConnectApiClientConfig` is used to configure the api client.

| Property       | Required | Description                                                                                                                                                                                               |
|----------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `url`          | `true`   | The endpoint URL for the WaterlyConnect service, provided by the Waterly team. A typical value would end in `/connect/submit` like: https://host.name/connect/submit                                      | 
| `clientToken`  | `true`   | The unique client secret WaterlyConnect service, provided by the Waterly team. It is usually a 32 character string. Please use secure transmission and storage methods to manage this value.              |
| `clientDevice` | `true`   | See the section describing `ClientDeviceInfo` for more information                                                                                                                                        |
| `proxy`        | `false`  | If your API client is behind a firewall, it may be configured here.  This object is an Axios Proxy configuration object.  You may find more details on it [here](https://axios-http.com/docs/req_config). |

### ClientDeviceInfo

`ClientDeviceInfo` is used to describe the API client to the Waterly Connect service.

| Property        | Required | Description                                                                                                                                                                                   |
|-----------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`            | `true`   | An identifier for the API client, assigned by the Waterly team.                                                                                                                               |
| `type`          | `true`   | A simple string describing the type of system connecting to Waterly Connect.  For instance, it may be a device type (e..g, `Ewon Flexy`) or a system name. You are free to choose this value. |
| `lan_ip`        | `false`  | (Optional) The internal IP address of the client device or system                                                                                                                             |
| `wan_ip`        | `false`  | (Optional) The external IP address of the client device or system                                                                                                                             |
| `serial`        | `false`  | (Optional) A serial number for the client device or system                                                                                                                                    |
| `uptime_millis` | `false`  | (Optional) A number representing the epoch time, represented in milliseconds that they client device or system has been "up" (or since last boot).                                            | 

### TagDatum

`TagDatum` represents the actual tagged data to be submitted to WaterlyConnect

| Property                | Required | Description                                                                                                                                                |
|-------------------------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                  | `true`   | The client-assigned tag name for the value.  It may be any string, but must be unique within the submission.                                               |
| `value`                 | `true`   | The actual data value being measured.  While WaterlyConnect only accepts numeric values, this value **must** be encoded a string.  For instance: `"123.2"` |
| `last_change_timestamp` | `true`   | The timestamp that the value was recorded, measured in **seconds** since the epoch.                                                                        |
| `type`                  | `false`  | (Optional)(Legacy) A historical value used to track the type of data being submitted.                                                                      |
| `unit`                  | `false`  | (Optional)(Legacy) Typically unused, this value was used to track the unit type of the submitted data.                                                     |
