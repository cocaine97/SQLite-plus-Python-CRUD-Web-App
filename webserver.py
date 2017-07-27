from flask import Flask
import queries as q


app = Flask(__name__)
@app.route('/')
@app.route('/restaurants')
def names():
    res_data = q.res_data()
    res_out = ''
    for res in res_data:
        res_out += "<h1>{}</h1>".format(res.name)
    return res_out

if(__name__ == "__main__"):
    app.debug = True
    app.run(host="0.0.0.0",port = 5000)
