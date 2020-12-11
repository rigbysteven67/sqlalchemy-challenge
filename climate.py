# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 22:50:30 2020

@author: Steven
"""

from sqlalchemy import create_engine
import pandas as pd

from flask import Flask, jsonify

import json

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

app = Flask(__name__)

#%%
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
    )

#%%
@app.route("/api/v1.0/precipitation")
def precip():
    
    query = f'''
        select 
            date,
            avg(prcp) as avg_prcp
        from measurement 
        where 
            date >= (Select DATE(MAX(date),'-1 year') FROM measurement)
        group by
            date
        order by 
            date
        '''

    recent_year_precip_data = pd.read_sql(query, engine)
    
    recent_year_precip_data_json = recent_year_precip_data.to_json(orient='records') 

    return recent_year_precip_data_json


#%%
@app.route('/api/v1.0/stations')
def stations():

    query = f'''
        select distinct station
        from measurement
        '''
        
    stations_df = pd.read_sql(query, engine)

    stations_json = stations_df.to_json(orient='records') 

    return stations_json


#%%
@app.route('/api/v1.0/tobs')
def tobs():
    
    query = f'''
        select 
            station,
            count(station) as station_count,
            min(tobs) as lowest_temperature,
            max(tobs) as highest_temperature,
            avg(tobs) as avg_tobs
        from 
            measurement 
        group by 
            station
        order by 
            station_count desc
        limit 1
        '''

    most_active_station_df = pd.read_sql(query, engine)

    most_active_station = most_active_station_df['station'].values[0]
    
    query = f'''
        select
            date,
            tobs
        from 
            measurement 
        where 
            date >= (Select DATE(MAX(date),'-1 year') FROM measurement)
            and station = '{most_active_station}'
        order by 
            date
        '''
    
    most_tobs = pd.read_sql(query, engine) 
                       
    tobs_json = most_tobs.to_json(orient='records') 

    return tobs_json

#%%

@app.route(f'/api/v1.0/<start_date>')

def calc_temps(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    query = f'''
            select
                min(tobs) as lowest_temperature,
                max(tobs) as highest_temperature,
                avg(tobs) as avg_tobs
            from 
                measurement 
            where 
                date >= '{start_date}'
            '''
    
    temp_stats_df = pd.read_sql(query, engine)
    
    #temp_stats = tuple(temp_stats_df.values[0])
    
    temp_stats_json = temp_stats_df.to_json(orient='records') 
    
    return temp_stats_json


#%%

@app.route(f'/api/v1.0/<start_date>/<end_date>')

def calc_temps2(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    query = f'''
            select
                min(tobs) as lowest_temperature,
                max(tobs) as highest_temperature,
                avg(tobs) as avg_tobs
            from 
                measurement 
            where 
                date between '{start_date}' and '{end_date}'
            '''
    
    temp_stats_df = pd.read_sql(query, engine)
    
    #temp_stats = tuple(temp_stats_df.values[0])
    
    temp_stats_json = temp_stats_df.to_json(orient='records') 
    
    return temp_stats_json


#%%
if __name__ == '__main__':
    app.run(debug=True)
