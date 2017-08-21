#!/usr/bin/env python


import time

with open('temp_logfile.log', 'a') as sparkfile:
	sparkfile.write('Connection to Spark Cloud Timed out {0}\n'.format(time.strftime("%c")))

