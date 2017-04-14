from Module import Module
from datetime import datetime, timedelta
from time import time
import random
import requests
import json
import random

# Pretty much hello world
class StatisticsModule(Module):

    def __init__(self, client):
        self.client = client
        self.startTime = time()
        self.updateShitpost()
        self.updateXkcd()


    def updateShitpost(self):
        channel_id = "216234263379443712"

        params = {
            "channel_id":channel_id,
            "$or":[
                {"attachments": {"$ne": []}},
                {"embeds": {"$ne":[]}}
            ]
        }

        cur = self.client.db.messages.find(params, {"attachments":1,"embeds":1, "_id":0})
        filetypes = (".png", ".jpg", ".JPG", ".PNG", ".gif")
        qualified = []
        for doc in cur:
            if doc["attachments"] != []:
                if doc["attachments"][0]["url"].endswith(filetypes):
                    qualified.append(doc["attachments"][0]["url"])
            else:
                if doc["embeds"][0]["url"].endswith(tuple(filetypes)):
                    qualified.append(doc["embeds"][0]["url"])

        self.shitpost = random.choice(qualified)
        now = datetime.now().time()
        offset = 60 * (60 - now.minute)
        offset += 60 - now.second
        self.client.loop.call_later(offset, self.updateShitpost)

    def latestModLinks(self, amt):
        if amt <= 0:
            return []
        cur = self.client.db.messages.find({"content":{"$regex":"/.*steamcommunity\.com\/sharedfiles.*/"}}, {"content":1, "_id": 0}).limit(amt)
        links = []
        for doc in cur:
            links.append(doc["content"])
            #TODO: Make this andle messages with link and something else
        return links

    def updateXkcd(self):
        maxXkcd = 1815
        xkcdQueryUrlPart1 = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D"http%3A%2F%2Fxkcd.com%2F';

        xkcdQueryUrlPart2 = '%2F"%20and%20xpath%3D%27%2F%2Fdiv%5B%40id%3D"comic"%5D%2F%2Fimg%27%0A&format=json&diagnostics=true&callback';
        xkcdId = random.randint(100, maxXkcd)
        r = requests.get(xkcdQueryUrlPart1 + str(xkcdId) + xkcdQueryUrlPart2)
        self.xkcd = json.loads(r.text)
        now = datetime.now().time()
        offset = 60 * (60 - now.minute)
        offset += 60 - now.second
        self.client.loop.call_later(offset, self.updateXkcd)

    async def on_request(self, data):

        if "attr" not in data.keys():
            return {"response": "no_attr"}

        if data["attr"] == "starttime":
            return {"response":self.startTime}

        elif data["attr"] == "total_messages":
            if "channel_ids" in data.keys() and len(data["channel_ids"]) > 0:
                count = self.client.db.messages.find({"channel_id": {"$in":data["channel_ids"]}}).count()
                return {"response": count}
            else:
                count = self.client.db.messages.find().count()
                return {"response": count}

        elif data["attr"] == "shitpost":
            return {"response": self.shitpost}

        elif data["attr"] == "modlinks":
            return {"response": self.latestModLinks(data["amt"])}

        elif data["attr"] == "xkcd":
            return {"response": self.xkcd}

        return {"response":"attr_unknown"}

