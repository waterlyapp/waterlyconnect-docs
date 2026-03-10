import system
import time
from com.inductiveautomation.ignition.common.model.values import QualityCode


# ==========================================
# Configuration:
# ==========================================
waterly_api_url = "https://app.waterlyapp.com/connect/submit"
waterly_device_id = '<WATERLY_DEVICE_ID>'
waterly_device_token = "<WATERLY_DEVICE_TOKEN>"

system_tags = [
	"[System]Gateway/CurrentDateTime", 
	"[System]Gateway/Timezone",
	"[System]Gateway/UptimeSeconds"
]

logger = system.util.getLogger("WaterlyConnect")

def sendDataToWaterly(tags=None):
	#check and normalize inputs
	tags = tags or []
	if isinstance(tags, str):
		tags = [tags]
	
	tags.extend(system_tags)
	# read values
	tag_values = system.tag.readBlocking(tags)
	# set timestamp
	now = int(time.time())
	
	submission_tags = []
	
	for idx, tag in enumerate(tag_values):
		tag_name = tags[idx]
		if tag.quality == QualityCode.Good:
			submission_tags.append({
				"last_change_timestamp" : tag.timestamp.time/1000,
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
	
	

	url = "https://app.waterlyapp.com/connect/submit"
	json_payload = system.util.jsonEncode(body)
	headers = {
	    "x-waterly-request-type": "WaterlyConnect",
	    "x-waterly-connect-token": waterly_device_token
	}
	try:
		# use 'alternate' syntax for httpPost, explicitly defining parameters
		response = system.net.httpPost(
		    url,
		    "application/json",      # contentType
		    json_payload,            # postData 
		    10000,                   # connectTimeout
		    60000,                   # readTimeout
		    None, None,              # 
		    headers,                 # headerValues 
		    False,					 # bypass cert validation
		   	True					 # throw on error
		)
		logging.info("Successful Post to WaterlyConnect" + response)  #for debugging
	except Exception as e:
		logging.error("Error posting to WaterlyConnect: %s" % str(e))
	


