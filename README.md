# OBS-Tally-py
Tally light for OBS source using rpi, rgb leds, and obs-websocket
Each pi will sit and look for a websocket connection. Once connected, 
it will light yellow when the provided source is in preview and green when its in program

### Installation
* Run pip install watchgod to install the watchgod library, used to run the script

* Install and Setup NGINX and PHP-Server 
https://www.raspberrypi.org/documentation/remote-access/web-server/nginx.md

* Put index.php in /var/www/html/

* In index.php change tally.xml-path to match the actual path

* Run index.php from a browser

* Setup OBS-Tally Settings (IP, Password, Port from OBS-Websockets, Scenes and GPIO-Ports)

* Connect LEDs to the matching GPIO

* If you need to invert the outputs for no/nc relays, check the invert box in the webpage.

* Start this script and nginx on boot:
    sudo update-rc.d -f nginx defaults;
    sudo nano /etc/rc.local
	just above line 'exit 0' insert:
	sudo watchgod [/path/to/]obs-tally.main [/path/to/]tally.xml &


### Connection Diagram
![Connection Diagram](/docs/diagram.png)