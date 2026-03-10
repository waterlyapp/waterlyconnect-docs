# Waterly ⟷ Ignition Integration

This folder contains a ready-to-import Ignition project (`ignition_to_waterly.zip`) that posts selected tag values from your Ignition Gateway to Waterly on a schedule. It includes:

* A Python script module (`waterly`) with a helper function `sendDataToWaterly(tags)`
* Instructions and sample code to enable the function in Gateway Scheduled Events

> If you’re new to Ignition: it’s an industrial platform used to build and run SCADA/IIoT/MES applications with unlimited tags/clients, built on open tech like Python, OPC UA, and MQTT. Learn more on Inductive Automation’s [site](https://inductiveautomation.com/ignition/).

---

## Contents

```
waterlyconnect-clients/
└─ ignition/
   ├─ README.md   ← this file
   └─ ignition_to_waterly.zip  ← Ignition project export to import
   └─ ignition_to_waterly/  ← Directory containing viewable contents of zip
```

---

## Prerequisites

* Ignition 8.1+ Gateway with Designer access
* An Ignition tag provider with tags you want to post
* Waterly credentials (Device ID, API token) — email **[support@waterly.com](mailto:support@waterly.com)** to request them.

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
waterly_api_url = "https://app.dev.waterlyapp.com/connect/submit"
waterly_device_id = "<WATERLY_DEVICE_ID>"  # provided by Waterly
waterly_device_token = "<WATERLY_DEVICE_TOKEN>" #provided by Waterly
# --------------------------------------------------------
```

Save the project (Ctrl/Cmd+S).


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

## General Description of `sendDataToWaterly(tags)` 

* Resolves the provided tag paths and reads current values (blocking read).
* Builds a payload with tag path/value/timestamp and your org credentials.
* Sends a JSON HTTP POST to Waterly’s endpoint using your configured base URL and API token.
* Logs success/failure via a project logger; any exceptions surface in **Gateway Scripts** status and gateway logs.

> In gateway scope, `print` output goes to the gateway log files; using a logger (`system.util.getLogger`) is recommended for structured logs you can filter on the gateway. You can review gateway status/logging under **Status** on the Gateway Webpage.

---

## Testing & Troubleshooting

* **Validate tag paths:** Test reads in the **Designer Script Console** with `system.tag.readBlocking([...])` to confirm values. (Note: the console runs in Designer scope; for gateway-only behavior, rely on the Gateway Scripts status page/logs.)
* **Check status:** Gateway Webpage → **Status ▸ Gateway Scripts** shows whether your Scheduled/Timer scripts are running, last run, and errors.
* **Project saves:** If a script doesn’t appear to run, make sure you saved the project after adding/enabling the event.


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

* **v1.0.0** – Initial Ignition project export and README.
