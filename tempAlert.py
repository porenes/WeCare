import serial
import RPi.GPIO as GPIO
import urllib
import time

onOffPin = 4	# Button pin
ackPin = 22		# 
hotPin = 17		# Hot LED pin
coldPin = 18	# Cold LED pin

pid = 6971412647303446012 # Bonita Process ID
server_root = 'http://192.168.1.196:8080/bonita' # Bonita server root

triggerVal = 25 # Temp to alert
tempoDelay = 30 # Delay between alerts
alarmDelay = 10 # Warning delay between alarm

tempo = 60

GPIO.setmode(GPIO.BCM)
GPIO.setup(coldPin, GPIO.OUT)
GPIO.setup(hotPin, GPIO.OUT)
GPIO.setup(onOffPin, GPIO.IN)
GPIO.output(coldPin, False)
GPIO.output(hotPin, False)

def startCase(temp) :
	import urllib
	import urllib2
	import json
	from urllib2 import Request, urlopen, URLError

	print "starting case with temp : "+str(temp)
	try :
		urlAuth = server_root+'/loginservice'
		valuesAuth = {'username' : 'walter.bates',
	   	       'password' : 'bpm',
	   	       'redirect' : 'false' }
		data = urllib.urlencode(valuesAuth)
		req = urllib2.Request(urlAuth, data) 
		response = urllib2.urlopen(req)
		cookie = response.info()['Set-Cookie']
		url = server_root+'/API/bpm/case'
		headers = {'Cookie' : cookie,
		           'Content-Type': 'application/json;charset=UTF-8'}
		valuesStart = {'processDefinitionId' : str(pid),
						'variables' : [ {'name': 'temperature' , 'value' : str(temp)}] }
						
		dataStart = json.dumps(valuesStart)
		print "Sending data : "+dataStart
		req = urllib2.Request(url, dataStart , headers)
		req.add_header("Cookie",cookie)
		response = urllib2.urlopen(req)
		the_page = response.read()
		print the_page
	except URLError, e:
		print e.reason

def readCases() :
	import urllib
	import urllib2
	import json
	from urllib2 import Request, urlopen, URLError

	try :
		urlAuth = server_root+'/loginservice'
		valuesAuth = {'username' : 'walter.bates',
	   	       'password' : 'bpm',
	   	       'redirect' : 'false' }
		data = urllib.urlencode(valuesAuth)
		req = urllib2.Request(urlAuth, data) 
		response = urllib2.urlopen(req)
		cookie = response.info()['Set-Cookie']
		url = server_root+'/API/bpm/process/'+str(pid)
		req = urllib2.Request(url)
		req.add_header("Cookie",cookie)
		response = urllib2.urlopen(req)
		the_page = response.read()
		print the_page
	except URLError, e:
		print e.reason


def hot() :
	GPIO.output(hotPin, True)
	GPIO.output(coldPin, False)	

def cold() :
	GPIO.output(coldPin, True)
	GPIO.output(hotPin, False)	

def off() :
	GPIO.output(coldPin, False)
	GPIO.output(hotPin, False)	

ser = serial.Serial('/dev/ttyACM0',9600)

alert = 0
warning = 0
on = False
while True:
	# readCases()
	if (GPIO.input(onOffPin)) :
		print("Button Pressed")
		on = not on
		if (on) : cold()
		else : off()
	if (on):	
		temp = float(ser.readline())
		# Remove serial read error
		if (temp < 100) :
			tempo = tempo + 1
			if ( (temp > triggerVal)  ) :
		
				if ((tempo > tempoDelay) & (alert == 0) ) : 
					warning = warning + 1
					print "Warning : Alarm in "+str(alarmDelay-warning)+" seconds"
					if (warning >= alarmDelay) :
						startCase(temp)
						alert = 1
				hot()
			if ( (temp < triggerVal) ) :
				warning = 0
				if (alert == 1) :
					alert = 0
					tempo = 0

				cold()
			print("T : "+str(temp)+" - Alert : "+str(alert)+" - temporisation : "+str(tempo))
	time.sleep(1)

