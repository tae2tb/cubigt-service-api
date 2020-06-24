#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

from fastapi import FastAPI
import json, csv
import math, os, sys


app = FastAPI()


@app.get("/")
def hello_api():
    return {"Hello": "FastAPI Installed  Done."}

@app.get("/pg_conn/")
def pg_conn():
    import psycopg2
    param = {'host':'122.155.9.78', 'dbname':'cubigtree2019', 'user':'postgres', 'password':'postgresadmin', 'port':5432}
    #param = {'host':'127.0.0.1', 'dbname':'cubigtree2019', 'user':'postgres', 'password':'postgresadmin', 'port':5432}
    #print (param)
    try:
        conn = psycopg2.connect(host=param['host'], dbname=param['dbname'], user=param['user'], password=param['password'], port=param['port'])
        cursor = conn.cursor()
        print ("Database Connected!\n")
        
    except:
        print ('Unable connecting to database\n')
        cursor = None
    return cursor

@app.get("/pg_cuinvt/{id}/{version}")
def pg_cuinvt(id: str, version: str):
    cursor = pg_conn()
    sql = """
    select name_t, name_e, description
    from tree_inventory inv left join tree tre on inv.tree_id = tre.tree_id
    where tre.tree_id = '%s'
    """ % id
    cursor.execute(sql)
    row = cursor.fetchone()
    if version == 'TH':
        return {"id": id, "version": version, "name": row[0], "description": row[2]}
    elif version == 'EN':
        return {"id": id, "version": version, "name": row[1], "description": 'None'}

@app.get("/cu_tree_ll/")
def pg_cu_tree_ll():
    cursor = pg_conn()
    sql = """
    select gid, t.tree_id, survey_date, geohash, ST_AsGeoJSON( the_geom, 6) AS geojson,
    dbh, cirbh, total_h, verti_h, slop, stem_curve, bush_area, bush_thickness, url_image,
    name_id, name_t, name_e, genus, species, protection, royal_owner, condition, historical, address, plant_date, description, flowers, pods
    from tree t 
    left join tree_information tinf on t.tree_id = tinf.tree_id
    left join tree_inventory tinv on t.tree_id = tinv.tree_id
    where t.status = TRUE
    """
    cursor.execute(sql)
    
    # Retrieve the results of the query
    rows = cursor.fetchall()
    
    colnames = [desc[0] for desc in cursor.description]
    
    geomIndex = colnames.index("geojson")

    output = ""
    rowOutput = ""
    i = 0
    
    while i < len(rows):
        if rows[i][geomIndex] is not None:
            comma = "," if i > 0 else ""
            rowOutput =  comma + '{"type": "Feature", "geometry": ' + rows[i][geomIndex] + ', "properties": {'
            properties = ""
            
            j = 0
			
            while j < len(colnames):
                if colnames[j] != 'geometry':
                    comma = "," if j > 0 else ""
                    properties +=  comma + '"' + colnames[j] + '":"' + str(rows[i][j]) + '"'
                    
                j += 1
            
            rowOutput += properties + '}'
            rowOutput += '}'
            
            output += rowOutput
        
        # start over
        rowOutput = ""
        i += 1

        totalOutput = '{ "type": "FeatureCollection", "features": [ ' + output + ' ]}'
        
        dirfile = r'/home/sittinun/Webapps/cubigt/php/cu_tree_ll'

        with open(dirfile + '.geojson', 'w') as outfile:
            outfile.write(totalOutput)
