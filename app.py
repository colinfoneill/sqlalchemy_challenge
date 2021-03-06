#import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

import datetime as dt

#create an app
app = Flask(__name__)

#define the home page route
@app.route("/")
def home():
    print("Server received request for Home page")
    return (
        f"Welcome to the Home page! Below are your available routes:<br/>"
        f"'Precipitation': /api/v1.0/precipitation<br/>"
        f"'Stations': /api/v1.0/stations<br/>"
        f"'Temperature': /api/v1.0/tobs<br/>"
        f"'Start' (to calculate min, max, and avg temp for each day): /api/v1.0/start<br/>"
        f"'End' (to calculate min, max, and avg temperature for a specified date range): /api/v1.0/start/end<br/>"
    )

#define the route for precipitation data and return a dictionaried form of the precipitation query

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

#save reference to the measurements table
Measurement = Base.classes.measurement

#define route to precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    #create seassion (link) from Python to the DB
    session = Session(engine)

    #query all dates and correpsonding precipitation
    results = session.query(Measurement.date, func.sum(Measurement.prcp)).group_by(Measurement.date).order_by(Measurement.date).all()

    #close session
    session.close()

    #create a dictionary from the row data and append to a list of all_dates
    all_dates = []
    for date, precip in results:
        dict = {}
        dict[date] = precip
        all_dates.append(dict)
    
    
    print("Server received request for precipitation page")
    return jsonify(all_dates)

#define route for stations and return list of stations from the dataset

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

#save reference to the measurements table
Stations = Base.classes.station

#define route for stations data
@app.route("/api/v1.0/stations")
def stations():
    #create seassion (link) from Python to the DB
    session = Session(engine)

    #query all dates and correpsonding precipitation
    results = session.query(Stations.name).all()

    #close session
    session.close()

     # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    print("Server received request for stations page")
    return jsonify(all_stations)

#query dates and temperatures for the most active station from the last year of data and return JSON list of data queried
#define route for temperature data
@app.route("/api/v1.0/tobs")
def temperatures():
    #create seassion (link) from Python to the DB
    session = Session(engine)

    #query dates and temperatures of the most active station from the last year of data
    #define the "year_ago" variable
    year_ago = year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, func.avg(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date > year_ago).order_by(Measurement.date).all()

    #close session
    session.close()

    #create a dictionary from the row data and append to a list of all_temps
    all_temps = []
    for date, temp in results:
        temps = {}
        temps["date"] = date
        temps["temp"] = temp
        all_temps.append(temps)
    
    
    print("Server received request for temps page")
    return jsonify(all_temps)

    

#return JSON list of the min temp, average temp, and max temp for a given start or start-end range
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#define route for start range query
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    
    #normalize date input
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    
    #query results
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    #close session
    session.close()

    #store results into dictionaries and lists so we can jsonify the results   
    temp_stats = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        temp_stats.append(temp_dict)
    
    #jsonify results
    return jsonify(temp_stats)

#when given start and end date calculate TMIN, TAVG, TMAX for all dates between the two dates given (inclusive)
#define route for start and end range query
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    
    #normalize date input
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, '%Y-%m-%d')
    
    #query results
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt).all()
    
    #close session
    session.close()
    
    #store results into dictionaries and lists so we can jsonify the results 
    temp_stats = []
    for result in results:
        temp_dict = {}
        temp_dict["start_date"] = start_dt
        temp_dict["end_date"] = end_dt       
        temp_dict["min"] = result[0]
        temp_dict["max"] = result[1]
        temp_dict["avg"] = result[2]
        temp_stats.append(temp_dict) 

    #jsonify results
    return jsonify(temp_stats)



if __name__ == "__main__":
    app.run(debug=True)