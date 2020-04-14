from flask import Flask, jsonify
import datetime as dt
import pandas as pd
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import sqlalchemy
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
from datetime import date
style.use('fivethirtyeight')
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_date = last_date[0]
last_date = dt.datetime.strptime(last_date, '%Y-%m-%d').date()
year_ago = last_date - dt.timedelta(days=365)

app = Flask(__name__)

routes = ['/api/v1.0/precipitation', '/api/v1.0/stations', '/api/v1.0/tobs', '/api/v1.0/<start>', '/api/v1.0/<start>/<end>']

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"{routes[0]}<br/>"
        f"{routes[1]}<br/>"
        f"{routes[2]}<br/>"
        f"{routes[3]}<br/>"
        f"{routes[4]}"
    )

@app.route(routes[0])
def prcp():
    session = Session(engine)
    dictt = {}
    date_prcp = session.query(Measurement.date, Measurement.prcp).all()
    for d, p in date_prcp:
        dictt[d] = p
    return jsonify(dictt)

@app.route(routes[1])
def st():
    session = Session(engine)
    return jsonify(session.query(Station.station).all())

@app.route(routes[2])
def tmp():
    session = Session(engine)
    temps = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).all()
    temp_list = []
    for i in temps:
        temp_list.append(i[0])
    return jsonify(temp_list)

@app.route(routes[3])
def start(start):
    session = Session(engine)
    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all())

@app.route(routes[4])
def start_end(start, end):
    session = Session(engine)
    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all())

if __name__ == "__main__":
    app.run(debug=False)