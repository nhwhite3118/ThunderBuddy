import config
from flask import Flask
import flask
import pymysql
import zipcode
from twilio.rest.lookups import TwilioLookupsClient
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from datetime import datetime

app = Flask(__name__)

carrierPortalLookup = {
    "Verizon Wireless": "vtext.com",
    "Sprint Spectrum, L.P.": "messaging.sprintpcs.com",
    "AT&T Wireless": "txt.att.net",
}

# twilio
client = TwilioLookupsClient()
client = TwilioLookupsClient()

# database
conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='thunderbuddy')
cur = conn.cursor()


# subscribes a user by inserting their number into the database
@app.route("/api/subscribe/number/<number>/zip/<zip>", methods=["POST"])
def subscribe(number, zip):
    try:
        if len(str(int(number))) > 15:
            return "Please input a valid number"
    except:
        return "Please input a valid number"
    # allow users to change their location without duplicating in the bases
    cur.execute("DELETE FROM user WHERE number=" + number)
    conn.commit()

    zipcodeInfo = zipcode.isequal(zip)
    numberInfo = client.phone_numbers.get(number, include_carrier_info=True)
    carrier = numberInfo.carrier['name']
    # Convert carrier to portal
    portal = ""
    if carrier in carrierPortalLookup:
        portal = carrierPortalLookup[carrier]
    else:
        return "We are sorry, but ThunderBuddy does not support your carrier"

    sql = "INSERT INTO user(number,city,state,carrier_portal) VALUES(%s,%s,%s,%s)"
    city = str(zipcodeInfo.city).replace(" ", "_")
    state = str(zipcodeInfo.state)
    v = (str(number), city, state, portal)
    print(str(datetime.now()) + " Adding user - " + carrier + " " + str(v))
    cur.execute(sql, v)
    conn.commit()

    resp = flask.Response("Subscribed " + str(number), status=200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp,


# unsubscribes a user by removing their number from the database
@app.route("/api/unsubscribe/number/<number>", methods=["POST"])
def unsubscribe(number):
    try:
        if len(str(int(number))) > 15:
            return "Please input a valid number"
    except:
        return "Please input a valid number"

    print(str(datetime.now()) + " Removing user - " + number)
    cur.execute("DELETE FROM user WHERE number=" + number)
    conn.commit()

    resp = flask.Response("Unsubscribed " + str(number), status=200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


# debugging helpers
@app.route("/")
def hello():
    resp = flask.Response("Thunder sucks", status=200)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp




if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8000)
    print(str(datetime.now()) + " Flask started...")
    IOLoop.instance().start()

cur.close()
conn.close()
