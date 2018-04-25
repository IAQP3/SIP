import unittest
from cloudpost import *


class MyTest(unittest.TestCase):
	
	def test_post(self):
		cloud = CloudPost()
		get_info = cloud.get_channel_information()
		
		self.assertEqual(get_info, None)
		

if __name__ == '__main__':
	unittest.main()