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
from decimal import *
import xml.etree.cElementTree as ET
import time


tempThreshold = Decimal('76.3')

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
	room_id = 'Y2lzY29zcGFyazovL3VzL1JPT00vYmUyOTRkNDAtODU1ZC0xMWU3LWE4ODUtYjllNDU4OWVmYWNl'
	# TechX Team Space ID
	techx_space_id = 'Y2lzY29zcGFyazovL3VzL1JPT00vZWM2YzY3MzAtZDU1Mi0xMWU1LTg3ZDQtOWRiZjdlM2FkNGUx'

	# temperature bot's login secret
	temp_bot_spark_client_secret = 'OTkwZTliMDgtMDhkYy00MTdjLWFmMDQtYWRiYzU3Mzc4YmI0NmMxY2MyYzEtYWQ4'
	
	# Spark Message header and URI declaration
	full_uri = spark_api_base_uri + spark_messages_suffix
	spark_headers = {"content-type": "application/json; charset=utf-8",
					  "Authorization" : "Bearer {0}".format(temp_bot_spark_client_secret)
					}

	# Assign list elements returned from sensor REST call, 
	#error message and temperature to variables
	#currentTemp1 is from sensor 1
	currentTemp1 = Decimal(info[0])
	message1 = info[1]
	print currentTemp1
	#currentTemp2 is from sensor 2
	currentTemp2 = Decimal(info[2])
	message2 = info[3]
	print currentTemp2

	# Check to see if an error occured in temp sensor check
	if message1 and message2 == 'no error':
		#tempThreshold declared at top of script for ease of access
		if currentTemp1 >= tempThreshold or currentTemp2 >= tempThreshold:
			sparkMessage = 'RFL overheating current temp Sensor1: {0}F - Sensor2: {1}F'.format(currentTemp1, currentTemp2)
			params = {
					  "roomId" : room_id,
					  "text" : sparkMessage
					}
			# Make Restful Spark Call sending temperature if over threshold
			try:
				print 'making call to Spark'
				r = requests.post(full_uri, json.dumps(params), headers=spark_headers)
			except requests.exceptions.Timeout:
				# Except connection time out to Spark Cloud, write log
				error_mess ('Connection to Spark Cloud Timed out')
				log_file('error_mess')
					

		else:
			print 'Temp within acceptable range'
	else:
		#Send error message, as it did not match 'no error' string
		sparkMessage = message1 + '' + message2
		params = {
		  "roomId" : room_id,
		  "text" : sparkMessage
		}
		# Make Restful Spark Call
		r = requests.post(full_uri, json.dumps(params), headers=spark_headers)
		try:
			print 'making call to Spark'
			r = requests.post(full_uri, json.dumps(params), headers=spark_headers)
		except requests.exceptions.Timeout:
			# Except connection time out to Spark Cloud, write log
			error_mess ('Connection to Spark Cloud Timed out')
			log_file('error_mess')
					

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

	try:
		r = requests.get(url, headers=temp_sens_headers)
		#p.pprint(r.text)
	except requests.exceptions.Timeout as err:
		# Deal with timeout to temp sensor
		error_mess =  'Temp Sensor timed out {0}'.format(err)
		log_file(error_mess)
	except requests.exceptions.ConnectionError as err:
		# catch connection error to sensor
		error_mess =  'Temp Sensor Connection Error {0}'.format(err)
		log_file(error_mess)

	root = ET.fromstring(r.content)


	for node1 in root.iter('devices'):
		deviceIDLocate1 = node1[0].attrib
		deviceID1 = deviceIDLocate1['id']
		if deviceID1 == '01EEE5F918000082':
			print 'Correct device ID, getting temperature'
			message1 = 'no error'
		else:
			message1 = 'Device not in original XML location, please check parsing'


		tempInfo1 = node1[0][1].attrib
		currentTemp1 = tempInfo1['value']


	for node2 in root.iter('devices'):
		deviceIDLocate2 = node2[1].attrib
		deviceID2 = deviceIDLocate2['id']
		if deviceID2 == 'D10000086566D628':
			print 'Correct device ID, getting temperature'
			message2 = 'no error'
		else:
			message2 = 'Device not in original XML location, please check parsing'

		tempInfo2 = node2[1][1].attrib
		currentTemp2 = tempInfo2['value']

	return [currentTemp1, message1, currentTemp2, message2]

def log_file(error_mess):

	''' 
		Write any errors to a file 
		Error Messages may be: 
			- Spark connection errors,
			- Temperature Sensor timeout, connection error
			- Overheating log time and date

	'''
	# Open file and append error message from passing definition
	with open('temp_logfile.log', 'a') as sparkfile:
		sparkfile.write('{0}: {1} \n'.format(error_mess, time.strftime("%c")))

	# Terminate script for another attempt
	quit()

if __name__ == "__main__":


	info = get_temp()
	print info
	send_mess_to_spark(info)

