import requests
import cherrypy
import json

import time


from DeviceConnector import *


#POSSIBILITIES   REST-ful
# localhost:8080/temperature
# localhost:8080/humidity      <-- oltre a mandare hum, ti informo con {h:val, alert:boolean}
# localhost:8080/lock_status   
# localhost:8080/light_status  <-- fake 
# localhost:8080/photo         <-- fake (3 foto)




# RICORDA : fai la init dove comunichi al caltalogue il mio ip
# id_device :"ID", IP,GET [temperature, humidity, loc,..], POST [],lista topic [] 
 
 
 

class REST_DeviceConnector:
    exposed = True

    def __init__(self):
	self.deviceconnector = DeviceConnector () 
	
	def GET (self, *uri):
				
		if (uri[0] == 'temperature'):
			
			
			senml = self.deviceconnector.temperature()
		
			if senml is None:
					raise cherrypy.HTTPError(500, "Invalid Senml")
					
			value = ((senml['e'])[0])['v'] 
			
			if isinstance(value, basestring):			
				raise cherrypy.HTTPError(500, "Error in reading data from sensor")	
			
			else: 
				out = json.dumps(senml)
		
		
		
		elif (uri [0] == 'humidity'):		
		
			senml = self.deviceconnector.humidity()
		
			if senml is None:
				raise cherrypy.HTTPError(500, "Invalid Senml")

				
			value = ((senml['e'])[0])['v'] 
			
			
			if isinstance(value, basestring):
				raise cherrypy.HTTPError(500, "Error in reading data from sensor")
				
			else: 
				out = json.loads(senml)
	
	
	
		elif (uri [0] == 'lock_status'):
			
			senml = self.deviceconnector.lock_status()
		
			
			if senml is None:
				raise cherrypy.HTTPError(500, "Invalid Senml")
				
			else: 
				out = json.loads(senml)
			
		elif (uri [0] == 'light_status'):
			
			senml = self.deviceconnector.light_status()
		
			
			if senml is None:			
				raise cherrypy.HTTPError(500, "Invalid Senml")
				
			else: 
				out = json.loads(senml)
		
		elif (uri[0] not in self.deviceconnector.get):
			raise cherrypy.HTTPError(500, "The parameter inserted does not support any action")
						
	return out	
	print out
		

			
			
			
			# Pub-Sub	
	
# Pub --> brokerip/temp
# Pub --> brokerip/hum

# Pub --> brokerip/light

# Sub ..> brokerip/Tcontrol
# Sub ..> brokerip/Lcontrol
# Sub ..> brokerip/Halert
	

		
		                                       #Quando metterlo Cherrypy  ?
			
if __name__ == '__main__':
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}
	cherrypy.tree.mount(REST_DeviceConnector(), '/', conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': 8080})
	cherrypy.engine.start()
	cherrypy.engine.block()
# #non mettere cherrypi block, altrimenti non compila dopo

	
	
	


