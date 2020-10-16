import mysql.connector as mc

class MySQLStorage:

	def __init__(self, **kwargs):
		user = kwargs.get('user', 'root')
		password = kwargs.get('password')
		database_name = kwargs.get('database')

		if password != None:
			self.database = mc.connect(
					user=user,
					password=password,
					database=database_name,
					auth_plugin='mysql_native_password'
				)
		else:
			self.database = mc.connect(
					user=user,
					database=database_name
				)

		self.cursor = self.database.cursor(buffered=True)

		self.base_query = "SELECT url, keywords FROM termXurlXkeywords WHERE term = %s"

	def get_urls(self, intent, slot):
		result = []

		self.cursor.execute(self.base_query, (intent,))
		intent_set = set(self.cursor.fetchall())

		self.cursor.execute(self.base_query, (slot,))
		slot_set = set(self.cursor.fetchall())

		result_set = slot_set.intersection(intent_set)

		if not result_set:
			return slot_set
		else:
			return result_set


	def get_urls2(self, tokens):	
		result = []

		for t in tokens:
			self.cursor.execute(self.base_query, (t,))
			r = self.cursor.fetchall()

			if r:
				result.append(set(r))

		if not result:
			return set()

		if len(result) > 1:
			return result[0].intersection(*result[1:])
		else:
			return result[0]

