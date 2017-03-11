from Module import Module

# Pretty much hello world
class DatabaseModule(Module):

    async def on_request(self, data):

        if "request" not in data.keys():
            return {"response": "no_request"}


        if data["request"] == "globalShortcuts":
            cur = self.client.dbexec("SELECT shortcut, url from PlayerShortcuts WHERE author_id is NULL")
            resp = []

            for row in cur:
                resp.append([row[0], row[1]])

            return {"response":resp}

        else:
            return {"response": "unknown_response"}

