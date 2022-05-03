import os

# stopping all docker containers
os.system("docker rm -f $(docker ps -a -q)")

# starting selenium hub
os.system("docker run -d -p 4442-4444:4442-4444 --net grid --name selenium-hub selenium/hub:4.1.3-20220405")

# starting nodes
for node_count in range(5):
    os.system('docker run -d --net grid -e SE_EVENT_BUS_HOST=selenium-hub     --shm-size="1g"     -e SE_EVENT_BUS_PUBLISH_PORT=4442     -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443     selenium/node-chrome:100.0-20220405')

"""
30 12 26 * * python3 /home/automatic_scraping_engine/reset_hub.py
31 12 26 * * screen -r yogafinder;python3 /home/automatic_scraping_engine/yogafinder.py;screen -d
32 12 26 * * screen -r vendry;python3 /home/automatic_scraping_engine/vendry.py;screen -d
33 12 26 * * screen -r wspot;python3 /home/automatic_scraping_engine/weddingspot.py;screen -d
34 12 26 * * screen -r wwire;python3 /home/automatic_scraping_engine/weddingwire.py;screen -d
35 12 26 * * screen -r splacer;python3 /home/automatic_scraping_engine/splacer.py;screen -d
36 12 26 * * screen -r reelscout;python3 /home/automatic_scraping_engine/reelscout.py;screen -d
37 12 26 * * screen -r peerspace;python3 /home/automatic_scraping_engine/peerspace.py;screen -d
38 12 26 * * screen -r eventective;python3 /home/automatic_scraping_engine/eventective.py;screen -d
39 12 26 * * screen -r breawer;python3 /home/automatic_scraping_engine/breawer.py;screen -d
39 12 26 * * screen -r venuefinder;python3 /home/automatic_scraping_engine/breawer.py;screen -d
"""