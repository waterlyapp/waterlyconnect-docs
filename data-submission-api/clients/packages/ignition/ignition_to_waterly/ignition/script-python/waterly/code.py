import system
import time
from com.inductiveautomation.ignition.common.model.values import QualityCode
from java.lang import Exception as JavaException, System


# ==========================================
# Configuration:
# ==========================================
waterly_api_url = "https://connect.waterly.com/api/data-submission/v1/submit"
waterly_device_id = '<WATERLY_DEVICE_ID>'

system_tags = [
	"[System]Gateway/CurrentDateTime",
	"[System]Gateway/Timezone",
	"[System]Gateway/UptimeSeconds"
]

logger = system.util.getLogger("WaterlyConnect")

try:
	string_types = (basestring,)  # Ignition uses Jython 2.7, including unicode paths.
except NameError:
	string_types = (str,)


def sendDataToWaterly(tags=None, send_now_time_all=False):
	"""Send full tag paths, optionally using one execution timestamp per batch.

	Each entry may be a path string or a dict with tag_name and optional
	send_now_time (default False). send_now_time_all overrides every entry,
	including the automatically appended system tags.
	"""
	# The Gateway JVM inherits this variable at startup. Never persist it in
	# project resources or fall back to a token configured in the script.
	try:
		waterly_device_token = System.getenv("WATERLY_DEVICE_TOKEN")
	except (Exception, JavaException):
		logger.error("Waterly Connect configuration error: cannot read WATERLY_DEVICE_TOKEN from the Gateway environment.")
		return
	if not waterly_device_token or not waterly_device_token.strip():
		logger.error("Waterly Connect configuration error: WATERLY_DEVICE_TOKEN environment variable is not set or is blank.")
		return

	#check and normalize inputs
	tags = tags or []
	if isinstance(tags, string_types) or isinstance(tags, dict):
		tags = [tags]

	# Keep caller-owned lists/dicts unchanged so scheduled calls can reuse them.
	tag_configs = [tag if isinstance(tag, dict) else {"tag_name": tag} for tag in tags]
	tag_configs.extend({"tag_name": tag_name} for tag_name in system_tags)
	tag_paths = [config["tag_name"] for config in tag_configs]
	# read values
	tag_values = system.tag.readBlocking(tag_paths)
	# Capture once per invocation and reuse for the body and opted-in tags.
	now = int(time.time())

	submission_tags = []

	for idx, tag in enumerate(tag_values):
		config = tag_configs[idx]
		tag_name = config["tag_name"]
		if tag.quality == QualityCode.Good:
			use_now = send_now_time_all or config.get("send_now_time", False)
			submission_tags.append({
				"last_change_timestamp" : now if use_now else int(tag.timestamp.time // 1000),
				"name" : tag_name,
				"value" : str(tag.value)
			})
	body={
		"device" : {
			"id" : waterly_device_id,
			"type" : "Ignition"
		},
		"timestamp" : now,
		"tags" : submission_tags
	}

	json_payload = system.util.jsonEncode(body)
	headers = {
		"x-waterly-request-type": "WaterlyConnect",
		"x-waterly-connect-token": waterly_device_token
	}
	try:
		# use 'alternate' syntax for httpPost, explicitly defining parameters
		system.net.httpPost(
			waterly_api_url,
			"application/json",      # contentType
			json_payload,            # postData
			10000,                   # connectTimeout
			60000,                   # readTimeout
			None, None,              #
			headers,                 # headerValues
			False,					 # bypass cert validation
			True					 # throw on error
		)
		# Responses and exception messages can echo credentials. Log only
		# fixed messages, without headers, response bodies, or exception details.
		logger.info("Successful Post to WaterlyConnect")
	except (Exception, JavaException):
		logger.error("Error posting to WaterlyConnect. Check the endpoint, Gateway token configuration, and network connectivity.")
