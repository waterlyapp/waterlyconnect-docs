function New-WaterlyConnectDeviceInfo {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)]
    [string]$Id,

    [Parameter(Mandatory)]
    [string]$Type,

    [string]$LanIp,
    [string]$WanIp,
    [string]$Serial,
    [long]$UptimeMillis
  )

  $device = [ordered]@{
    id = $Id
    type = $Type
  }

  if ($PSBoundParameters.ContainsKey("LanIp")) {
    $device.lan_ip = $LanIp
  }

  if ($PSBoundParameters.ContainsKey("WanIp")) {
    $device.wan_ip = $WanIp
  }

  if ($PSBoundParameters.ContainsKey("Serial")) {
    $device.serial = $Serial
  }

  if ($PSBoundParameters.ContainsKey("UptimeMillis")) {
    $device.uptime_millis = $UptimeMillis
  }

  return [pscustomobject]$device
}

function New-WaterlyConnectTagDatum {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)]
    [string]$Name,

    [Parameter(Mandatory)]
    [AllowNull()]
    [object]$Value,

    [Parameter(Mandatory)]
    [long]$LastChangeTimestamp,

    [int]$Type,
    [string]$Unit
  )

  $valueString = ""
  if ($null -ne $Value) {
    if (($Value -is [System.IFormattable]) -and -not ($Value -is [string])) {
      $valueString = $Value.ToString($null, [System.Globalization.CultureInfo]::InvariantCulture)
    } else {
      $valueString = [string]$Value
    }
  }

  $tag = [ordered]@{
    name = $Name
    value = $valueString
    last_change_timestamp = [long]$LastChangeTimestamp
  }

  if ($PSBoundParameters.ContainsKey("Type")) {
    $tag.type = $Type
  }

  if ($PSBoundParameters.ContainsKey("Unit")) {
    $tag.unit = $Unit
  }

  return [pscustomobject]$tag
}

class WaterlyConnectApiClient {
  [string]$Url
  [string]$ClientToken
  [object]$ClientDevice
  [string]$Proxy

  WaterlyConnectApiClient(
    [string]$Url,
    [string]$ClientToken,
    [object]$ClientDevice,
    [string]$Proxy
  ) {
    if ([string]::IsNullOrWhiteSpace($Url)) {
      throw "Url is required."
    }

    if ([string]::IsNullOrWhiteSpace($ClientToken)) {
      throw "ClientToken is required."
    }

    if ($null -eq $ClientDevice) {
      throw "ClientDevice is required."
    }

    $deviceId = $ClientDevice.id
    $deviceType = $ClientDevice.type

    if ([string]::IsNullOrWhiteSpace($deviceId) -or [string]::IsNullOrWhiteSpace($deviceType)) {
      throw "ClientDevice requires id and type."
    }

    $this.Url = $Url
    $this.ClientToken = $ClientToken
    $this.ClientDevice = $ClientDevice
    $this.Proxy = $Proxy
  }

  [void] SubmitData([object[]]$Tags) {
    if ($null -eq $Tags -or $Tags.Count -eq 0) {
      throw "Tags array is required."
    }

    $submission = @{
      tags = @($Tags)
      device = $this.ClientDevice
      timestamp = [int][DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    }

    $headers = @{
      "x-waterly-connect-token" = $this.ClientToken
      "x-waterly-request-type" = "WaterlyConnect"
    }

    $invokeParams = @{
      Method = "Post"
      Uri = $this.Url
      Headers = $headers
      Body = ($submission | ConvertTo-Json -Depth 10)
      ContentType = "application/json"
    }

    if (-not [string]::IsNullOrWhiteSpace($this.Proxy)) {
      $invokeParams.Proxy = $this.Proxy
    }

    try {
      Invoke-RestMethod @invokeParams | Out-Null
    } catch {
      $statusCode = $null
      $statusDescription = $null
      $responseBody = $null

      if ($_.Exception -and $_.Exception.Response) {
        $response = $_.Exception.Response
        if ($response -is [System.Net.Http.HttpResponseMessage]) {
          $statusCode = [int]$response.StatusCode
          $statusDescription = $response.ReasonPhrase
          try {
            $responseBody = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
          } catch {
            $responseBody = $null
          }
        } elseif ($response -is [System.Net.WebResponse]) {
          $statusCode = [int]$response.StatusCode
          $statusDescription = $response.StatusDescription
          try {
            $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            $reader.Close()
          } catch {
            $responseBody = $null
          }
        }
      }

      $detail = if ($statusCode) {
        if ([string]::IsNullOrWhiteSpace($responseBody)) {
          "HTTP $statusCode $statusDescription"
        } else {
          "HTTP $statusCode $statusDescription: $responseBody"
        }
      } else {
        $_.Exception.Message
      }

      throw "WaterlyConnect submission failed: $detail"
    }
  }
}

function New-WaterlyConnectApiClient {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)]
    [string]$Url,

    [Parameter(Mandatory)]
    [string]$ClientToken,

    [Parameter(Mandatory)]
    [object]$ClientDevice,

    [string]$Proxy
  )

  return [WaterlyConnectApiClient]::new($Url, $ClientToken, $ClientDevice, $Proxy)
}

Export-ModuleMember -Function New-WaterlyConnectApiClient, New-WaterlyConnectDeviceInfo, New-WaterlyConnectTagDatum
