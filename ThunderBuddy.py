import config
#import urllib2
from urllib.request import urlopen
import json

f = urlopen('http://api.wunderground.com/api/'+config.WEATHER_UNDERGROUND_API_KEY+'/geolookup/conditions/q/IA/Cedar_Rapids.json')
json_string = f.read().decode('utf-8')
parsed_json = json.loads(json_string)
location = parsed_json['location']['city']
temp_f = parsed_json['current_observation']['temp_f']
print ("Current temperature in %s is: %s" % (location, temp_f))
f.close()
