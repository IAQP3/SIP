from bluepy.btle import Scanner, DefaultDelegate, UUID, Peripheral, BTLEException
import time
import struct
import sys
import os
import datetime
from threading import Thread
import RPi.GPIO as GPIO
import logging
from cloudpost import *

py_path=os.path.dirname(os.path.realpath(__file__))


#LOGGING
logging.basicConfig(level=logging.DEBUG)
file_logger = logging.getLogger('main')

file_handler = logging.FileHandler(py_path+'/logs/crash.log')
file_logger.addHandler(file_handler) 
file_logger.setLevel(logging.WARNING)


recognizedServices = dict()
BLE_SERVICE_ENVIRONMENT = "0000181a-0000-1000-8000-00805f9b34fb"

settings_path = py_path+"/settings.xml"

def load_recognized_characteristics():
    parsed_file = xml.etree.ElementTree.parse(settings_path).getroot()
    uuid_root = parsed_file.find('uuids')
    chars = []
    for atype in uuid_root.findall('uuid'):
        chars.append(atype.find('name').text)
    logging.debug("Parsed UUIDs: {}\n".format(chars))
    recognizedServices[BLE_SERVICE_ENVIRONMENT] = chars
	


class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, device, isNewDev, isNewData):
		if isNewDev:
			logging.info("Discovered device: {}".format(device.addr))
		elif isNewData:
			logging.info("Received new data from: {}".format(device.addr))
 
 
class MyDelegate(DefaultDelegate):
	def __init__(self,params):
		DefaultDelegate.__init__(self)
		self.peripheral = params

def printAdvertisingInformation(device):
	for (adtype, desc, value) in device.getScanData():
		logging.info("{}: {}".format(desc, value)) 
	logging.info("Address: {}".format(device.addr))
	logging.info("AddressType: {}".format(device.addrType))
	logging.info("Interfacenumber: {}".format(device.iface))
	logging.info("Signal strength: {}".format(device.rssi))
	logging.info("Device is connectable: {}".format(device.connectable))
	logging.info("Number of recieved packets: {}".format(device.updateCount))
	return True

def printDeviceNames(devices):
	logging.info("\n\nList of found device names:\n*****************************")
	for dev in devices:
		#logging.info("Device {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
		#print ("Description: {}".format(dev.getDescription(9)))
		for (adtype, desc, value) in dev.getScanData():
			if (desc == "Complete Local Name"):
				logging.info("Device name: {}".format(value))

			
			
def scanForDevices():
	scanner = Scanner().withDelegate(DefaultDelegate())#ScanDelegate())
	devices = scanner.scan(4.0)
	return devices;

def scanIAQDevices():
	iaq_devices = [];
	devices = scanForDevices()
	for dev in devices:
		for (adtype, desc, value) in dev.getScanData():
			if (desc == "Complete Local Name"):
				if "IAQ" in value:
					iaq_devices.append(dev);
					logging.info("  -{} \t({}) \tRSSI={} dB".format(value, dev.addr, dev.rssi))

	return iaq_devices

	
def preparePeripheral(device):
	#Create the peripheral object from bluetooth device
	peripheral = Peripheral(device)
	peripheral.setDelegate(MyDelegate(peripheral))
	Peripheral.availableChararacteristics = []
	time.sleep(2)
	
	
	#Read all device characteristics and add make a list of recognized characteristics
	services = peripheral.getServices()
	
	for ser in services:
		if ser.uuid == BLE_SERVICE_ENVIRONMENT:
			logging.debug("  Found recognized service: {}".format(ser.uuid.getCommonName()))
			serChar = ser.getCharacteristics()
			for char in serChar:
				if char.uuid in recognizedServices[str(ser.uuid)]:
					logging.debug("   Added characteristics: {}".format(char.uuid.getCommonName()))
					peripheral.availableChararacteristics.append(char)
				else:
					logging.debug("   (Unused characteristics: {})".format(char.uuid.getCommonName()))
					
	return peripheral

def readCharacteristics(peripheral):
	read_buffer=[]
	
	for char in peripheral.availableChararacteristics:
		for uuids in peripheral.channel.supportedUUIDS:
			if uuids['name'] == char.uuid:
				sensor 		= uuids['sensor']
				data_type 	= uuids['data_type']
				factor 		= uuids['factor']
				unit 			= uuids['unit']
				field 			= uuids['field']
		try:
			read_data=char.read()
			value = factor*struct.unpack(data_type, read_data)[0]
			read_buffer.append({'field': str(field), 'value': value})
			
		except:
			logging.exception("Read of value {} failed.".format(sensor))
		
		logging.debug("  -{}:\t{} {} \t Raw: {}".format(sensor, value, unit, read_data))
	
	return read_buffer

'''
#Threaded blinking
class blink_led(Thread):
	def __init__(self, count, delay):
		Thread.__init__(self)
		self.setDaemon(True)
		self._count=count
		self._delay=delay
		self.start()
		
	def run(self):
		for _ in range(0,self._count*2):
			input_state=GPIO.input(18)
			GPIO.output(18, 1-input_state)
			time.sleep(self._delay)
'''		
	
class Led():
	def __init__(self, pin):
		self._pin=pin
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self._pin, GPIO.OUT)
		GPIO.output(self._pin, 0)
		#self._thread=Thread(target=self._blink)
	
	def blink(self, count, delay):
		for _ in range(0,count*2):
			input_state=GPIO.input(self._pin)
			GPIO.output(self._pin, 1-input_state)
			time.sleep(delay)
			
		
def main():
	load_recognized_characteristics()
	cloud = CloudPost()
	cloud.get_channel_information()
	
	while True:
		# Scan for devices until found
		devices = []
		logging.info("Scanning for devices")
		while not len(devices):
			devices = scanIAQDevices()
		
		# Read all connected devices characteristics
		# Add them to a buffer and post to the cloud
		
		for device in devices:
			try:
				peripheral = preparePeripheral(device)
			except:
				logging.exception("Failed to prepare peripheral")
				break
			
			logging.info("Peripheral address: {}".format(peripheral.addr.upper()))
			
			if peripheral.addr.upper() in cloud.channels.keys():
				peripheral.channel = cloud.channels[peripheral.addr.upper()]
			else:
				peripheral.channel = cloud.create_channel(peripheral.addr.upper())
			
			time.sleep(2);#Wait for the peripheral to write all measurements
			
			send_data=readCharacteristics(peripheral)
			peripheral.channel.post(send_data)
			peripheral.disconnect()
		
		logging.info("Time: {}\n".format(datetime.datetime.now()))
		time.sleep(60)


if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		file_logger.error("Python crashed. Error: %s", e)

	
	
	
	
	
	
	
	
	
	
	