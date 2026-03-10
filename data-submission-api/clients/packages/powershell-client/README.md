# WaterlyConnect PowerShell Client

## Required Values

You will need 3 specific values provided by the Waterly team to proceed:

- `url`: The endpoint URL to submit data to
- `clientToken`: The client "secret" for the API client
- `clientDevice`: A device object with `id` and `type` fields (see `New-WaterlyConnectDeviceInfo`)

---

## Prerequisites

- PowerShell 5.1+ or PowerShell 7+

---

## Usage

```powershell
Import-Module ./WaterlyConnect.psm1

$clientDevice = New-WaterlyConnectDeviceInfo -Id "my-fancy-device" -Type "SCADACo"

$client = New-WaterlyConnectApiClient `
  -Url "https://foo.bar/connect/submit" `
  -ClientToken "abcpdqxyz123" `
  -ClientDevice $clientDevice

$tagInputs = @(
  @{ Name = "TagName"; Value = 123.2 }
  @{ Name = "TagTwo"; Value = 99.1 }
)

$tags = foreach ($tag in $tagInputs) {
  New-WaterlyConnectTagDatum `
    -Name $tag.Name `
    -Value $tag.Value `
    -LastChangeTimestamp ([int][DateTimeOffset]::UtcNow.ToUnixTimeSeconds())
}

$client.SubmitData($tags)
```

---

## Looping Example

Use any data source and build tag data in a loop before submitting:

```powershell
$tags = @()
foreach ($row in $dataRows) {
  $tags += New-WaterlyConnectTagDatum `
    -Name $row.TagName `
    -Value $row.Value `
    -LastChangeTimestamp $row.TimestampSeconds
}

$client.SubmitData($tags)
```

---

## API

### `New-WaterlyConnectApiClient`

Creates an API client instance.

| Parameter      | Required | Description |
|----------------|----------|-------------|
| `Url`          | `true`   | The endpoint URL for the WaterlyConnect service. A typical value would end in `/connect/submit`. |
| `ClientToken`  | `true`   | The unique client secret provided by the Waterly team. |
| `ClientDevice` | `true`   | See `New-WaterlyConnectDeviceInfo`. |
| `Proxy`        | `false`  | Optional proxy URL for `Invoke-RestMethod`. |

### `New-WaterlyConnectDeviceInfo`

Builds the device info payload (`id` and `type` are required).

### `New-WaterlyConnectTagDatum`

Builds a tag datum payload (`name`, `value`, and `last_change_timestamp` are required).
Numeric values are formatted using invariant culture so decimal separators are always `.`.

### `WaterlyConnectApiClient.SubmitData(tags)`

Submits an array of tag data to WaterlyConnect. This method throws if the submission fails.
