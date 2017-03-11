from Module import Module
from time import time

import random
import json

# Pretty much hello world
class StatisticsModule(Module):

    def __init__(self):
        self.startTime = 0

    async def on_ready(self):
        self.startTime = time()
        self.updateShitpost()


    def updateShitpost(self):
        cur = self.client.dbexec("SELECT attachments, embeds, id FROM Messages WHERE channel_id=? AND (attachments!=? or embeds!=?)", (216234263379443712, "[]", "[]"))

        filetypes = (".png", ".jpg", ".JPG", ".PNG", ".gif", ".gifv")
        qualified = []
        for row in cur:
            if row[0] != "[]":
                m = json.loads(row[0])
                urlend = m[0]["url"][-6:]
                if urlend[urlend.find("."):] in filetypes:
                    qualified.append(m[0]["url"])
            else:
                m = json.loads(row[1])
                urlend = m[0]["url"][-6:]
                if "." in urlend:
                    if urlend[urlend.find("."):] in filetypes:
                        qualified.append(m[0]["url"])
        self.shitpost = random.choice(qualified)

    def latestModLinks(self, amt):
        if amt <= 0:
            return []

        cur = self.client.dbexec("SELECT content from Messages WHERE content like ? LIMIT ?;", ("%steamcommunity.com/sharedfiles%",amt))

        links = []
        for row in cur:
            links.append(row[0])

        return links

    #TODO: Error checking!
    async def on_request(self, data):
        if data["attr"] == "starttime":
            return {"response":self.startTime}

        elif data["attr"] == "total_messages":
            if "channel_ids" in data.keys():
                conditions = "WHERE channel_id=? or" * len(data["channel_ids"])
                conditions = conditions[:-2] + ";"
                cur = self.client.dbexec("SELECT count(*) FROM Messages " + conditions, tuple(data["channel_ids"]))
                num = 0
                for row in cur:
                    num = row[0]
                return {"response": num}
            else:
                cur = self.client.dbexec("SELECT count(*) FROM Messages;")
                return {"response": cur[0][0]}

        elif data["attr"] == "shitpost":
            self.updateShitpost()
            return {"response": self.shitpost}

        elif data["attr"] == "modlinks":
            return {"response": self.latestModLinks(data["amt"])}


        return {"response":"attr_unknown"}