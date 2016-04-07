import config
from urllib.request import urlopen
import json
import pymysql
import time
import smtplib

# We need to keep track of the number of unique cities we ask weatherunderground
# for. We get 10 API calls/minute, and 500/day, so we need to keep totals
wunderground_this_day = 0
# We need to cache cities so that our usage scales with unique cities instead
# of unique users
forecasts = {}
conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='thunderbuddy')

def send_alerts():
    wunderground_this_min = 0
    cur = conn.cursor()
    cur.execute("SELECT * FROM user")
    for user in cur:
        number = str(user[0])
        city = str(user[1]).replace(" ", "_")
        state = str(user[2])
        if city + state not in forecasts:  # find forecasts only for new cities
            print("Checking forecast for " + city)
            wunderground_this_min += 1
            if wunderground_this_min >= 10:  # Only make 10 api calls/min
                time.sleep(120)
                wunderground_this_min = 0
            forecasts[city + state] = make_forecast(city, state)
        # send_email(number+"@vtext.com","Test")
        if forecasts[city + state]:  # if there is thunder, message the user
            send_email(number + "@vtext.com", forecasts[city + state]) # TODO lookup

def make_forecast(city, state):
    # Retrieve Weather Underground Data
    f = urlopen(
        "http://api.wunderground.com/api/" + config.WEATHER_UNDERGROUND_API_KEY + "/forecast/q/" + state + "/" + city + ".json")
    json_string = f.read().decode('utf-8')
    parsed_json = json.loads(json_string)
    forecastList = parsed_json["forecast"]["txt_forecast"]["forecastday"]

    message = ""
    for forecastEntry in forecastList:
        fcttext = forecastEntry["fcttext"].lower()
        fcttext_metric = forecastEntry["fcttext_metric"].lower()
        if "thunder" in fcttext or "thunder" in fcttext_metric:
            print("Appending to message - thunder coming on " + forecastEntry["title"] + "!")
            message += "Thunder coming on " + forecastEntry["title"] + "!\n"
    f.close()
    return message


def send_email(recipient, body, subject = "ThunderBuddy"):
    gmail_user = 'thunderbuddyproject@gmail.com'
    gmail_pwd = config.EMAIL_PASSWORD
    to = recipient if type(recipient) is list else [recipient]

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (gmail_user, ", ".join(to), subject, body)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(gmail_user, to, message)
        server.close()
        print('successfully sent email')
    except:
        print("failed to send email")


send_alerts()
