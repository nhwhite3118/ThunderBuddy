import config
from urllib.request import urlopen
import json
from twilio.rest import TwilioRestClient
import pymysql
import time

#We need to keep track of the number of unique cities we ask weatherunderground
#for. We get 10 API calls/minute, and 500/day, so we need to keep totals
wunderground_this_day = 0
#We need to cache cities so that our usage scales with unique cities instead
#of unique users
forecasts = {}
client = TwilioRestClient(config.TWILIO_ACCOUNT_KEY, config.TWILIO_AUTH_KEY)
conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='thunderbuddy')


def make_forecast(city,state):
    # Retrieve Weather Underground Data
    f = urlopen("http://api.wunderground.com/api/" + config.WEATHER_UNDERGROUND_API_KEY + "/forecast/q/"+state+"/"+city+".json")
    json_string = f.read().decode('utf-8')
    parsed_json = json.loads(json_string)
    forecastList = parsed_json["forecast"]["txt_forecast"]["forecastday"]

    message = ""
    for forecastEntry in forecastList:
        fcttext = forecastEntry["fcttext"].lower()
        fcttext_metric = forecastEntry["fcttext_metric"].lower()
        if "thunder" in forecastEntry or "thunder" in fcttext_metric:
            print("Appending to message - thunder coming on " + forecastEntry["title"] + "!")
            message += "Thunder coming on " + forecastEntry["title"] + "!\n"
    f.close()
    return message

def send_alerts():
    wunderground_this_min=0
    cur = conn.cursor()
    cur.execute("SELECT * FROM user")
    for user in cur:
        number = str(user[0])
        city = str(user[1])
        state = str(user[2])
        if city+state not in forecasts: #find forecasts only for new cities
            print("Checking forecast for "+city)
            wunderground_this_min+=1
            if(wunderground_this_min>=10):  #Only make 10 api calls/min
                time.sleep(120)
                wunderground_this_min=0
            forecasts[city+state] = make_forecast(city,state)
        #send_email(number+"@vtext.com","Test")
        if forecasts[city+state]: #if there is thunder, message the user
            send_email(number+"@vtext.com",forecasts[city+state])
            #client.messages.create(to = number, from_ = config.TWILIO_NUMBER, body = forecasts[city+state])




def send_email(recipient,body, user="thunderbuddyproject@gmail.com", pwd=config.EMAIL_PASSWORD, subject="ThunderBuddy"):
    import smtplib

    gmail_user = 'thunderbuddyproject@gmail.com'
    gmail_pwd = config.EMAIL_PASSWORD
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print ('successfully sent the mail')
    except:
        print ("failed to send mail")



send_alerts()

