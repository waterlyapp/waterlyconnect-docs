import system
import time
from com.inductiveautomation.ignition.common.model.values import QualityCode


# ==========================================
# Configuration:
# ==========================================
waterly_api_url = "https://connect.waterly.com/api/data-submission/v1/submit"
waterly_device_id = '<WATERLY_DEVICE_ID>'
waterly_device_token = "<WATERLY_DEVICE_TOKEN>"

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
		response = system.net.httpPost(
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
		logger.info("Successful Post to WaterlyConnect" + response)  #for debugging
	except Exception as e:
		logger.error("Error posting to WaterlyConnect: %s" % str(e))
	
