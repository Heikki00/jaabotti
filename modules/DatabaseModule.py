from Module import Module

# Pretty much hello world
class DatabaseModule(Module):

    async def on_request(self, data):

        if "request" not in data.keys():
            return {"response": "no_request"}


        if data["request"] == "globalShortcuts":
            cur = self.client.db.playershortcuts.find({"author_id":None},{"name":1,"url":1,"_id":0})
            res = []
            for doc in cur:
                res.append(doc)
            return {"response": res}

        else:
            return {"response": "unknown_response"}

