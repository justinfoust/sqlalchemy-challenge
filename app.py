import datetime as dt
import re

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date1/start-date(yyyyMMdd)<br/>"
        f"/api/v1.0/date2/start-date(yyyyMMdd)/end-date(yyyyMMdd)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    prcp_results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    prcp_data = {}
    for date, prcp in prcp_results:
        prcp_data.setdefault(date,[]).append(prcp)

    return jsonify(prcp_data)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    sta_results = session.query(Station.name).all()

    session.close()

    sta_names = list(np.ravel(sta_results))

    return jsonify(sta_names)    


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date = session.query(Measurement.date).\
                    order_by(Measurement.date.desc()).\
                    first()[0]

    yr_later_date = str(dt.date.fromisoformat(last_date) - dt.timedelta(days=366))

    tobs_results = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.date > yr_later_date).\
                        filter(Measurement.date < last_date).\
                        all()

    session.close()

    tobs_data = {}
    for date, tobs in tobs_results:
        tobs_data.setdefault(date,[]).append(tobs)

    return jsonify(tobs_data)


@app.route("/api/v1.0/date1/<start>")
def range1(start):
    s_date = '{0}-{1}-{2}'.format(*re.match(r"(....)(..)(..)", start).groups())

    session = Session(engine)

    tobs_stats = session.query(
                    func.min(Measurement.tobs), 
                    func.avg(Measurement.tobs), 
                    func.max(Measurement.tobs)
                    ).\
                    filter(Measurement.date >= s_date).\
                    all()

    session.close()

    tobs_list = list(np.ravel(tobs_stats))
    return jsonify(tobs_stats)


@app.route("/api/v1.0/date2/<start>/<end>")
def range2(start, end):
    s_date = '{0}-{1}-{2}'.format(*re.match(r"(....)(..)(..)", start).groups())
    e_date = '{0}-{1}-{2}'.format(*re.match(r"(....)(..)(..)", end).groups())

    session = Session(engine)

    tobs_rng_stats = session.query(
                    func.min(Measurement.tobs), 
                    func.avg(Measurement.tobs), 
                    func.max(Measurement.tobs)
                    ).\
                    filter(Measurement.date >= s_date).\
                    filter(Measurement.date <= e_date).\
                    all()

    session.close()

    tobs_rng_list = list(np.ravel(tobs_rng_stats))
    return jsonify(tobs_rng_stats)



if __name__ == '__main__':
    app.run(debug=True)