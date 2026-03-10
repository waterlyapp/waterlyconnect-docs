# Waterly ⟷ Ewon Flexy Integration

This folder contains a Flexy BASIC script (`flexy-basic.txt`) that will automatically POST tag values from an Ewon Flexy 205 to the WaterlyConnect API on a schedule.

---

## Contents

```
waterlyconnect-clients/
└─ flexy/
   ├─ README.md             ← this file
   └─ flexy-basic.txt       ← BASIC script for copy/paste to Flexy
```

---

## Prerequisites

* An **Ewon Flexy 205** device with Internet connectivity
* Access to the **Flexy web interface** (for loading BASIC scripts)
* Waterly credentials (API token, endpoint URL, org information).

    * Email **[support@waterly.com](mailto:support@waterly.com)** to request your credentials.

---

## 1) Load the Script into Flexy

1. Open the **Flexy web interface** in your browser.
2. Navigate to **Setup ▸ Scripting ▸ BASIC IDE**.
3. Paste the content of the script (`flexy-basic.txt`).
4. Click **Save & Run**.
5. Optionally set **Autorun** so the script executes automatically after a reboot.

---

## 2) Configure Credentials

At the top of the script, replace the placeholder token with the credentials provided by Waterly:

```basic
$token$ = "<REDACTED>"
$deviceId$ ="<REDACTED>"
$url$   = "https://app.waterlyapp.com/connect/submit"
```

Do **not** commit your token to GitHub. Store it only on your Flexy device.

---

## 3) How It Works

* **Timer** (`TSET 1,300`) triggers every 300 seconds (5 minutes).
* On each trigger, the `SendData` routine builds a JSON payload:

    * **timestamp** = Flexy system time
    * **device** = device ID + type (`ewon`)
    * **tags** = all defined Flexy tags (name, value, last change timestamp)
* The script issues an HTTP POST (`REQUESTHTTPX`) to the WaterlyConnect endpoint.
* **Response handling** is included — success codes are printed, errors are logged.

---

## 4) Optional Logic

You may add conditional sending logic (e.g., only send tags from a specific group). The script includes commented examples:

```basic
GroupATag$ = GETSYS TAG, "IVGroupA"
IF (GroupATag$ = "1") THEN
  ' Send data
ELSE
  PRINT "Not in correct group"
ENDIF
```

---

## 5) Monitoring & Debugging

* **Console logs** (`PRINT`) appear in the Flexy diagnostic logs.
* The script reports both request attempts and response status codes.
* If you experience connectivity issues, verify that your Flexy can reach `https://app.waterlyapp.com`.

---

## 6) Security Notes

* Keep your **Waterly API token** private.
* Avoid storing the token in public repos.
* Use Ewon’s built-in user security to restrict who can edit scripts.

---

## About Flexy & Waterly

The Ewon Flexy is an industrial gateway that supports PLC connectivity, remote access, and custom scripting. This integration bridges Flexy tag data directly into **WaterlyConnect** for analytics and reporting.



