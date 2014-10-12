#! /usr/bin/env python

import sys
import gps
import time
import requests
import threading
import json
from operator import itemgetter

class GpsSender(threading.Thread):
    delay = 5

    def __init__(self):
	super(GpsSender, self).__init__()
	self.daemon = True
	self.buffer = []
	self.datalock = threading.Lock()
	self.site = server

    def send(self, data):
	ack = False
	try:
	    if self.datalock.acquire(False):
		ack = True
		for d in data:
		    self.buffer.append(d)

		self.buffer.sort(key=itemgetter('time'))
		return True

	finally:
	    if ack:
		self.datalock.release()

	return False

    def run(self):
	while True:
	    time.sleep(GpsSender.delay)
	    try:
		self.datalock.acquire()
		if len(self.buffer) > 0:
		    data = {'gpcoord-data' : json.dumps(self.buffer)}
		    requests.post(self.site, data, timeout=5)
		    del self.buffer[:]
		    print 'Data sent!'
	    except requests.exceptions.RequestException:
		print 'Can\'t send data!'
		print 'buffer len is' + str(len(self.buffer))
	    except StopIteration:
		print 'Sender finished!'
		del self.buffer[:]
		quit()
	    finally:
		self.datalock.release()

class GpsReportWorker(threading.Thread):

    def __init__(self):
	super(GpsReportWorker, self).__init__()
	self.daemon = True
	self.buffer = []
	self.counter = 0
	self.skipped = 3
	# Listen on port 2947 (gpsd) of localhost
	self.session = gps.gps("localhost", "2947")
	self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
	self.sender = GpsSender()
	print 'GpWorker initialized!'

    def run(self):
	self.sender.start()
	while self.sender.isAlive():
	    try:
		report = self.session.next()
		# Wait for a 'TPV' report and display the current time
		# To see all report data, uncomment the line below
		#print report
		if report is not None and report['class'] == 'TPV':
		    if hasattr(report, 'lon') and hasattr(report, 'lat') and hasattr(report, 'time') and hasattr(report, 'speed'):
			payload = {'time' : report.time, 'lat' : report.lat, 'lon' : report.lon, 'speed' : report.speed * gps.MPS_TO_KPH}
			print "Time: " + str(report.time)
			print "Lattitude: " + str(report.lat)
			print "Laongtitude: " + str(report.lon)
			print "Speed: " + str(report.speed * gps.MPS_TO_KPH)
			print '\n'
			print '...'
			self.counter = self.counter + 1
			if self.counter > self.skipped:
			    self.buffer.append(payload)
			    self.counter = 0
		# Try to send data in buffer and clear it on success!
		if self.sender.send(self.buffer):
		    print 'GpsReportWorker: buffer has %d items. Clearing ...' % len(self.buffer)
		    del self.buffer[:]
		else:
		    print 'Sender is busy (/\)'
		

	    except (SystemExit, KeyboardInterrupt):
		print 'Worker is gived up! Stopped.'
		self.sender = None
		self.session = None
		quit()

class GpsReport:
    delay = 15

    def __init__(self):
	self.worker = None

    def run(self):
	while True:
	    try: 
		if self.worker is None:
		    print "Worker is not running! Starting ..."
		    self.worker = GpsReportWorker()
		    self.worker.start()

		time.sleep(GpsReport.delay)

		if self.worker.isAlive():
		    print 'Collecting Gps Data ...'
		else:
		    print 'Gps Worker is Dead! :('
		    self.worker = None
	    except (SystemExit, KeyboardInterrupt, StopIteration):
		print "Terminating!"
		self.worker = None
		quit()


f = open('config.json')
config = json.load(f)
server = config["servers"][0]["server"]

print "Server: " + server

GpsReport = GpsReport()
GpsReport.run()