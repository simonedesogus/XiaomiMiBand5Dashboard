# Xiaomi Mi Band 5 to InfluxDB + Grafana

As a fun little project, I decided to pull the data from the Xiaomi Mi Band 5 that I wear every day and put this data in my local influxDB server and make a Grafana dashboard.
The data can be analyzed further to find out which RAW_KIND code corresponds to the different activities that the MiBand can track.

The project was heavily inspired by the GitHub user arpanghosh8453:
https://www.reddit.com/r/Python/comments/ms57g1/i_have_used_python_to_record_my_health_stats_in/

## Setup

First thing first, we need to pull the data from the MiBand5 to a database. This feature is not available from the official Mi Fit app, but luckily we can use the Gadgetbridge app from the FreeYourGadget project.

### Gadgetbridge

The official repo:

https://github.com/Freeyourgadget/Gadgetbridge#special-pairing-procedures

Download the apk from F-Droid and install it on your android phone.

In order to pair the MiBand5 to your phone follow the procedure
described here:

https://codeberg.org/Freeyourgadget/Gadgetbridge/wiki/Huami-Server-Pairing

Once the MiBand5 is fully connected with our Gadgetbridge app,
we can download the data into a sqlite3 db from the Database Management tab-> Export DB. The Exported DB will be called Gadgetbridge and it will be in /storage/emulated/0/Android/data/nodomain.freeyourgadget.gadgetbridge/files

Grab the db and move it inside the repository folder.

### InfluxDB

To store our time series data, we need a time series database. InfluxDB is the DB that I chose for this project,
and you can find how to install the OSS version here:

https://portal.influxdata.com/downloads/

NOTE: I prefer to use the 1.8.4 version as a docker image.

To run the container with default config use the command:

```
$ docker run -p 8086:8086 \
      -v influxdb:/root/influxdb/data \
      influxdb:1.8.4 
```

From inside the container, run the influx command to setup for the first time a username and password.
If you plan to interact with influxDB from another computer in the same network, open the port 8086.

### Grafana

Download and install Grafana from here:

https://grafana.com/grafana/download

Access the Grafana webpage from localhost:3000 or IP:3000, where IP is the IP of the computer in the same network
where the instance of Grafana is running.
If you plan to interact with Grafana from another computer in the same network, open the port 3000.

If you want to reuse the Dashboard that I made, import the Grafana.json from the repo into Grafana.

### Script

Now it is time to use the script readSQLLiteDBToInfluxDB.py from the repo to write the data in InfluxDB.
Install the dependencies with:

```
pip install -r requirements.txt
```

Modify the config.ini with your parameters.
Run the script being careful that the Database is called Gadgetbridge.db and it is inside the repository.

The lastWrittenDP.txt will be modified with the last Written DP timestamp, and it is used by the script to avoid writing datapoints that were already written before.

Repeat this procedure every time you need to upload the database to influx, and hop into grafana to visualize the data!
