import discord
import asyncio
from discord import compat
from discord.client import log

from Module import Module
from modules import *


import subprocess
import socket
import json

import htmlsocketserver

import pymongo

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


#BTW uwsgi --ini jaasite/jaasite_uwsgi.ini

# Main class, contains modules, communicates between them and front-end
class JaaClient(discord.Client):

    def __init__(self):
        super().__init__()

        # Get all modules and add client to their variables

        with open("data/config.json", "r") as f:
            self.args = json.loads(f.read())

        # discord.opus.load_opus(self.args["opus"])

        self.htmlsocketserver = htmlsocketserver.Htmlsocketserver(self)
        self.db = pymongo.MongoClient().jaa

        self.modules = [subclass(self) for subclass in Module.__subclasses__()]

    #Call on_request(data) on module if such module exists. Returns response from module, or None if module was not found
    async def try_request(self, module, data):
        module = next((m for m in self.modules if m.__class__.__name__ == module), None)
        response = None
        if hasattr(module, "on_request"):
            response = await module.on_request(data)

        return response

    #Sends event through websocker. Meant to be called from modules.
    def send_event(self, eventName, data={}):
        future = asyncio.ensure_future(
            self.htmlsocketserver.send_event(eventName, data))
        asyncio.wait(future)



    #Starts the bot
    def run(self):
        try:
            print("Setting up socketserver...")
            self.htmlsocketserver.start()

            print("Starting to log in...")
            with open("data/token", "r") as f:
                self.loop.run_until_complete(self.login(f.read()))

            print("Logged in, starting to connect...")
            self.loop.run_until_complete(self.connect())

        except KeyboardInterrupt:
            print("Starting to shut down...")
            self.loop.run_until_complete(self.logout())
            self.htmlsocketserver.stop()
            print("Logout complete, gathering tasks...")
            pending = asyncio.Task.all_tasks(loop=self.loop)
            gathered = asyncio.gather(*pending, loop=self.loop)
            print("Tasks gathered, starting to cancel...")
            try:
                gathered.cancel()
                self.loop.run_until_complete(gathered)
                gathered.exception()
            except:
                pass
        finally:
            print("Closing the loop...")
            self.loop.close()

    async def on_ready(self):
        #Find the voice channel and connect to it
        try:
            c = next(channel for channel in self.get_all_channels() if channel.id == self.args["vchannel"])
            self.vclient = await self.join_voice_channel(c)
        except StopIteration:
            print("No channel with id: {} found!".format(self.args["vchannel"]))


        print('All ready!')

    # If message is deemed as a command, specified by 'CommandChannels' and
    # 'CommandStarter', send 'on_command' event to all modules
    async def on_message(self, message):
        # If message is in command channels and starts with prefix(default '!'),
        # call all modules that have on_command() with sliced command(no
        # prefix)


        if message.channel.id in self.args["CommandChannels"] or ( self.args["PrivateCommands"] and message.channel.is_private ):
            if message.content.startswith(self.args["CommandStarter"]):
                command = message.content[len(self.args["CommandStarter"]):].split()
                for m in self.modules:
                    print("Sending", str(command), "to", str(m))
                    if hasattr(m, "on_command"):
                        await m.on_command(command, message)

    # Helper function to send events to modules
    @asyncio.coroutine
    def _run_event_module(self, module, event, *args, **kwargs):
        try:
            yield from getattr(module, event)(*args, **kwargs)
        except:
            pass

    # Mostly copied from discord.CLient, but this version dispatches to all
    # modules after client
    def dispatch(self, event, *args, **kwargs):
        log.debug('Dispatching event {}'.format(event))
        method = 'on_' + event
        handler = 'handle_' + event

        if hasattr(self, handler):
            getattr(self, handler)(*args, **kwargs)

        if hasattr(self, method):
            compat.create_task(self._run_event(
                method, *args, **kwargs), loop=self.loop)

        for m in self.modules:
            if hasattr(m, method):
                compat.create_task(self._run_event_module(
                    m, method, *args, **kwargs), loop=self.loop)


client = JaaClient()
client.run()
