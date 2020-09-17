import subprocess, time
from lib.GPIOSetup import GPIO
from lib.setup import states, settings

class Appliance:

	def __init__(self, attributes):
		self.attributes = attributes
		self.name = attributes['Name']
		self.type = attributes['Type']
		if self.type == 'GPIO':
			self.pin = attributes['Pin']
			self.active = attributes['ActiveState']
		if self.type == 'Script' or self.type == 'RF':
			if 'Timeout' in attributes:
				self.timeout = "timeout "+str(attributes['Timeout'])+" "
			else:
				self.timeout = "timeout 0.2 "
			if self.type == 'Script':
				self.status_cmd = self.timeout + attributes['Status']
			if self.type == 'RF':
				if self.name not in states:
					self.state = attributes['Ostate']
				else:
					self.state = states[self.name]
			if 'Action' in attributes:
				self.action = True
				self.on_cmd = attributes['Action'][True]
				self.off_cmd = attributes['Action'][False]
			else:
				self.action = False

	def getState(self):
		if self.type == 'GPIO':
			if GPIO.input(self.pin) is self.active:
				return 1
			else:
				return 0
		elif self.type == 'RF':
			return self.state
		else:
			#get the state of other Appliances in other rooms
			#not properly implemented yet
			returnCode = subprocess.call([self.status_cmd], shell=True)
			if returnCode == 0:
				return 1
			return 0

	def setState(self, state):
		if self.type == 'GPIO':
			if state > 1:
				original_state= GPIO.input(self.pin)
				new_state = 1 - original_state
			else:
				new_state = 1 - self.active - state
			GPIO.output(self.pin, new_state)
			if GPIO.input(self.pin) is self.active:
				return 1
			else:
				return 0
		elif self.type == 'RF':
			self.state = state
			return 1

	def executeAction(self):
		if self.type == 'GPIO':
			original_state= GPIO.input(self.pin)
			new_state = 1 - original_state
			GPIO.output(self.pin, new_state)
			if 'Duration' in self.attributes:
				time.sleep(self.attributes['Duration'])
				GPIO.output(self.pin, original_state)
		if (self.type == 'Script' or self.type == 'RF') and self.action:
			if self.getState():
				subprocess.call([self.off_cmd], shell=True)
			else:
				subprocess.call([self.on_cmd], shell=True)
			if self.type == 'RF':
				self.state = abs(1 - self.state)
				states[self.name] = self.state
				print('{} is {}'.format(self.name, self.state))
	
	def saveState(self):
		if self.type == 'RF':
			states[self.name] = self.state
			