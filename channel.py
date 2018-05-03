import xml.etree.ElementTree
import requests
from time import gmtime, strftime
import os
import logging

py_path=os.path.dirname(os.path.realpath(__file__))

class Channel():
	def __init__(self, api_key, name, address, ID):
		self.settings_file = py_path+"/settings.xml"
		self.api_key = api_key
		self.supportedUUIDS = []
		self.name = name
		self.description = address
		self.api_post_url = None
		self.load_settings()
		self.id = ID;
		self.load_uuids()
	
	def post(self, send_data):
		logging.info("Sending data to cloud")
		data = {'api_key': self.api_key}
		
		for pair in send_data:
			data['field' + pair['field']] = pair['value']
		
		try:
			r = requests.post(self.api_post_url, data)
		except requests.exceptions.ConnectionError as e:
			logging.exception('Connection Error')
			logging.exception(e)
			return 0
		
		if (r.status_code==200):
			logging.info("Succesfully posted data")
			logging.debug(r.json())
		else:
			logging.info("Error posting data:")
		
		return r.status_code
	
	def get_field_for_UUID(self, uuid):
		for a in self.supportedUUIDS:
			#logging.info("a: {} uuid: {}".format(a,uuid))
			if a['name'] == uuid:
				return a['field']
		return None

	def load_uuids(self):
		parsed_file = xml.etree.ElementTree.parse(self.settings_file).getroot()
		uuid_root = parsed_file.find('uuids')
		for atype in uuid_root.findall('uuid'):
			new_uuid = {}
			new_uuid['name'] = atype.find('name').text
			new_uuid['sensor'] = atype.find('sensor').text
			new_uuid['location'] = atype.find('location').text
			new_uuid['data_type'] = atype.find('data_type').text
			new_uuid['field'] = int(atype.find('field').text)
			new_uuid['factor'] =  float(atype.find('factor').text)
			new_uuid['unit'] =  atype.find('unit').text
			self.supportedUUIDS.append(new_uuid)

	def load_settings(self):
		parsed_file = xml.etree.ElementTree.parse(self.settings_file).getroot()
		# Load thingspeak settings
		#server_element = parsed_file.find('server')
		thingspeak_element = parsed_file.find('thingspeak')
		post_address_element = thingspeak_element.find('post_address')
		self.api_post_url = post_address_element.text

		'''# Load RF-SensIt settings
		server_element = parsed_file.find('server')
		rfsensit_element = server_element.find('rfsensit_tcp')
		self.TCP_IP = rfsensit_element.find('post_address').text
		self.TCP_PORT = int(rfsensit_element.find('post_port').text)
		self.BUFFER_SIZE = int(rfsensit_element.find('post_buffer_size').text)
		'''

