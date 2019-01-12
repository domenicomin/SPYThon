import paho.mqtt.client as PahoMQTT
import threading
import json
import time
import Adafruit_DHT as DHT # To control the temperature/humidity sensor
import RPi.GPIO as GPIO # To control the relay
import DeviceConnector

class MyRPi:
	def __init__(self, clientID, broker, port):
		self.broker = broker
		self.port = port
		self.clientID = clientID
		self._topic = ""
		self._isSubscriber = False
        self.devCon = DeviceConnector()
		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(clientID, False)

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessageReceived

		##GPIO.setmode(GPIO.BCM)
		##relay = 23 #is the relay pin
		##GPIO.setup(relay, GPIO.OUT)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.broker, rc))

	def myOnMessageReceived (self, paho_mqtt , userdata, msg):
		# A new message is received -> change relay status
		print (msg.topic, msg.payload)
        #payload deve essere un senml, nel campo "v" c'è il
        #valore atteso (1 acceso, 0 spento)
		msg_dict = json.loads(str(msg.payload))
        # mi arriva il json con il controllo se è 1 o 0
        if (msg.topic is str(self.broker)+"/Tcontrol"):
            devCon.Tcontrol(msg_dict)
        
        elif (msg.topic is str(self.broker)+"/Lcontrol"):
            devCon.Lcontrol(msg_dict)
		# Here I append to the dict "v", relative to the relay the field 
		# value to set the value of the relay
		


	def myPublish (self, topic, msg):
		# if needed, you can do some computation or error-check before publishing
		print ("publishing '%s' with topic '%s'" % (msg, topic))
		# publish a message with a certain topic
		self._paho_mqtt.publish(topic, msg, 2)

	def mySubscribe (self, topic):
		# if needed, you can do some computation or error-check before subscribing
		print ("subscribing to %s" % (topic))
		# subscribe for a topic
		self._paho_mqtt.subscribe(topic, 2)
		# just to remember that it works also as a subscriber
		self._isSubscriber = True
		self._topic = topic

	def start(self):
		#manage connection to broker
		self._paho_mqtt.connect(self.broker , self.port)
		self._paho_mqtt.loop_start()

	def stop (self):
		if (self._isSubscriber):
			# remember to unsuscribe if it is working also as subscriber
			self._paho_mqtt.unsubscribe(self._topic)
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

### THREADS ###


### ricorda di controllare i tempi
class Temp(threading.Thread):  
	def __init__(self,pub,devCon):
		threading.Thread.__init__(self)
        self.pub = pub
        self.devCon = devCon
 	def run(self):
 		while True:
            senml_temp = self.devCon.temperature()
			self.pub.myPublish(str(self.pub.broker)+'/temp', senml_temp)
 			time.sleep(15)

class Hum(threading.Thread):
 	def __init__(self,pub, devCon):
 		threading.Thread.__init__(self)
         self.pub = pub
         self.devCon = devCon
 	def run(self):
 		while True:
            senml_hum = self.devCon.humidity()
			self.pub.myPublish(str(self.pub.broker)+'/hum', senml_hum)
 			time.sleep(30)

		
class Light(threading.thread):
	def __init__(self,pub,devCon):
		threading.Thread.__init__(self)
        self.pub = pub
        self.devCon = devCon
	def run(self):
		while True: 
            fakeLight = self.devCon.light_status()
			self.pub.myPublish(str(self.pub.broker)+'/light', fakeLight)
            time.sleep(45)
class Lock():
 	def __init__(self,pub,devCon):
 		threading.Thread.__init__(self)
         self.pub = pub
         self.devCon = devCon
 	def run(self):
 		while True:
            lockStatus = self.devCon.lock_status()
			self.pub.myPublish(str(self.pub.broker)+'/lock', lockStatus)
 			time.sleep(60)

if __name__ == "__main__":
    devCon = DeviceConnector()
    #qui come broker devo ottener l'ip del broker
	test = MyRPi('RPi', 'iot.eclipse.org', 1883)
	test.start()

	temp = Temp(test,devCon)
	hum = Hum(test,devCon)
	light_status = Light(test,devCon)
    lock_status = Lock(test,devCon)


	temp.start()
	hum.start()
	motion.start()

	test.mySubscribe(test.broker+'/Tcontrol')
    test.mySubscribe(test.broker+'/Lcontrol')

	while True:
		pass

	test.stop()


    #