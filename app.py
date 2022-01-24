import numpy as np
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
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return(
        f"List of all Available Routes are:<br/>"  
        f"1: Precipitation Route (Previous year):<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"2: Stations List Route:<br/>"
        f"/api/v1.0/stations<br/>"
        f"3: Temperature Observations Route:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"4: Dates Route:<br/>"
        f"When given the start date, calculate MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"/api/v1.0/start<br/>"
        f"When given the start and the end date, calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"
        f"/api/v1.0/start/end<br/>"
    )

###########################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation and date"""
    # Query all precipitation and date
    precipitation_db = session.query(measurement.date,measurement.prcp).all()

    session.close()

    # Convert list of tuples into dictionary
    precepitation =[]
    for date,prcp in precipitation_db:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precepitation.append(prcp_dict)

    return jsonify(precepitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations from the dataset 
    stations = [measurement.station]
    all_stations = session.query(*stations).\
        group_by(measurement.station).all()
    session.close()

    stations_list = list(np.ravel(all_stations)) 
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tempartureobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the last year of data.
    prev_year = '2016-08-23'
    tobs = [measurement.date, measurement.tobs]
    station_temps = session.query(*tobs).\
            filter(measurement.date >= prev_year, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()
    session.close()

    all_tobs=[]
    for tobs,date in station_temps:
        tobs_list={}
        tobs_list['date']=date
        tobs_list['tobs']=tobs
        all_tobs.append(tobs_list)
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>/<end>")
def temps_route(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()
    tobs_1={}
    tobs_1["Min_Temp"]=results[0][0]
    tobs_1["avg_Temp"]=results[0][1]
    tobs_1["max_Temp"]=results[0][2]
    return jsonify(tobs_1)

@app.route("/api/v1.0/<start>")
def temps_route2(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).all()
    session.close()
    tobs_2={}
    tobs_2["Min_Temp"]=results[0][0]
    tobs_2["avg_Temp"]=results[0][1]
    tobs_2["max_Temp"]=results[0][2]
    return jsonify(tobs_2)

if __name__ == '__main__':
    app.run(debug=True)