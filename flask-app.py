from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import mars_scrape

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)



@app.route("/")
def index():
    marsinfo = mongo.db.marsinfo.find_one()
    return render_template("index.html", marsinfo=marsinfo)


@app.route("/scrape")
def scraper():
    marsinfo = mongo.db.marsinfo
    mars_data = mars_scrape.scrape()
    marsinfo.update(
        {},
        mars_data,
        upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
