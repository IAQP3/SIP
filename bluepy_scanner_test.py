from bluepy.btle import Scanner, DefaultDelegate, UUID, Peripheral, BTLEException
import time
import struct
import sys
import datetime

from cloudpost import *


recognizedServices = dict()
BLE_SERVICE_ENVIRONMENT = "0000181a-0000-1000-8000-00805f9b34fb"
settings_file = ("settings.xml")

def load_recognized_characteristics():
    parsed_file = xml.etree.ElementTree.parse(settings_file).getroot()
    uuid_root = parsed_file.find('uuids')
    chars = []
    for atype in uuid_root.findall('uuid'):
        chars.append(atype.find('name').text)
    #print("Parsed UUIDs: {}\n".format(chars))
    recognizedServices[BLE_SERVICE_ENVIRONMENT] = chars
        
#load_recognized_characteristics()


'''
BLE_CHAR_TEMPERATURE      = "00002a6e-0000-1000-8000-00805f9b34fb"
BLE_CHAR_HUMIDITY               = "00002a6f-0000-1000-8000-00805f9b34fb"

recognizedServices = dict()
recognizedServices[BLE_SERVICE_ENVIRONMENT] = [BLE_CHAR_TEMPERATURE, BLE_CHAR_HUMIDITY]
print("Services dictionary:")
'''
#print(recognizedServices)


class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, device, isNewDev, isNewData):
		if isNewDev:
			print("Discovered device: {}".format(device.addr))
		elif isNewData:
			print("Received new data from: {}".format(device.addr))
 
 
class MyDelegate(DefaultDelegate):
	def __init__(self,params):
		DefaultDelegate.__init__(self)
		self.peripheral = params

def printAdvertisingInformation(device):
	for (adtype, desc, value) in device.getScanData():
		print("{}: {}".format(desc, value)) 
	print("Address: {}".format(device.addr))
	print("AddressType: {}".format(device.addrType))
	print("Interfacenumber: {}".format(device.iface))
	print("Signal strength: {}".format(device.rssi))
	print("Device is connectable: {}".format(device.connectable))
	print("Number of recieved packets: {}".format(device.updateCount))
	return True

def printDeviceNames(devices):
	print("\n\nList of found device names:\n*****************************")
	for dev in devices:
		#print("Device {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
		#print ("Description: {}".format(dev.getDescription(9)))
		for (adtype, desc, value) in dev.getScanData():
			if (desc == "Complete Local Name"):
				print("Device name: {}".format(value))

			
			
def scanForDevices():
	scanner = Scanner().withDelegate(DefaultDelegate())#ScanDelegate())
	devices = scanner.scan(4.0)
	return devices;

def scanIAQDevices():
	print("\nScanning for devices....")
	iaq_devices = [];
	devices = scanForDevices()
	for dev in devices:
		for (adtype, desc, value) in dev.getScanData():
			if (desc == "Complete Local Name"):
				if "IAQ" in value:
					iaq_devices.append(dev);
					print("  -{} \t({}) \tRSSI={} dB".format(value, dev.addr, dev.rssi))
	print("Scan complete\n");
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
			print("\n  Found recognized service: {}".format(ser.uuid.getCommonName()))
			serChar = ser.getCharacteristics()
			for char in serChar:
				if char.uuid in recognizedServices[str(ser.uuid)]:
					print("   Added characteristics: {}".format(char.uuid.getCommonName()))
					peripheral.availableChararacteristics.append(char)
				else:
					print("   Found characteristics: {}".format(char.uuid.getCommonName()))
					
	return peripheral

def readCharacteristicsToBuffer(peripheral):
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
			peripheral.channel.add_to_buffer(field,value)
		except:
			print("Read of value {} failed.".format(sensor))
		print("  -{}:\t{} {} Raw: {}".format(sensor, value, unit, read_data))	



def main():
	load_recognized_characteristics()
	cloud = CloudPost()
	cloud.get_channel_information()
	loop_counter = 0
	
	while True:
		loop_counter = loop_counter + 1
		# Scan for devices until found
		devices = []
		while not len(devices):
			devices = scanIAQDevices();

		# Prepare peripherals
		# Read recognized services and characteristics and enable adding a channel
		peripherals = []
		print("Preparing peripherals:")
		for device in devices:
			print(" Peripheral:\t{}".format(device.addr))
			peripherals.append(preparePeripheral(device))
		
		# See if a Thingspeak channel exists for this device
		# Create a new channel if not
		for peripheral in peripherals:
			if peripheral.addr.upper() in cloud.channels.keys():
				peripheral.channel = cloud.channels[peripheral.addr.upper()]
			else:
				peripheral.channel = cloud.create_channel(peripheral.addr.upper())
		
		# Read all connected devices characteristics
		# Add them to a buffer and post to the cloud
		print("Reading peripherals:")
		for peripheral in peripherals:
			print(peripheral.addr)
			time.sleep(2);#Wait for the peripheral to write all measurements
			
			readCharacteristicsToBuffer(peripheral)

			#peripheral.channel.post()
			peripheral.disconnect()
		
		sys.exit(1)
		print("Time: {}\n".format(datetime.datetime.now()))
		time.sleep(5*60)



if __name__ == "__main__":
	main()