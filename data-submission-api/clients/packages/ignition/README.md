# Waterly ⟷ Ignition Integration

This folder contains a ready-to-import Ignition project (`ignition_to_waterly.zip`) that posts selected tag values from your Ignition Gateway to Waterly on a schedule. It includes:

* A Python script module (`waterly`) with a helper function `sendDataToWaterly(tags, send_now_time_all=False)`
* Instructions and sample code to enable the function in Gateway Scheduled Events
* Optional execution timestamps for periodic/calculated tags, with existing source timestamps preserved by default
* Authentication from the Gateway's `WATERLY_DEVICE_TOKEN` environment variable, with no token stored in the project

> If you’re new to Ignition: it’s an industrial platform used to build and run SCADA/IIoT/MES applications with unlimited tags/clients, built on open tech like Python, OPC UA, and MQTT. Learn more on Inductive Automation’s [site](https://inductiveautomation.com/ignition/).

---

## Contents

```
data-submission-api/clients/packages/ignition/
├─ README.md                ← this file
├─ ignition_to_waterly.zip  ← Ignition project export to import
├─ ignition_to_waterly/     ← Directory containing viewable contents of zip
└─ tests/                  ← Local regression tests using mocked Gateway APIs
```

---

## Prerequisites

* Ignition 8.1+ Gateway with Designer access
* An Ignition tag provider with tags you want to post
* Waterly-provided endpoint URL, Device ID, API token, and device type. This project uses device type `Ignition`; confirm that with Waterly when requesting your configuration from **[support@waterly.com](mailto:support@waterly.com)**.
* Administrator access to the Gateway server to configure its environment and restart the Ignition service. Windows is the standard installation path below; Linux and container instructions follow.

---

## 1) Import the Ignition Project

### Option A — Import from the Gateway Webpage (recommended)

1. Open the **Gateway Webpage** > **Config** tab > **System ▸ Projects**.
2. Click **Import project…**, select `ignition_to_waterly.zip`, and follow the prompts.

> Tip: You can verify and monitor scripts later under **Status ▸ Gateway Scripts** (shows execution status, last run, errors).

### Option B — Import from Designer (alternate)

You can also restore a project backup via **Designer ▸ File ▸ Import**, depending on export format/version.

---

## 2) Configure Waterly

Configure the endpoint and device ID in the project, and provision the API token on the **server running the Ignition Gateway**. Setting a variable on an integrator's Designer workstation does not configure the Gateway.

### Set the endpoint and device ID in Designer

In Designer, open **Project Browser ▸ Scripting ▸ Script Library ▸ waterly** and update the configuration at the top of the module:

```python
# --- Non-secret Waterly configuration ---
waterly_api_url = "https://connect.waterly.com/api/data-submission/v1/submit"
waterly_device_id = "<WATERLY_DEVICE_ID>"  # provided by Waterly
```

Use the endpoint supplied by Waterly, including `/submit`. The device type remains `Ignition` in the request body. Save the project with **Ctrl+S**. Do not add a token constant to the module or move the device ID into an environment variable.

### Windows Gateway server — standard installation

1. Sign in to the **Gateway server** with administrator access. Plan the service restart with the site operator, since it interrupts the Gateway's other work too.
2. Search Windows for **Edit the system environment variables**. Open **System Properties ▸ Advanced ▸ Environment Variables**.
3. Under **System variables**, select **New** (or **Edit** if the variable already exists). Use the exact name `WATERLY_DEVICE_TOKEN` and paste the Waterly-provided token as the value, without added quotes or spaces. Save all dialogs. Do not use the **User variables** section.
4. Open **Services** (`services.msc`), find the Ignition Gateway service installed for this Gateway, and **Restart** it. The service name can be customized during installation. Restart the Windows service, not just Designer or the project.
5. After the Gateway returns, run the Gateway Timer/Scheduled event described below. Confirm `Successful Post to WaterlyConnect` in the `WaterlyConnect` logger and verify the submission in Waterly.

Windows environment variables are [inherited by processes](https://learn.microsoft.com/en-us/windows/win32/procthread/environment-variables). A variable set only in a Command Prompt or PowerShell session does not configure the service. Ignition's [Java Service Wrapper reads system variables when the Windows service starts](https://wrapper.tanukisoftware.com/doc/english/props-envvars.html). If the Gateway still reports a missing variable after a full service restart, have the server administrator verify the system variable and service configuration; arrange a server reboot if its service launcher retains the old environment.

### Linux Gateway server — systemd installations

Have the server administrator configure the environment of the actual Ignition service. For example:

1. Create `/etc/ignition-waterly/gateway.env` outside the project and repository, owned by root with file permissions `600` and parent-directory permissions `700`. Enter this line in an editor, replacing the fictional value with the Waterly token:

   ```text
   WATERLY_DEVICE_TOKEN=REPLACE_WITH_WATERLY_PROVIDED_TOKEN
   ```

2. Find the installed service name with `systemctl list-unit-files '*[Ii]gnition*'`. If it is `Ignition-Gateway.service`, run `sudo systemctl edit Ignition-Gateway.service` and add:

   ```ini
   [Service]
   EnvironmentFile=/etc/ignition-waterly/gateway.env
   ```

3. Reload the service definition and restart the Gateway, substituting the installed service name if different:

   ```sh
   sudo systemctl daemon-reload
   sudo systemctl restart Ignition-Gateway.service
   ```

4. Verify a Gateway event and the resulting Waterly submission as described for Windows.

This uses systemd's [service environment settings](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=). A shell `export` or user profile alone does not configure a system service. For a non-systemd installation, have the administrator set the variable in that service's startup environment and restart the entire service.

### Containerized Gateway

Pass `WATERLY_DEVICE_TOKEN` into the **Gateway container** at creation time. For an existing Docker Compose deployment, add an `env_file` entry to its Gateway service (named `gateway` in this example), preserving its current image, ports, and persistent data volume:

```yaml
services:
  gateway:
    env_file:
      - /secure/ignition/waterly.env
```

Create the referenced file on the deployment host with access limited to the deployment administrator. Its contents use the same `WATERLY_DEVICE_TOKEN=REPLACE_WITH_WATERLY_PROVIDED_TOKEN` format shown above; replace the fictional value locally. Keep the file outside the project and source control. This is an addition to an existing deployment, not a complete Compose file.

Recreate the Gateway container after initially adding or changing the token:

```sh
docker compose up -d --force-recreate --no-deps gateway
```

Compose's [env_file setting](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/) passes the value into the container. A host `.env` file alone does not do this. A plain [`docker compose restart`](https://docs.docker.com/reference/cli/docker/compose/restart/) does not apply changed environment settings. Retain the Gateway's persistent data volume when recreating it, then verify a submission.

### Existing installations, token rotation, and redundancy

This update **changes how the token is configured**. Provision `WATERLY_DEVICE_TOKEN` on the Gateway host, then replace the existing `waterly` module with this version and restart the Gateway service. Remove the old token assignment instead of copying it into the new module. Preserve your endpoint, device ID, tag configuration, and Gateway Event scripts when reviewing import/overwrite prompts. Existing function calls and timestamp options continue to work.

If updating by copy/paste, replace the **complete module**, including its imports, from [code.py](ignition_to_waterly/ignition/script-python/waterly/code.py), then restore only your non-secret endpoint and device ID. Copying only the function omits this required import:

```python
from java.lang import Exception as JavaException, System
```

The module reads `System.getenv("WATERLY_DEVICE_TOKEN")` from the Gateway JVM's startup environment. It does not create, modify, persist, or dynamically reload environment variables. There are no alternate variable names or hard-coded fallbacks. A missing, empty, or whitespace-only value produces a configuration error and stops that invocation before any tag read or HTTP request.

To rotate the token:

1. Update `WATERLY_DEVICE_TOKEN` on the Gateway host or in its container deployment environment.
2. Restart the entire Gateway service, or recreate its container with the updated environment.
3. Verify that Gateway submissions succeed in Waterly.

For **redundant Gateways**, provision the correct token independently on **each node** and coordinate restarts with the site operator. Project synchronization, Gateway backup/restore, and redundancy do not replicate this operating-system environment variable. Verify the integration on each node when it is active.

Only the environment-variable approach is supported by this integration. Do not put the token in tags, `ignition.conf`, Java `-D` properties, or project scripts.

---

## 3) Configure the Gateway Schedule Script

You can run the post on a **Scheduled** event (specific times) or a **Timer** event (fixed rate). Configure in Designer:

1. Open **Designer** > **Project Browser ▸ Scripting ▸ Gateway Events**.
2. Choose **Scheduled** (or **Timer**) and click **+** to add a new script.
3. Give it a name, configure timing, paste the example code below, **Enable** it, and **Save** the project.

### A) Gateway **Scheduled** Script (runs at specific times)

> Available in Ignition 8.1.6+. Use when you want “run at 00:00 and 12:00,” etc.

**Script Tab →** paste:

```python
def onScheduledEvent():
    # Select the tags you want to send
    tags = [
        "[Sample_Tags]Realistic/Realistic0",
        "[Sample_Tags]Realistic/Realistic2",
    ]
    # Call into the helper that posts to Waterly
    waterly.sendDataToWaterly(tags)
```

### B) Gateway **Timer** Script (runs every N ms)

> Use when you want a heartbeat like “every 60 seconds.” Configure **Delay** and **Delay Type** (Fixed Delay/Fixed Rate).

**Script Tab →** paste:

```python
tags = [
    "[Sample_Tags]Realistic/Realistic0",
    "[Sample_Tags]Realistic/Realistic2",
]
waterly.sendDataToWaterly(tags)
```

**Remember to Save the project** so the gateway picks up the changes. You can see last execution and errors under **Gateway Webpage ▸ Status ▸ Gateway Scripts**.

---

## 4) Choose Timestamps for Periodic or Calculated Values

By default, each tag's `last_change_timestamp` comes from its Ignition `QualifiedValue.timestamp`, converted from milliseconds to whole Unix seconds. Existing lists of full tag-path strings work without changes.

Use `send_now_time=True` primarily for periodic/calculated aggregate values such as daily runtime, daily starts, daily flow totals, or chemical usage. A value may be identical on consecutive reporting days (for example, 8.5 hours on both days), while Ignition retains the earlier source timestamp. Sending the execution timestamp lets Waterly receive the later observation with the time of the new submission.

### Select individual tags

Entries can be full-path strings or dictionaries with `tag_name` and optional `send_now_time`. These forms can be mixed in the same list:

```python
tags = [
    "[default]Process/TankLevel",  # Keep the Ignition source timestamp
    {"tag_name": "[default]DailyTotals/DailyRuntime", "send_now_time": True},
    {"tag_name": "[default]DailyTotals/DailyStarts", "send_now_time": True},
    {"tag_name": "[default]Process/Pressure"},  # Also keeps the source timestamp
]
waterly.sendDataToWaterly(tags)
```

Paste this into your Timer event, or inside the `onScheduledEvent()` function shown above. Replace the fictional paths with your full Ignition paths. A dictionary entry without `send_now_time` behaves the same as `send_now_time=False`.

`tag_name` is always the full Ignition path, including the provider and folders. The helper uses that exact string to read the tag and sends it unchanged in the existing Waterly payload's `name` field. No separate path, alias, or display name is configured.

### Use execution time for every tag in an invocation

```python
tags = [
    "[default]DailyTotals/DailyFlowTotal",
    {"tag_name": "[default]DailyTotals/DailyRuntime", "send_now_time": False},
]
waterly.sendDataToWaterly(tags, send_now_time_all=True)
```

| Global `send_now_time_all` | Per-tag `send_now_time` | Timestamp sent |
| --- | --- | --- |
| `False` (default) | Omitted or `False` | Ignition source timestamp |
| `False` (default) | `True` | Current execution timestamp |
| `True` | Any setting | Current execution timestamp |

The helper captures `now = int(time.time())` **once per invocation**, after reading the tags and before processing their values. It reuses that same whole-second timestamp for the payload's `timestamp` and every tag using execution time. A later invocation captures a new `now`.

The connector also appends `[System]Gateway/CurrentDateTime`, `[System]Gateway/Timezone`, and `[System]Gateway/UptimeSeconds`. These keep their source timestamps by default; `send_now_time_all=True` applies to them too. Only tags with good quality are submitted, regardless of timestamp mode.

Schedule aggregate submissions after the reporting values have been calculated, at the time intended to represent the observation. Execution time is the time the helper runs; it does not backdate a reading to a previous reporting period. For live process values where the last change time matters, keep the default source timestamp.

---

## General Description of `sendDataToWaterly(tags, send_now_time_all=False)`

* Resolves the provided tag paths and reads current values (blocking read).
* Builds a payload with unchanged full tag paths, string-encoded values, selected timestamps in whole Unix seconds, and your device configuration.
* Sends a JSON HTTP POST to Waterly’s endpoint using your configured base URL and API token.
* Reads the token from the Gateway JVM environment and sends it in the existing `x-waterly-connect-token` header.
* Logs fixed success/failure messages using the `WaterlyConnect` logger. Response bodies, request headers, and exception details are omitted so an echoed token cannot enter these logs. Configuration and HTTP failures are logged and return without raising; a completed Gateway event alone does not prove a successful submission.

> In gateway scope, `print` output goes to the gateway log files; using a logger (`system.util.getLogger`) is recommended for structured logs you can filter on the gateway. You can review gateway status/logging under **Status** on the Gateway Webpage.

---

## Testing & Troubleshooting

* **`WATERLY_DEVICE_TOKEN environment variable is not set or is blank`:** Set a nonblank value on the Gateway server and restart its service. On Windows, use **System variables**; on containers, recreate with the updated environment. The connector sends no request while this error persists.
* **`cannot read WATERLY_DEVICE_TOKEN from the Gateway environment`:** Have the Gateway administrator check whether the runtime permits Java environment access. No request is sent. Do not work around the error by restoring a script token.
* **`NameError` for `System` or `JavaException` under `TimerScriptTask`:** The installed script may be missing the new Java import. Replace the complete `waterly` module as described under existing installations, preserve your endpoint/device ID, and save the project. This is an incomplete script update, not the intended missing-token error. The intended error appears under the `WaterlyConnect` logger.
* **`Error posting to WaterlyConnect`:** Check the supplied endpoint, device ID, token, outbound network access, and TLS trust. Detailed HTTP responses and exceptions are intentionally not logged. Share the time of the failure and non-secret device configuration with Waterly support; never send the token or complete request headers.
* **Validate tag paths:** Test reads in the **Designer Script Console** with `system.tag.readBlocking([...])` to confirm values. (Note: the console runs in Designer scope; for gateway-only behavior, rely on the Gateway Scripts status page/logs.)
* **Check status:** Gateway Webpage → **Status ▸ Gateway Scripts** shows whether your Scheduled/Timer scripts are running. Also check the `WaterlyConnect` logger and Waterly's received submissions; configuration/HTTP failures can leave the event itself marked as completed.
* **Project saves:** If a script doesn’t appear to run, make sure you saved the project after adding/enabling the event.
* **Repeated daily values have an older date:** For periodic/calculated aggregates, set `send_now_time=True` on those entries and confirm the schedule runs after their calculation finishes.
* **Unexpected execution timestamps:** Check whether `send_now_time_all=True` is set; it overrides per-tag `False` settings for that invocation. Omit it or set it to `False` to honor individual settings.
* **Unexpected keyword argument:** Update the imported `waterly` module before calling it with `send_now_time_all`.

### Local regression tests (for maintainers)

From the repository root with Python 3 installed, run:

```text
python -B -m unittest discover -s data-submission-api/clients/packages/ignition/tests -v
```

Use `py -3` or `python3` in place of `python` if that is how Python 3 is installed. The tests use Python's standard library and mocked Ignition/Java APIs; they do not read live tags, send HTTP requests, or verify Windows service environment inheritance. They cover token retrieval, missing/blank values, environment access failures, token-safe success/error logging, unchanged requests, timestamp modes, quality filtering, and ZIP/source consistency. The deployed script remains compatible with [Ignition's Jython scripting environment](https://docs.inductiveautomation.com/docs/8.1/platform/scripting/scripting-in-ignition).

Before rollout, import the ZIP into an Ignition test Gateway and execute a Gateway Timer/Scheduled event. Verify a successful submission with a test device, rejection without a configured token, and recovery after provisioning/restarting. Check that token rotation takes effect after restarting and that neither logs nor a fresh project export contain the token. Use a test Gateway and a local HTTP receiver with a fictional token to exercise empty/whitespace values and responses that echo credentials without sending those tests to Waterly. Repeat the service-provisioning check on Windows for the target installation. The Designer Script Console runs outside the Gateway process and cannot establish Gateway environment inheritance.

When changing the script, rebuild `ignition_to_waterly.zip` from the contents of `ignition_to_waterly/`, with `project.json` at the ZIP root. Keep the downloadable project and source files identical, and exclude local configuration and Python cache files.


---

## Security Notes

* Treat your **API token** like a password. Keep it in the Gateway's deployment environment and restrict access to that host and its environment configuration. Environment variables are not encrypted secret storage; authorized host/container administrators can inspect them.
* Do not print the token, dump the process environment, or log complete request headers. Do not include token values in screenshots or support material.
* If you clone this project, **do not** commit secrets or deployment environment files to Git. Removing a token from the current script does not erase it from earlier exports, backups, or source history; rotate credentials that were exposed.
* Consider network allow-lists / firewall rules so the gateway can reach Waterly’s API.

---

## About Ignition & Waterly

Ignition is a universal industrial application platform used for SCADA/IIoT/MES with a server-centric, web-deployed architecture and unlimited licensing.

Waterly is actively collaborating with the Ignition ecosystem to make secure, reliable data exchange from plant-floor tags to Waterly analytics and reporting simple and robust. If you’re an integrator or end user interested in deeper integration patterns (Perspective, tag change triggers, batching), we’d love to chat.

---

## Need Help?

* Credentials or endpoint questions: **[support@waterly.com](mailto:support@waterly.com)**
* Ignition scripting & events:

    * **Gateway Event Scripts** (overview & location in Designer)
    * **Project Import/Export** (Gateway)
    * **Timer & Scheduled scripts** (how they run, config)
  

---

### Changelog

* **v2.0.0** – Breaking configuration change: requires `WATERLY_DEVICE_TOKEN` in the Gateway runtime environment, removes the project token constant, rejects missing/blank tokens, and prevents response/exception details from exposing credentials in connector logs. Endpoint, device ID, tag payloads, and timestamp options are unchanged.
* **v1.1.0** – Added optional per-tag `send_now_time` and per-invocation `send_now_time_all`, sharing one execution timestamp per submission while preserving existing full-path inputs and source timestamps by default.
* **v1.0.0** – Initial Ignition project export and README.
