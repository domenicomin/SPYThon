import json
import RPi.GPIO as GPIO
import time
import Adafruit_DHT 

import urllib #leggere ip

from plugwise import *

import matplotlib.image as mpimg


#POSSIBILITIES   REST-ful
# localhost:8080/temperature
# localhost:8080/humidity      <-- oltre a mandare hum, ti informo con {h:val, alert:boolean}
# localhost:8080/lock_status   
# localhost:8080/light_status  <-- fake 
# localhost:8080/photo         <-- fake (3 foto)



# RICORDA : fai la init dove comunichi al caltalogue il mio ip
# id_device :"ID", IP,GET [temperature, humidity, loc,..], POST [],lista topic [] 


	

# Pub-Sub	
	
# Pub --> brokerip/temp
# Pub --> brokerip/hum

# Pub --> brokerip/light

# Sub ..> brokerip/Tcontrol
# Sub ..> brokerip/Lcontrol
# Sub ..> brokerip/Halert


class DeviceConnector:
	exposed = True
			
	def __init__(self):

	
		#IP READING
		data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
		self.ip= data["ip"]

		#LOCK PIN
		self.pin_lock=26
		
		#LIGHT PIN (emulated with wire)
		self.pin_light=5
		
		#DHT22 (T & H sensor)
		self.pin_dht=18
		self.dht_sensor=22   			#tipo dht22									
		
		#GPIO
                GPIO.setmode(GPIO.BCM)	 # the pin numbers refer to the board connector not the chip
		GPIO.setup(self.pin_light, GPIO.IN) # set up pin ?? (one of the above listed pins) as an input with a pull-up resistor

		self.pin_rele1 = 12 #settalo bene
		
		#SMART PLUG
		self.mac1 = "000D6F0005670E36"
		self.mac2 = "000D6F0004B1E48D"
		self.usbport = "/dev/ttyUSB0"   # in alto a destra 
		
		#ALERT
		self.humidityalert = 0 #alert off
		
		#DEVICE registration
		self.deviceID = "raspberry_dom"
		self.get = ["temperature", "humidity", "lock_status","light_status", "photo"]    
		self.sub_topics = ["Tcontrol", "Lcontrol", "Halert"]
		self.pub_topics = ["temperature", "humidity","light_status","lock_status"]
		self.resources = ["temperature", "humidity", "lock_status","light_status", "photo", "Tcontrol", "Lcontrol"]
		
		#camera
		self.image_path= "/home/pi/Pictures/image1.jpeg"
		
	def register(self):
		
		device['ID']= self.deviceID   #check
		device['IP'] = self.ip
		device['GET'] = self.get            #RESTful services
		#device['POST'] = data['POST']                     #per la foto ????
		device['sub_topics'] = self.sub_topics
		device['pub_topics'] = self.pub_topics
		device['resources'] = self.resources
		
	def temperature (self):  #vedi se nel senml posso cambiare formato da in caso di errore
	
		humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, self.pin_dht)
		
		if temperature is not None:
		
			T_senml = {'bn': "http://" + self.ip + '/Tsensor/', 'e': [{ "n": "temperature", "u": "Cel","t": time.time(), "v": float('{0:0.1f}' .format(temperature)) }]}
		else:	
			T_senml = {'bn': "http://" + self.ip + '/Tsensor/', 'e': [{ "n": "temperature", "u": "Cel","t": time.time(), "v": "Error in reading"}]}
		
		print T_senml
		return T_senml
	
	def humidity (self):
	
		humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, self.pin_dht)
		
		if humidity is not None:
		
			H_senml= {'bn': "http://" + self.ip + '/Hsensor/', 'e': [{ "n": "humidity", "u": "%","t": time.time(), "v": float('{0:0.1f}' .format(humidity))}]}
		else:	
			H_senml= {'bn': "http://" + self.ip + '/Hsensor/', 'e': [{ "n": "humidity", "u": "%","t": time.time(), "v": "Error in reading"}]}
		
		print H_senml
		return H_senml

	def lock_status(self):
                GPIO.setup(self.pin_lock, GPIO.IN)
	
                
		if GPIO.input(self.pin_lock) == True :
		
			Lock_senml= {'bn': "http://" + self.ip + '/Lock_sensor/', 'e': [{ "n": "lock_status", "u": "state","t": time.time(), "v": "closed"}]}
		else:	
			Lock_senml= {'bn': "http://" + self.ip + '/Lock_sensor/', 'e': [{ "n": "lock_status", "u": "state","t": time.time(), "v": "open"}]}
		
		
		GPIO.cleanup(self.pin_lock)
		print Lock_senml
		return Lock_senml
		
	def light_status(self):
            
                GPIO.setup(self.pin_light, GPIO.IN)


		if GPIO.input(self.pin_light) == True :
		
			Light_senml= {'bn': "http://" + self.ip + '/Light_sensor/', 'e': [{ "n": "light_status", "u": "state","t": time.time(), "v": "ON"}]}
		else:	
			Light_senml= {'bn': "http://" + self.ip + '/Light_sensor/', 'e': [{ "n": "light_status", "u": "state","t": time.time(), "v": "OFF"}]}
		
		GPIO.cleanup(self.pin_light)
		print Light_senml
		return Light_senml
		
	def photo(self):
		
		img = mpimg.imread(self.image_path)
		
		return img 
		
		
	# conoscendo ip le prendi da raspberry
	# carico su sito online
	# mando link a cazzo 
	
	def Tcontrol(self, Heater_senml):
		
		GPIO.setup(self.pin_rele1, GPIO.OUT)

		# Heater_senml = {'bn': self.ip + '/Heater_status/',
		#		'e': [{ "n": "Heater_status", "u": None,
		#		"t": time.time(), "v": 1}]}                  or 0
		
		control = ((Heater_senml['e'])[0])['v'] 
		
		if control == 1 :
			
			GPIO.output(self.pin_rele1, GPIO.HIGH)
			
		else: 
			
			GPIO.output(self.pin_rele1, GPIO.LOW)
			
			
	def Lcontrol(self, Lamp_senml):
	
		# Lamp_senml = {'bn': self.ip + '/Lamp_status/',
		#		'e': [{ "n": "Lamp_status", "u": None,
		#		"t": time.time(), "v": 1}]}                  or 0
		
		control = ((Lamp_senml['e'])[0])['v'] 
		
		s = Stick(port=self.usbport)
	
		c1,c2 = Circle(self.mac1,s) , Circle(self.mac2,s)
		
		if control == 1:
			
			c1.switch_on()

		else: 

			c1.switch_off()
			
			
	def Halert (self, alert):
	
	    #Halert_json = {"v": 1}                  or 0
	
		 self.humidityalert = alert['v']
		 
		 
	
 

