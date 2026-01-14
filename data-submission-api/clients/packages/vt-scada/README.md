# Waterly ⟷ VTScada Integration (Option A)

This guide provides a single, supported path for sending VTScada tag data to WaterlyConnect using VTScada's native HTTPSend capabilities. It is written for integrators with minimal scripting experience.

## Requirements
- VTScada **12.0.19 or later** (Help > About VTScada).
- Waterly credentials: API token, device ID, and endpoint URL.

*If you are on an earlier VTScada version, contact support@waterly.com for guidance on legacy options.*

## Files to Install
Copy the following files into your VTScada application folder (example paths shown):
- Script module: `C:\VTScada\MyApp\Source\WaterlyConnect.SRC`
- Tag list: `C:\VTScada\MyApp\WaterlyConnect\Config\WaterlyTags.csv`

Sample files are included in this repo:
- `packages/vt-scada/WaterlyConnect.SRC`
- `packages/vt-scada/WaterlyTags.csv`

## Script Configuration (Required Edits)
Open `WaterlyConnect.SRC` and edit only this configuration block:
- `WaterlyURL`: Waterly endpoint (typically `https://app.waterlyapp.com/connect/submit`)
- `WaterlyToken`: your API token
- `WaterlyDeviceID`: your device ID
- `WaterlyTagsCsv`: full path to the CSV file (recommended under `MyApp\WaterlyConnect\Config`)
- `LogPath`: file path for support logs (recommended under `MyApp\WaterlyConnect\Logs`)
- `BatchSize`: default is `100` (higher values may degrade processing performance)

## CSV Configuration (Schedules)
Edit `WaterlyTags.csv` to define which tags are sent and when:
- `TagPath`: full VTScada tag path (use backslashes)
- `Enabled`: `1` to send, `0` to ignore
- `Interval`: one of `minute`, `hour`, `day_at_time`
- `IntervalNum`:
  - `minute`: every N minutes (e.g., `5`)
  - `hour`: every N hours (e.g., `1`)
  - `day_at_time`: HHMMSS in 24-hour time; use `|` to send multiple times (e.g., `070000|190000`)
- `Description`: optional note for operators (avoid commas)

Only rows with `Enabled=1` are sent. Spaces around `Interval` or `IntervalNum` are ignored, but avoid spaces in `TagPath`. For `day_at_time`, use seconds `00` unless your trigger runs more frequently than once per minute.

## Install in VTScada
1. Place the files in the paths above. Create `MyApp\WaterlyConnect\Config` and `MyApp\WaterlyConnect\Logs` if they do not exist.
2. In VTScada, run **File > Import File Changes** to load `WaterlyConnect.SRC`.
3. Create a **Trigger Tag** (or timer tag) that runs **every minute**:
   - **On condition**: repeat every 60 seconds
   - **Off condition**: fixed delay 5 seconds (creates a short pulse)
4. Create a **Script Tag** (e.g., `WaterlyPost`):
   - Module: `WaterlyConnectPost`
   - Scope Tag: your trigger tag

## Logging and Troubleshooting
The script logs to both VTScada logs and a file path you set in `LogPath`.
- VTScada logs: open **Log Viewer** and search for `WaterlyConnect`.
- File log: navigate to the file under `MyApp\WaterlyConnect\Logs` and share it with support if needed.

## How the Script Works
- Reads enabled tags from `WaterlyTags.csv` on each trigger.
- Filters tags by schedule and sends them in batches of up to 100 tags.
- Logs a summary of successes/failures after each run.
