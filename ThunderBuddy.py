import config
from urllib.request import urlopen
import json
from twilio.rest import TwilioRestClient

# Retrieve Weather Underground Data
f = urlopen("http://api.wunderground.com/api/" + config.WEATHER_UNDERGROUND_API_KEY + "/forecast/q/KS/Salina.json")
json_string = f.read().decode('utf-8')
parsed_json = json.loads(json_string)
forecastList = parsed_json["forecast"]["txt_forecast"]["forecastday"]
for forecastEntry in forecastList:
    fcttext = forecastEntry["fcttext"].lower()
    fcttext_metric = forecastEntry["fcttext_metric"].lower()
    if "thunder" in forecastEntry or "thunder" in fcttext_metric:
        print("Thunder coming on " + forecastEntry["title"] + "!")

client = TwilioRestClient(config.TWILIO_ACCOUNT_KEY, config.TWILIO_AUTH_KEY)

message = client.messages.create(to=config.RECIPIENT, from_=config.TWILIO_NUMBER,
                                 body="Hello there!")
# Send SMS alerts
f.close()
