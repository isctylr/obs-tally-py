#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>


import asyncio
import base64
import hashlib
import json
import logging
import sys
import socket
import websockets
import xml.etree.ElementTree as ET

from gpiozero import LED

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup()

logger = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ConnectionFailure(Exception):
    pass


class OBSTally():

  def __init__(self):
    self.ws = None
    self.tree = ET.parse('tally.xml')
    self.root = self.tree.getroot()
    self.host = self.root[0].text
    self.port = self.root[1].text
    self.password  = self.root[2].text

    #
    # Scene Config
    #
    self.camera_name = self.root[3].text

    #
    # Configure Tallys
    #
    self.p_red = LED(self.root[4].text)
    self.p_green = LED(self.root[5].text)
    self.p_blue = LED(self.root[6].text)

    #
    # Init LEDs
    #

    self.p_red.off()
    self.p_green.off()
    self.p_blue.off()

    #
    # State
    #
    self.camera_state = "Init"

  async def on_connect(self):
    # authenticate with obs-websocket
    requestpayload = {'message-id':'1', 'request-type':'GetAuthRequired'}
    await self.ws.send(json.dumps(requestpayload))
    getauthresult = json.loads(await self.ws.recv())
    if getauthresult['status'] != 'ok':
      raise ConnectionFailure('Server returned error to GetAuthRequired request: {}'.format(getauthresult['error']))
    if getauthresult['authRequired']:
      if self.password == None:
        raise ConnectionFailure('A password is required by the server but was not provided')
      secret = base64.b64encode(hashlib.sha256((self.password + getauthresult['salt']).encode('utf-8')).digest())
      auth = base64.b64encode(hashlib.sha256(secret + getauthresult['challenge'].encode('utf-8')).digest()).decode('utf-8')
      auth_payload = {"request-type": "Authenticate", "message-id": '2', "auth": auth}
      await self.ws.send(json.dumps(auth_payload))
      authresult = json.loads(await self.ws.recv())
      if authresult['status'] != 'ok':
        raise ConnectionFailure('Server returned error to Authenticate request: {}'.format(authresult['error']))
    # No auth errors, yay
    logger.debug("Connection successful")
    # Get initial state
    await self.get_initial_state()


  async def get_initial_state(self):
    # Check if camera is in program
    requestpayload = {'message-id':'2', 'request-type':'GetCurrentScene'}
    await self.ws.send(json.dumps(requestpayload))
    result = json.loads(await self.ws.recv())
    progs = result['sources']
    if self.on_program_changed(progs):
      return

    # Check if camera is in preview
    requestpayload = {'message-id':'3', 'request-type':'GetPreviewScene'}
    await self.ws.send(json.dumps(requestpayload))
    result = json.loads(await self.ws.recv())
    prevs = result['sources']
    self.on_preview_changed(prevs)

  def on_disconnect(self):
    self.switch_state("Disconnected")

  def handle_message(self, message):
    messageobj = json.loads(message)
    logger.debug(message)
    if (messageobj['update-type'] == "SwitchScenes"):
      self.on_program_changed(messageobj['sources'])
    elif (messageobj['update-type'] == "PreviewSceneChanged"):
      self.on_preview_changed(messageobj['sources'])

  def on_preview_changed(self, sources):
    """
      :returns boolean true if it is in the preview screen (and not in program)
    """
    logger.debug("Preview changed")
    if self.camera_state == "Program":
      # Program overrides preview, so ignore
      return False
    for src in sources:
      if src['name'] == self.camera_name and src['render']:
        self.switch_state("Preview")
        return True
    self.switch_state("Off")
    return False

  def on_program_changed(self, sources):
    """
      :returns boolean true if it is in the program screen 
    """
    logger.debug("Program changed")
    for src in sources:
      if src['name'] == self.camera_name and src['render']:
        self.switch_state("Program")
        return True

    if self.camera_state == "Program":
      # The camera was switched out, so its always moved to preview
      self.switch_state("Preview")
    else:
      self.switch_state("Off")
    return False

  def switch_state(self, state):
    if state == "Off":
      self.camera_state = "Off"
      logger.info("Camera off")
      self.p_green.on()
      self.p_red.on()
      self.p_blue.on()
    elif state == "Preview":
      self.camera_state = "Preview"
      logger.info("Camera in Preview")
      self.p_green.off()
      self.p_red.off()
      self.p_blue.on()
    elif state == "Program":
      self.camera_state = "Program"
      logger.info("Camera in Program")
      self.p_green.off()
      self.p_red.on()
      self.p_blue.on()
    elif state == "Disconnected":
      self.camera_state = "Disconnected"
      logger.info("Camera Disconnected")
      self.p_green.off()
      self.p_red.on()
      self.p_blue.off()

  async def listen_forever(self):
    while True:
    # outer loop restarted every time the connection fails
      logger.debug('Creating new connection...')
      try:
        async with websockets.connect('ws://{}:{}'.format(self.host, self.port)) as ws:
          self.ws = ws
          await self.on_connect()
          while True:
          # listener loop
            try:
              reply = await asyncio.wait_for(ws.recv(), timeout=10)
            except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
              try:
                pong = await ws.ping()
                await asyncio.wait_for(pong, timeout=5)
                logger.debug('Ping OK, keeping connection alive...')
                continue
              except:
                self.on_disconnect()
                logger.debug(
                  'Ping error - retrying connection in 5 sec (Ctrl-C to quit)')
                await asyncio.sleep(5)
                break
            # logger.debug('Server said > {}'.format(reply))
            self.handle_message(reply)
      except socket.gaierror:
        self.on_disconnect()
        logger.debug(
          'Socket error - retrying connection in 5 sec (Ctrl-C to quit)')
        await asyncio.sleep(5)
        continue
      except OSError:
        self.on_disconnect()
        logger.debug('OS Error - Retrying connection in 5 sec (Ctrl-C to quit)')
        await asyncio.sleep(5)
        continue
      except ConnectionRefusedError:
        self.on_disconnect()
        logger.debug('Nobody seems to listen to this endpoint. Please check the URL.')
        logger.debug('Retrying connection in 5 sec (Ctrl-C to quit)')
        await asyncio.sleep(5)
        continue
      except ConnectionFailure:
        logger.error('Incorrect password provided for OBS-WebSocket!')
        await asyncio.sleep(10000) # needs to stay running for watchgod to reload.
        continue

#def main():
obs_tally = OBSTally()
asyncio.run(obs_tally.listen_forever())
