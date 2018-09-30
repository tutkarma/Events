#!/usr/bin/env python
import _mysql
import json
import cgi
from datetime import datetime

db = _mysql.connect(host="localhost",user="root", passwd="1", db="eden")
db.query("SET NAMES utf8;")


def insertEvent(eventid, title, dates, description, latitude, longitude):
	#insert event in database
	db.query("""INSERT INTO events (eventid, title, dates, description, coords)
	VALUES
	("{0}",  "{1}",  "{2}", "{3}", GeomFromText('POINT({4} {5})') );
	""".format(eventid, title, dates, description, latitude, longitude)
	)


def getLocalEvents(latitude, longitude, radius):
	#get all events within raduis of provided point
	db.query("""
	SELECT 
	  eventid, title, dates, description,
	  X(coords) AS "latitude",
	  Y(coords) AS "longitude",
	  GLength(
	      LineStringFromWKB(LineString(coords, GeomFromText('POINT({0} {1})')))
	      )*111300
	  
	  
	  AS distance
	FROM events
	HAVING distance < {2}
	ORDER BY distance ASC;
	""".format(latitude,longitude,radius)
	)
	#distance returns answer in degrees of longtitude so neede to multply by 111.3 or km or by 111300 for m
	res = db.store_result()
	eventsList = []
	for line in res.fetch_row(maxrows=0):
		dates = json.loads('{"dates" :'+line[2].decode('utf-8').replace("'",'"')+'}')
		datestart = datetime.utcfromtimestamp(dates["dates"][0]["start"]).strftime('%H:%M %d.%m.%Y')
		dateend   = datetime.utcfromtimestamp(dates["dates"][0]["end"]).strftime('%H:%M %d.%m.%Y')
		eventsList.append(
			{
				"id" : line[0],                 #id
				"title ": line[1].decode('utf-8'), #title
				"datestart" : datestart, #dates
				"dateend" : dateend,
				"description" : line[3].decode('utf-8'),  #descr
				"lat" : line[4],  		# x
				"lon" : line[5],        #y
				"distance" : line[6]                  #distance
			}
		)
		
	return eventsList


def dropDB():
	db.query("""DROP TABLE events;""")
	db.query("SET NAMES utf8;")
	db.query("""CREATE TABLE events (eventid VARCHAR(255), title VARCHAR(255), dates TEXT, description TEXT, coords GEOMETRY) DEFAULT CHARSET=utf8;""")

def initDB ():
	db.query("SET NAMES utf8;")
	parsed_json = ""
	with open('data_maps.json', 'r', encoding='utf8') as f:
	    parsed_json = json.loads(f.read())

	for event in parsed_json["events"]["results"]:
		if event["coords"]["lat"] == 0:
			#events without stated place will not show up on the map
			pass
		else:
			insertEvent(event["id"], 
			#escape special symbols like quotes and so on
			cgi.escape(event["title"], quote=True),
			event["dates"], 
			cgi.escape(event["description"], quote=True),
			event["coords"]["lat"], 
			event["coords"]["lon"])

