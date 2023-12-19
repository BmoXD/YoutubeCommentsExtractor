import os
import requests
import mysql.connector
from datetime import datetime
from configparser import ConfigParser

print("YouTube Comments Scraper Configuration Test")

    
# Testing if configuration file exists on disk in the current working directory
print("----------")
print("Checking if config file exists -->")
assert os.path.isfile("config.ini") == True
print("OK")
print("----------")

# Opening the configuration file
config = ConfigParser()
config.read('config.ini')

# Checking if YouTube related config options are present in the config file
print("Checking if config has YouTube related options -->")
assert config.has_option('youtube', 'video_link') == True
assert config.has_option('youtube', 'cookies_file') == True
print("OK")
print("----------")

# Checking if MySQL related config options are present in the config file
print("Checking if config has MYSQL related options -->")
assert config.has_option('mysql', 'mysql_host') == True
assert config.has_option('mysql', 'mysql_db') == True
assert config.has_option('mysql', 'mysql_user') == True
assert config.has_option('mysql', 'mysql_pass') == True
print("OK")
print("----------")

# Checking if possible to connect to MySQL with the existing config options
print("Checking if it is possible to connect to MySQL with the given config options -->")
mysql_config_mysql_host = config.get('mysql', 'mysql_host')
mysql_config_mysql_db = config.get('mysql', 'mysql_db')
mysql_config_mysql_user = config.get('mysql', 'mysql_user')
mysql_config_mysql_pass = config.get('mysql', 'mysql_pass')
connection = mysql.connector.connect(host=mysql_config_mysql_host, database=mysql_config_mysql_db, user=mysql_config_mysql_user, password=mysql_config_mysql_pass)
assert connection.is_connected() == True
print("OK")
print("----------")

# Checking if log config files exist for log config
print("Checking if log config file exists log_comments.yaml -->")
assert os.path.isfile("log_comments.yaml") == True
print("OK")
print("----------")
print("Checking if log destination directory exists -->")
assert os.path.isdir("log") == True
print("OK")
print("----------")
print("Checking if migration source directory exists -->")
assert os.path.isdir("migrations") == True
print("OK")
print("----------")

print("Configuration file test DONE -> ALL OK")
print("----------------------------------------")
