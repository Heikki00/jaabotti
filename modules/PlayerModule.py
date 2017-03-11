import asyncio
from Module import Module
import youtube_dl
from time import time

import re

rShort = re.compile(r"(http(s)?://)?(www\.)?youtu\.be/(?P<id>[^ /\n\t\?]+)(\?[^ /\n\t]+)?$")

rLong = re.compile(r"(http(s)?://)?(www\.)?youtube\.([^ \n\t/\.]+)/watch\?v=(?P<id>[^ /\n\t\&\?]+)(\&[^ /\n\t]+)?$")


def validateYTUrl(url):
    m = rShort.match(url)

    if m is not None:
        return 'https://youtu.be/' + m.group('id')

    m = rLong.match(url)

    if m is not None:
        return 'https://youtu.be/' + m.group('id')

    return ''


#-1 == loop
class Audio:

    def __init__(self, url, times=1):
        self.url = url
        self.times = times
        ytdl_opts = {"quiet": True}
        with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
            result = ytdl.extract_info(url, download=False)
            self.info = {}
            for s in ["id", "title", "thumbnail", "duration"]:
                self.info[s] = result[s]



class PlayerModule(Module):

    def __init__(self):
        self.volume = 1.0
        self.queue = []
        self.audioadded = asyncio.Event()
        self.current = None
        self.playnext = asyncio.Event()
        self.task = None
        self.player = None
        self.playtimes = []

    def _sendQueueChanged(self):
        audios = [{**a.info, **{"times": a.times}} for a in [self.current] + self.queue if a is not None]
        self.client.send_event("PlayerModule", "queueChanged", audios)

    async def on_ready(self):
        self.task = self.client.loop.create_task(self._player_task())


    def _next_audio(self):
        self.playnext.set()
        if self.current.times == 0:
            self.current = None

    def skip(self):
        self.current = None
        self.player.stop()
        self.playnext.set()

    def pause(self):
        if not self.isPaused() and self.player is not None:
            print("PAUSED")
            self.player.pause()
            self.playtimes.append(self.player.loops * self.player.delay)
            self.client.send_event("PlayerModule", "paused")

    def resume(self):
        if self.player is not None:
            self.player.resume()
            self.client.send_event("PlayerModule", "resumed")

    def addAudio(self, url, times):

        url_val = validateYTUrl(url)

        if url_val == '':
            return False

        aud = Audio(url_val, times)
        self.queue.append(aud)
        self.audioadded.set()

        self._sendQueueChanged()
        return True


    def stop(self):
        if self.player is not None:
            self.queue = []
            self.player.stop()
            self.player = None
            self.current = None
            self.client.send_event("PlayerModule", "stopped")

    def setVolume(self, volume):
        if self.player is not None:
            volume = max(min(volume, 2.0), 0.0)
            self.volume = volume
            self.player.volume = volume
            self.client.send_event("PlayerModule", "volumechange", {"volume":volume})

    def removeAudio(self, index):
        if len(self.queue) >= index and self.player is not None:
            if index != 0:
                self.queue.pop(index - 1)
                self._sendQueueChanged()
            else:
                self.skip()
            return True
        return False

    def isPaused(self):
        if self.player is None:
            return False
        return not self.player._resumed.is_set()

    def getPlayedAmount(self):
        if self.player is None:
            return 0

        return self.player.loops * self.player.delay + sum(self.playtimes)

    async def _player_task(self):
        shouldRepeat = False
        while True:
            self.playnext.clear()
            self.audioadded.clear()

            if not shouldRepeat or self.current is None:

                if len(self.queue) == 0:
                    await self.audioadded.wait()


                self.current = self.queue[0]
                self.queue = self.queue[1:]


            self.current.times -= 1
            shouldRepeat = self.current.times != 0
            self.player = await self.client.vclient.create_ytdl_player(self.current.url, use_avconv=False, after=self._next_audio)
            self.startTime = time()
            self.player.volume = self.volume
            self.player.start()

            await self.playnext.wait()
            self._sendQueueChanged()


    async def on_command(self, command, message):
        print(command)
        if len(command) == 2 and command[0] == "play":
            #TODO: Check url
            self.addAudio(command[1], 1)
        elif len(command) == 1 and command[0] == "pause":
            self.pause()
        elif len(command) == 1 and command[0] == "resume":
            self.resume()
        elif len(command) == 1 and command[0] == "stfu":
            self.stop()
        elif len(command) == 1 and command[0] == "skip":
            self.skip()
        elif len(command) == 2 and command[0] == "playnow":
            self.stop()
            self.addAudio(command[1], 1)
        elif len(command) == 2 and command[0] == "volume":
            command[1] = command[1].replace("%", "")
            try:
                self.setVolume(int(command[1]) / 100)
            except ValueError:
                pass


    #TODO Error checking, renaming
    async def on_request(self, args):

        if "action" not in args.keys():
            return {"response": "no_action"}

        if args["action"] == "addaudio":
            if "url" not in args.keys() and "times" not in args.keys():
                return {"response": "bad_addaudio"}

            success = self.addAudio(args["url"], int(args["times"]))
            if success:
                return {"response": "success"}
            else:
                return {"response": "failure"}

        elif args["action"] == "removeaudio":
            if "index" not in args.keys():
                return {"response": "bad_removeaudio"}

            success = self.removeAudio(int(args["index"]))
            if success:
                return {"response": "success"}
            else:
                return {"response": "failure"}

        elif args["action"] == "pause":
            self.pause()
            return {"response": "success"}

        elif args["action"] == "togglepause":
            if self.isPaused():
                self.resume()
            else:
                self.pause()
            return {"response": "success"}


        elif args["action"] == "resume":
            self.resume()
            return {"response": "success"}

        elif args["action"] == "skip":
            self.skip()
            return {"response": "success"}

        elif args["action"] == "stop":
            self.stop()
            return {"response": "success"}

        elif args["action"] == "setvolume":
            if "volume" not in args.keys():
                return {"response": "bad_removeaudio"}

            self.setVolume(args["volume"])
            return {"response": "success"}

        # Give everything, pretty much
        elif args["action"] == "get":
            audios = [{**a.info, **{"times": a.times}} for a in self.queue]
            if self.current is not None:
                audios.insert(0, {**self.current.info, **{"times": self.current.times}})
            return {"audios": audios, "isPaused": self.isPaused(), "volume":self.volume, "playedAmount": self.getPlayedAmount()}

        else:
            return {"response": "unknown_action"}
