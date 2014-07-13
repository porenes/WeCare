import RPi.GPIO as GPIO
import time
import sys,getopt

GPIO.setmode(GPIO.BCM)
 
ack_pin = 22 #le bouton
buzzer_pin = 27 #le buzzer 

pid = 6971412647303446012 # Bonita Process ID
server_root = 'http://192.168.1.196:8080/bonita' # Bonita server root

def put(url, values, headers, cookie) :
	import urllib
	import urllib2
	import json
	from urllib2 import Request, urlopen, URLError
	
	print "put : "+url						
	data = json.dumps(values)
	req = urllib2.Request(url, data , headers)
	req.add_header("Cookie",cookie)
	req.get_method = lambda: 'PUT'
	response = urllib2.urlopen(req)
	print response.getcode()

def doTask(tid) :
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
		headers = {'Cookie' : cookie,
		           'Content-Type': 'application/json;charset=UTF-8'}
		print "Assigning task"+str(tid)
		url = server_root+'/API/bpm/humanTask/'+str(tid)
		values = {'assigned_id' : '4'}
		put(url, values, headers, cookie)
		print "Doing task : "+str(tid)
		url = server_root+'/API/bpm/activity/'+str(tid)
		values = {'state' : 'completed'}
		put(url, values, headers, cookie)

	except URLError, e:
		print e.reason

 
GPIO.setup(ack_pin, GPIO.IN) 
GPIO.setup(buzzer_pin, GPIO.OUT) 


print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)
try :
	opts, args = getopt.getopt(sys.argv[1:],"t:")
except getopt.GetoptError:
	print 'alarm.py -t <task>'
	sys.exit(2)
for opt, arg in opts:
	if opt in ("-t"):
		tid = arg
		print "tid : "+str(tid)
while True :
	GPIO.output(buzzer_pin, True)
	time.sleep(0.1)
	GPIO.output(buzzer_pin, False)
	time.sleep(0.5)
	if (GPIO.input(ack_pin)) :
		print("STOP task:"+str(tid))
		doTask(str(tid))
		GPIO.output(buzzer_pin, False)
		GPIO.cleanup()
		break

	