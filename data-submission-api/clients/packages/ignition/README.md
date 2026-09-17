# Waterly ⟷ Ignition Integration

This folder contains a ready-to-import Ignition project (`ignition_to_waterly.zip`) that posts selected tag values from your Ignition Gateway to Waterly on a schedule. It includes:

* A Python script module (`waterly`) with a helper function `sendDataToWaterly(tags, send_now_time_all=False)`
* Instructions and sample code to enable the function in Gateway Scheduled Events
* Optional execution timestamps for periodic/calculated tags, with existing source timestamps preserved by default

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

---

## 1) Import the Ignition Project

### Option A — Import from the Gateway Webpage (recommended)

1. Open the **Gateway Webpage** > **Config** tab > **System ▸ Projects**.
2. Click **Import project…**, select `ignition_to_waterly.zip`, and follow the prompts.

> Tip: You can verify and monitor scripts later under **Status ▸ Gateway Scripts** (shows execution status, last run, errors).

### Option B — Import from Designer (alternate)

You can also restore a project backup via **Designer ▸ File ▸ Import**, depending on export format/version.

---

## 2) Configure Waterly Credentials

**Do not commit secrets to source control.** 

### Edit the script constants (quick start)

In Designer, open **Project Browser ▸ Scripting ▸ Script Library ▸ waterly** and update the placeholders at the top of `waterly.py`:

```python
# --- Waterly configuration (replace with real values) ---
waterly_api_url = "https://connect.waterly.com/api/data-submission/v1/submit"
waterly_device_id = "<WATERLY_DEVICE_ID>"  # provided by Waterly
waterly_device_token = "<WATERLY_DEVICE_TOKEN>" #provided by Waterly
# --------------------------------------------------------
```

Save the project (Ctrl/Cmd+S).

For an existing installation, update the `waterly` script module from this package before using the new timestamp options. When importing, review any overwrite prompts and retain your configured credentials and Gateway Event scripts. Existing calls that only pass tag paths continue to work.


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
* Logs success/failure via a project logger; any exceptions surface in **Gateway Scripts** status and gateway logs.

> In gateway scope, `print` output goes to the gateway log files; using a logger (`system.util.getLogger`) is recommended for structured logs you can filter on the gateway. You can review gateway status/logging under **Status** on the Gateway Webpage.

---

## Testing & Troubleshooting

* **Validate tag paths:** Test reads in the **Designer Script Console** with `system.tag.readBlocking([...])` to confirm values. (Note: the console runs in Designer scope; for gateway-only behavior, rely on the Gateway Scripts status page/logs.)
* **Check status:** Gateway Webpage → **Status ▸ Gateway Scripts** shows whether your Scheduled/Timer scripts are running, last run, and errors.
* **Project saves:** If a script doesn’t appear to run, make sure you saved the project after adding/enabling the event.
* **Repeated daily values have an older date:** For periodic/calculated aggregates, set `send_now_time=True` on those entries and confirm the schedule runs after their calculation finishes.
* **Unexpected execution timestamps:** Check whether `send_now_time_all=True` is set; it overrides per-tag `False` settings for that invocation. Omit it or set it to `False` to honor individual settings.
* **Unexpected keyword argument:** Update the imported `waterly` module before calling it with `send_now_time_all`.

### Local regression tests (for maintainers)

From the repository root, run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s data-submission-api/clients/packages/ignition/tests -v
```

The tests use Python 3's standard library and mocked Ignition APIs; they do not read live tags or send HTTP requests. They cover default timestamps, per-tag/global precedence, identical timestamps within a batch, repeated observations, unchanged full paths, quality filtering, and ZIP/source consistency. The deployed script remains compatible with [Ignition's Jython scripting environment](https://docs.inductiveautomation.com/docs/8.1/platform/scripting/scripting-in-ignition). A Gateway import and scheduled execution should also be checked in an Ignition test environment before rollout.

When changing the script, rebuild `ignition_to_waterly.zip` from the contents of `ignition_to_waterly/`, with `project.json` at the ZIP root. Keep the downloadable project and source files identical, and exclude local configuration and Python cache files.


---

## Security Notes

* Treat your **API token** like a password. If you store it in tags, put it in a dedicated provider and lock down edit permissions.
* If you clone this project, **do not** commit secrets to Git.
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

* **v1.1.0** – Added optional per-tag `send_now_time` and per-invocation `send_now_time_all`, sharing one execution timestamp per submission while preserving existing full-path inputs and source timestamps by default.
* **v1.0.0** – Initial Ignition project export and README.
