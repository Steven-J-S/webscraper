# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 07:56:56 2021

@author: zm176oos
"""

def open_data(sql):
    import pyodbc
    import pandas as pd
    
    #### DWH connectie 
    server_1cijf = '1CIJFERSQLPRD.duo.local' 
    database = 'master' 
    connectie = pyodbc.connect('DRIVER={SQL Server};SERVER='+server_1cijf+';DATABASE='+database+';trusted_connection=true') 
        
    data = pd.read_sql(sql, connectie)
      
    return data