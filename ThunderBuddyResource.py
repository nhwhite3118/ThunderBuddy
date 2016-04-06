import config
from flask import Flask
import pymysql
app = Flask(__name__)

conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='thunderbuddy')
cur = conn.cursor()
cur.execute("SELECT * FROM user")
for r in cur:
    print(r)

@app.route("/api/subscribe/number/<number>")
def subscribe(number):
    try:
        if len(str(int(number)))>15:
            return "Please input a valid number"
    except:
            return "Please input a valid number"
    cur.execute("DELETE FROM user WHERE number="+number)
    conn.commit()
    city="Austin"
    state="TX"
    sql = "INSERT INTO user(number,city,state) VALUES(%s,%s,%s)"
    v = (str(number),str(city),str(state))
    cur.execute(sql,v)
    conn.commit()
    return "Hello! - " + str(number)

@app.route("/api/unsubscribe/number/<number>")
def unsubscribe(number):
    try:
        if len(str(int(number)))>15:
            return "Please input a valid number"
    except:
            return "Please input a valid number"
    print("About to remove "+str(number)+" from user")
    cur.execute("DELETE FROM user WHERE number="+number)
    conn.commit()
    print("User now contains: ")
    cur.execute("SELECT * FROM user")
    for r in cur:
        print(r)

    return "Goodbye! - " + str(number)

if __name__ == "__main__":
    app.run()

cur.close()
conn.close()
