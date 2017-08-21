#!/usr/bin/env python

''' 
	Script to interact with Spark API sending information from our
	temperature sensor to a spark room.

	Updates needed: 
	1. Search for Sensor by ID, then pull Temp
	2. Check for REST state errors and report if device is unreachable
	3. Report if Spark becomes unreachable

'''

__version__ = 1.0

import json
import requests
import pprint as p
import xml.etree.cElementTree as ET


tempThreshold = 77.0

def send_mess_to_spark(info):

	''' 
	Send either the current temp or an error message to spark room

	'''

	# Spark room info and login token declaration
	# Base URI for Spark call
	spark_api_base_uri = 'https://api.ciscospark.com/'
	# Spark Messages suffix for REST API
	spark_messages_suffix = 'v1/messages'
	# Script Testing ROOM ID
	room_id = ''
	# TechX Team Space ID
	techx_space_id = ''

	# temperature bot's login secret - removed for sec
	temp_bot_spark_client_secret = ''
	
	# Spark Message header and URI declaration
	full_uri = spark_api_base_uri + spark_messages_suffix
	spark_headers = {"content-type": "application/json; charset=utf-8",
					  "Authorization" : "Bearer {0}".format(temp_bot_spark_client_secret)
					}

	# Assign list elements returned from sensor REST call, 
	#error message and temperature to variables
	currentTemp = float(info[0])
	message = info[1]

	# Check to see if an error occured in temp sensor check
	if message == 'no error':
		#tempThreshold declared at top of script for ease of access
		if currentTemp >= tempThreshold or :
			sparkMessage = 'RFL overheating current temp {0}'.format(currentTemp)
			params = {
					  "roomId" : room_id,
					  "text" : sparkMessage
					}
			# Make Restful Spark Call sending temperature if over threshold
			r = requests.post(full_uri, json.dumps(params), headers=spark_headers)

		else:
			print 'Temp within acceptable range'
	else:
		#Send error message, as if did not match no error string
		sparkMessage = message
		params = {
		  "roomId" : room_id,
		  "text" : sparkMessage
		}
		# Make Restful Spark Call
		r = requests.post(full_uri, json.dumps(params), headers=spark_headers)


def get_temp():

	''' 

		Get Temperature from Temp sensor 

		current limitation of this code is that the XML parsing does not
		check for the device and then locate temperature. It relies on a pre-defined
		location in the XML script. An error will be sent to Spark if the sensor
		is not found i.e. it has been removed, or a new sensor was added displacing
		it in the XML schema.

	'''

	temp_sensor1 = '128.107.225.245'

	temp_sens_headers = {'content-type': 'application/xml; charset=utf-8'}
	url = 'http://' + temp_sensor1 + '/data.xml'

	r = requests.get(url, headers=temp_sens_headers)
	#p.pprint(r.text)

	root = ET.fromstring(r.content)

	# Parse XML from temp sensor, look for ID, then get current temp

	for node in root.iter('devices'):
		deviceIDLocate = node[1].attrib
		deviceID = deviceIDLocate['id']
		if deviceID == 'D10000086566D628':
			print 'Correct device ID, getting temperature'
			message = 'no error'
		else:
			message = 'Device not in original XML location, please check parsing'


		tempInfo = node[1][1].attrib
		currentTemp = tempInfo['value']

	return [currentTemp, message]


if __name__ == "__main__":


	info = get_temp()
	print(info)
	#send_mess_to_spark(info)

