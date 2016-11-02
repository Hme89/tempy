from flask import url_for, render_template, redirect
from FlaskApp import app
from src.pictrl.cabinctrl import HeatControl

hc = HeatControl()
    
@app.route('/')
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    return redirect(url_for("index"))

@app.route("/user/<username>")
def show_user_profile(username):
    return "User {}".format(username)

@app.route("/simple")
def simple_ui():
    return hc.read_temp()
    #return "Simple UI page"

@app.route("/advanced")
def advanced_ui():
    return "Advanced UI page"

@app.route('/about')
def about():
    return render_template("about.html")
