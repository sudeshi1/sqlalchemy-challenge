import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
        f"Climate Analysis: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end> <br/>"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
        # Create our session (link) from Python to the DB
        session = Session(engine)
        
        # Convert the Query Results to a Dictionary Using `date` as the Key and `prcp` as the Value
        # Calculate the Date 1 Year Ago from the Last Data Point in the Database
        one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
        
        # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
        prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()
        
        # Close session
        session.close()
        
        # Convert List of Tuples Into a Dictionary
        prcp_data_list = dict(prcp_data)
        # Return JSON Representation of Dictionary
        return jsonify(prcp_data_list)

# Station Route
@app.route("/api/v1.0/stations")
def stations():
        # Create our session (link) from Python to the DB
        session = Session(engine)
    
        # Query all stations
        no_stations=session.query(Station.name).all()

        # Close the session
        session.close()

        # Convert list of tuples into normal list
        all_stations = list(np.ravel(no_stations))

        # Jsonify the list
        return jsonify(all_stations)

# TOBs Route
@app.route("/api/v1.0/tobs")
def tobs():
        # Create our session (link) from Python to the DB
        session = Session(engine)
        
        # Query for the Dates and Temperature Observations from a Year from the Last Data Point
        one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
        
        # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
        tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()
                
        # Close the session
        session.close()
        
        # Create a dictionary from the row data and append to a list of all_tobs
        all_tobs=[]
        
        for date, tobs in tobs_data:
                all_tobs.append({date:tobs})

        # Jsonify the list
        return jsonify(all_tobs)

# Start Day Route
@app.route("/api/v1.0/<start>")
def temperatures_start(start):
    ## Fetch the minimun, average and maximum temperature for the dates
       ## greater or equal to the start date, or a 404 if not
       
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the min, max and average temperatures
    sel=[Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    temperatures=session.query(*sel).filter(Measurement.date>=start).all()
    
    # Query all the dates within the database
    dates=session.query(Measurement.date).all()
    
    # Close the session  
    session.close()
    
    # Convert list of tuples into normal list
    all_dates=list(np.ravel(dates))
    
    #  Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start
    for start_date in all_dates:
        if start_date==start:
            results_start = {
                "Start Date": start,
                "End Date": "2017-08-23",
                "Temperature Minimum": temperatures[0][1],
                "Temperature Average": round(temperatures[0][3],1),
                "Temperature Maximum": temperatures[0][2]
            }
            return jsonify([results_start])
    return jsonify([f"Error!! Data between '{start}' and '2017-08-23' was not found."]), 404

# End Day Route
@app.route("/api/v1.0/<start>/<end>")
def temperatures_end(start,end):
    ## Fetch the minimun, average and maximum temperature for the dates
       ## greater or equal to the start date and lesser or equal to the end date, or a 404 if not
       
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all temperatures
    sel=[Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    temperatures=session.query(*sel).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    
    # Query all the dates within the database
    dates=session.query(Measurement.date).all()
    
    # Close the session  
    session.close()
    
    # Convert list of tuples into normal list
    all_dates=list(np.ravel(dates))
    for start_date in all_dates:
        if start_date==start:
            for end_date in all_dates:
                if end_date==end:
                    if end>start:
                        results_start_end = {
                            "Start Date": start,
                            "End Date": end,
                            "Temperature Minimum": temperatures[0][1],
                            "Temperature Average": round(temperatures[0][3],1),
                            "Temperature Maximum": temperatures[0][2]
                        }
                        return jsonify([results_start_end])
            return jsonify([f"ERROR!! Data between '{start}' and '{end}' was not found."
                            f"When entering the end date, make sure the start date is entered first and the end date is entered last."]), 404
    return jsonify([f"Error!! Data between '{start}' and '{end}' was not found."
                        f"When entering the end date, make sure the start date is entered first and the end date is entered last."]), 404

# Define Main Behavior
if __name__ == '__main__':
    app.run(debug=True)