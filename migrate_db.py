from configparser import ConfigParser
import os
import yaml
import logging
import logging.config
import mysql.connector
import time

from mysql.connector import Error
from datetime import datetime

connection = None
connected = False

# Connecting to the database
def init_db():
	global connection
	connection = mysql.connector.connect(host=mysql_host,
									  database=mysql_db,
									  user=mysql_user,
									  password=mysql_pass)
	
def get_cursor():
	global connection
	try:
		connection.ping(reconnect=True, attempts=1, delay=0)
		connection.commit()
	except mysql.connector.Error as err:
		log.error("No connection to db " + str(err))
		connection = init_db()
		connection.commit()
	return connection.cursor()


# Create migrations table
def create_migrations_table():
	cursor = get_cursor()
	result = []
	try:
		cursor = connection.cursor()
		cursor.execute(f"""
				CREATE TABLE IF NOT EXISTS migrations (
					id INT AUTO_INCREMENT PRIMARY KEY,
				 	table_name VARCHAR(255),
					file_name VARCHAR(255),
					exec_ts INT(10),
					exec_dt DATETIME
				)
			""")
		connection.commit()
	except Error as e :
		log.error("Problem creating migrations table in DB: " + str(e))
	pass
	#return result

#Check if a table exists
def table_exists(table_name):
	try:
		cursor = get_cursor()
		
		cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'")
		results = cursor.fetchone()[0]
		if results <= 0:
			return False
	except Error as e:
		log.error(f"Error checking if table {table_name} exists: {str(e)}")
	return True

def get_all_tables():
	try:
		cursor = get_cursor()
		cursor.execute("SHOW TABLES")
		all_tables = cursor.fetchall()
		table_names = [table[0] for table in all_tables if table[0] != 'migrations']
		return table_names
	except Error as e:
		log.error(f"Error getting table names: {str(e)}")
	return []

def does_migration_exist(migration, table_name):
	try:
		cursor = get_cursor()
		query = "SELECT * FROM migrations WHERE 'table' = %s AND 'migration' = %s"
		cursor.execute(query, (table_name, migration))
		result = cursor.fetchone()
		return result is not None
	except Error as e:
		log.error(f"Error checking migration entry: {str(e)}")
		return False
	
# Document the migration of a table in the migration table
def document_migration(table_name, file_name, exec_ts, exec_dt):
	cursor = get_cursor()
	try:
		cursor = connection.cursor()
		query = f"""INSERT INTO migrations (table_name, file_name, exec_ts, exec_dt)
					VALUES (%s, %s, %s, %s)
		"""
		query_values = (table_name, file_name, exec_ts, exec_dt)
		cursor.execute(query, query_values)
		connection.commit()
	except Error as e :
		log.error('Problem inserting migration values into DB: ' + str(e))
		pass

def execute_migrate_query(table, query):
	cursor = get_cursor()
	try:
		log.debug(str(query))
		cursor = connection.cursor()
		formatted_query = query % ("`"+table+"` ")
		log.debug(formatted_query)
		cursor.execute(formatted_query)
		connection.commit()
	except Error as e :
		log.error('Problem running the migrate query: ' + str(e))
		return True
	return False

def main():
	migration_list = []

	# Check if the migrations table exists
	if table_exists("migrations") == False:
		create_migrations_table()
	else:
		log.info("Migration table already exists!")

	migration_files = os.listdir(os.getcwd() + "/migrations/")
	for file in migration_files:
		if file.endswith('.sql'):
			migration_list.append(file)
			  
	# Sorting list to be processed in the correct order. Just because...
	migration_list.sort(reverse=False)

	table_list = get_all_tables()

	for table in table_list:
		for migration in migration_list:
			if does_migration_exist(migration, table) == False:
				with open(os.getcwd() + "/migrations/" + migration, 'r') as file:
					sql_query = file.read()
					log.debug(sql_query)
					log.info("Doing migration: " + str(migration))
					if execute_migrate_query(table, sql_query) == False:
						exec_ts = int(time.time())
						exec_dt = datetime.utcfromtimestamp(exec_ts).strftime('%Y-%m-%d %H:%M:%S')
						document_migration(table, migration, exec_ts, exec_dt)
						log.info("OK")
			else:
				log.error("Problem applying migration. Aborting")



if __name__ == "__main__":

# If log folder doesn't exist then create one!
	log_folder = 'log'
	if not os.path.exists(log_folder):
		os.makedirs(log_folder)
		print(f"Created '{log_folder}' folder.")

	# Loading logging configuration
	with open('./log_migratedb.yaml', 'r') as stream:
		log_config = yaml.safe_load(stream)

	logging.config.dictConfig(log_config)
	
	log = logging.getLogger('root')
	
	try:
		config = ConfigParser()
		config.read('config.ini')

		# [mysql] section
		mysql_host = config.get('mysql', 'mysql_host')
		mysql_db = config.get('mysql', 'mysql_db')
		mysql_user = config.get('mysql', 'mysql_user')
		mysql_pass = config.get('mysql', 'mysql_pass')
	except:
		log.exception('')
	log.info("Done loading config.ini")

	# Let's connect to the database
	init_db()

	log.info('Connecting to MySQL DB')
	try:
		cursor = get_cursor()
		if connection.is_connected():
			db_Info = connection.get_server_info()
			log.info('Connected to MySQL database. MySQL Server version on ' + str(db_Info))
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			log.debug('Your connected to - ' + str(record))
			connection.commit()
	except Error as e :
		log.error('Error while connecting to MySQL' + str(e))

	main()