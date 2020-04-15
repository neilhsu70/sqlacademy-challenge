import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
	    f"Precipitation Readings<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
	    f"List of Stations<br/>"
        f"/api/v1.0/stations<br/><br/>"
	    f"Temperature Observations (tobs)<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Minimum, average, and maximum temperature for a given date.<br/>"
        f"/api/v1.0/start (YYYY-MM-DD)<br/><br/>"
        f"Minimum, average, and maximum temperature for a given start to end date.<br/>"
        f"/api/v1.0/start/end (YYYY-MM-DD)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.asc()).all()
    session.close()

    measurement_date = [result[0] for result in results]
    measurement_prcp = [result[1] for result in results]
    precipitation_dict = dict(zip(measurement_date, measurement_prcp))

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    results = session.query(Measurement.station).all()
    session.close()

    measurement_stat = [result[0] for result in results]
    measurement_stat_unique = np.unique(measurement_stat).tolist()

    return jsonify(measurement_stat_unique)


@app.route("/api/v1.0/tobs")
def temp_obs():

    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d').date()
    year_ago = last_date - dt.timedelta(days=365)

    temps = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).all()

    temp_list = []

    for i in temps:
        temp_list.append(i[0])

    return jsonify(temp_list)

   
@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)
    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    start_list = []

    startDict = {}
    startDict["Minimum"] = start_query[0][0]
    startDict["Average"] = start_query[0][1]
    startDict["Maximum"] = start_query[0][2]
    start_list.append(startDict)

    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start, end):

    session = Session(engine)
    start_end_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    start_end_list = []
    
    start_end_dict = {}
    start_end_dict["Minimum"] = start_end_query[0][0]
    start_end_dict["Average"] = start_end_query[0][1]
    start_end_dict["Maximum"] = start_end_query[0][2]
    start_end_list.append(start_end_dict)

    return jsonify(start_end_list)    

if __name__ == '__main__':
    app.run(debug=True)