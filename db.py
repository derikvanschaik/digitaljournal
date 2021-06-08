import datetime as datetime
import json 

class Db:
	def __init__(self, filename):
		self.data = {}
		self.filename = filename
		try:
			with open(filename) as json_file:
				self.data = json.load(json_file)
		except FileNotFoundError:
			pass 

	def write(self, date, title, tags, text):
		self.data[date] = {
			'title':title,
			'tags':tags,
			'text':text,
			}
		self.save_database()

	def delete(self, date):
		self.data.pop(date)
		self.save_database()

	def get_entry(self, time):
		if time in self.data:
			return self.data[time]
		return None

	def get_all_entries(self):
		return self.data
	
	def save_database(self):
		with open(self.filename, 'w') as outfile:
			json.dump(self.data, outfile)

