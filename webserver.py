from flask import Flask
app = Flask(__name__)
@app.route('/')
def intro():
    return "<h1>Flask is up and Running!<h1>"

if(__name__ == "__main__"):
    app.debug = True
    app.run(host="0.0.0.0",port = 5000)
