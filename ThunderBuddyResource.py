import config
from flask import Flask
import pymysql
import zipcode

app = Flask(__name__)

conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='thunderbuddy')
cur = conn.cursor()
cur.execute("SELECT * FROM user")
for r in cur:
    print(r)


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

    sql = "INSERT INTO user(number,city,state) VALUES(%s,%s,%s)"
    zipcodeInfo = zipcode.isequal(zip)
    v = (str(number), str(zipcodeInfo.city), str(zipcodeInfo.state))
    cur.execute(sql, v)
    conn.commit()
    return "Subscribed - " + str(number)


# unsubscribes a user by removing their number from the database
@app.route("/api/unsubscribe/number/<number>", methods=["POST"])
def unsubscribe(number):
    try:
        if len(str(int(number))) > 15:
            return "Please input a valid number"
    except:
        return "Please input a valid number"
    print("About to remove " + str(number) + " from user")
    cur.execute("DELETE FROM user WHERE number=" + number)
    conn.commit()

    return "Unsubscribed - " + str(number)


if __name__ == "__main__":
    app.run()

cur.close()
conn.close()
