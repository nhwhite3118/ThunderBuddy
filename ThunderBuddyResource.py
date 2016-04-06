import config
from flask import Flask
import pymysql
app = Flask(__name__)

conn = pymysql.connect(host='127.0.0.1', user=config.DB_USER, passwd=config.DB_PASSWORD, db='thunderbuddy')
cur = conn.cursor()
cur.execute("SELECT * FROM user")
for r in cur:
    print(r)
cur.close()
conn.close()

@app.route("/api/subscribe/number/<number>")
def subscribe(number):
    return "Hello World! - " + str(number)

if __name__ == "__main__":
    app.run()
