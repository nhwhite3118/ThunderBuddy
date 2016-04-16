import config
from urllib.request import urlopen
import json
import pymysql
import time
import smtplib

# We need to keep track of the number of unique cities we ask weatherunderground
# for. We get 10 API calls/minute, and 500/day, so we need to keep totals
wundergroundThisDay = 0
# We need to cache cities so that our usage scales with unique cities instead
# of unique users
forecasts = {}
conn = pymysql.connect(host="127.0.0.1", user=config.DB_USER, passwd=config.DB_PASSWORD, db="thunderbuddy")


def sendAlerts():
    print("time - " + time.ctime())
    wundergroundThisMinute = 0
    cur = conn.cursor()
    cur.execute("SELECT * FROM user")

    for user in cur:
        number = user[0]
        city = user[1]
        state = user[2]
        portal = user[3]
        if city + state not in forecasts:
            # find forecasts only for new cities
            print("Checking forecast for " + city)
            wundergroundThisMinute += 1
            if wundergroundThisMinute >= 10:
                # Only make 10 api calls/min
                time.sleep(120)
                wundergroundThisMinute = 0
            forecasts[city + state] = makeForecast(city, state)

        if len(forecasts[city + state]) > 0:
            # if there is thunder, message the user
            sendEmailSms(number + "@" + portal, forecasts[city + state])


def makeForecast(city, state):
    # Retrieve Weather Underground Data
    f = urlopen("http://api.wunderground.com/api/" + config.WEATHER_UNDERGROUND_API_KEY + "/forecast/q/" + state + "/" + city + ".json")
    jsonString = f.read().decode('utf-8')
    parsedJson = json.loads(jsonString)
    forecastList = parsedJson["forecast"]["txt_forecast"]["forecastday"]
    thunderDays = []

    message = ""
    for forecastEntry in forecastList:
        fcttext = forecastEntry["fcttext"].lower()
        fcttextMetric = forecastEntry["fcttext_metric"].lower()
        if "thunder" in fcttext or "thunder" in fcttextMetric:
            thunderDays.append(forecastEntry["title"])

    if len(thunderDays) > 0:
        # build message and replace last comma with 'and'
        message = "Thunder coming on " + ", ".join(thunderDays)[::-1].replace(",", "dna ", 1)[::-1]

    f.close()
    return message


def sendEmailSms(recipient, body):
    gmailUser = 'thunderbuddyproject@gmail.com'
    gmailPassword = config.EMAIL_PASSWORD
    to = recipient if type(recipient) is list else [recipient]

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmailUser, gmailPassword)
        server.sendmail(gmailUser, to, body)
        server.close()
        print("successfully sent email to - " + str(to))
    except:
        print("failed to send email to - " + str(to))


sendAlerts()
