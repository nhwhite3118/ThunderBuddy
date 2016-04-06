from flask import Flask
app = Flask(__name__)

@app.route("/api/subscribe/number/<number>")
def subscribe(number):
    return "Hello World! - " + str(number)

if __name__ == "__main__":
    app.run()