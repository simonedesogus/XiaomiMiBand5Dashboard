import sqlite3
from influxdb import InfluxDBClient
import os
import configparser

# Config
config = configparser.ConfigParser()
config.read(os.path.abspath('./Config/config.ini'))

conn = sqlite3.connect('Gadgetbridge.db')
device = config['DEFAULT']['DEVICE'] 
user = config['DEFAULT']['USER']

def writeActivity(conn):
	"""
	Input:	The conn to the sqlite3 db
	Descr:	Reads the file lastWrittenDP.txt that contains the timestamp of the lastWrittenDP.
			Scans the MI_BAND_ACTIVITY_SAMPLE table to find new DP that haven't been written before and
			writes this information to influxDB.
	"""

	filename = "./lastWrittenDP.txt"

	with open(filename, 'r') as fr:
		try:
			lastWrittenTimestamp = int(fr.readline().replace("\n", ""))
		except Exception as e:
			print(f"Error reading {filename}. {e}")
			return False


	query = f"SELECT * FROM MI_BAND_ACTIVITY_SAMPLE WHERE HEART_RATE > 30 AND HEART_RATE < 220 AND RAW_INTENSITY != -1"
	cursor = conn.execute(query)
	activityDPs = []
	counter = 0
	for row in cursor:
		timestamp = row[0]*1000*1000*1000 #ns precision
		if timestamp > lastWrittenTimestamp:
			rawIntensity = row[3]
			steps = row[4]
			rawKind = row[5]
			heartRate = row[6]
			activityDP = f"Activity,user={user},deviceId=1 rawIntensity={rawIntensity},steps={steps},rawKind={rawKind},heartRate={heartRate} {timestamp}"
			activityDPs.append(activityDP)
			lastWrittenTimestamp = timestamp	# this works also as a sanity check that the timestamps are contiguous
			counter +=1
        
        # Write batches of 1000 DP at a time
		if counter == 1000:
			writtenCorrectly = writeToInflux(activityDPs)
			if not writtenCorrectly:
				print(f"Error writing to influxdb. Exiting...")
				exit()

			with open(filename, 'w') as fw:
				fw.write(f"{lastWrittenTimestamp}")

			activityDPs = []
			counter = 0

	if counter < 1000:
		writtenCorrectly = writeToInflux(activityDPs)
		if not writtenCorrectly:
				print(f"Error writing to influxdb. Exiting...")
				exit()
    
	with open(filename, 'w') as fw:
		fw.write(f"{lastWrittenTimestamp}")

def writeToInflux(dataPointsList):
	"""
	Input: The dataPointsList. \n
	Descr: Write the list of datapoints into influxDB.
	"""

	host = config['DEFAULT']['HOST']
	port = config['DEFAULT']['PORT']
	username = config['DEFAULT']['USERNAME']
	password = config['DEFAULT']['PASSWORD']
	database = config['DEFAULT']['DATABASE']
	client = InfluxDBClient(host=host, port=port, username=username, password=password, gzip=False, ssl=False, verify_ssl=False)

	try:
		writtenCorrectly = client.write_points(dataPointsList, database=database, time_precision='n', batch_size=1000, protocol='line')
	except Exception as e:
		message = f"Exception occurred while writing into influxDB {e}"
		print(message)
		writtenCorrectly = False
	
	return writtenCorrectly

writeActivity(conn)
conn.close()