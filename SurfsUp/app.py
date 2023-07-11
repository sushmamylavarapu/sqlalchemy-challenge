# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from datetime import datetime
from flask import Flask as jsonify

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session=Session()

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
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_data = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    return jsonify(dict(prcp_data))


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Station.station).all()
    session.close()
    return jsonify([station[0] for station in station_data])


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    last_one_year_date = session.query(func.date(func.max(Measurement.date), '-1 year')).scalar()
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= last_one_year_date).\
        filter(Measurement.station == most_active_station).all()
    session.close()
    return jsonify(dict(tobs_data))

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    session = Session(engine)
    if end is None:
        data = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .all()
        )
    else:
        data = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .filter(Measurement.date <= end)
            .all()
        )
    session.close()
    return jsonify(data[0])


if __name__ == "__main__":
    app.run(debug=True)
    