from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route("/")
def home():

    with open("components.json", "r") as file:
        components = json.load(file)

    return render_template("index.html", components=components)

if __name__ == "__main__":
    app.run(debug=True)