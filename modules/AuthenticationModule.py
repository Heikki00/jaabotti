from Module import Module

import random
# Pretty much hello world
class AuthenticationModule(Module):

    def genUserToken(self, length):
        chars = list("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM123456789")
        token = []

        for _ in range(length):
            token.append(random.choice(chars))

        return ''.join(token)

    async def on_command(self, command, message):
        if len(command) == 1 and command[0] == "link":
            token = self.genUserToken(10)
            self.client.db.usertokens.update({"user_id": message.author.id},
                                               {"user_id":message.author.id, "token":token},
                                               True)

            await self.client.send_message(message.author,
                                           "http://" + self.client.args["ip"] + "/jaacontrol/login/" + token)

    async def on_request(self, data):
        if "action" not in data.keys():
            return {"response": "no_action"}

        if data["action"] == "get":
            if "token" not in data.keys():
                return {"response": "no_token"}

            token = data["token"]
            user_entry = self.client.db.usertokens.find_one({"token":token})

            if user_entry is None:
                return {"response": "bad_token"}

            for server in self.client.servers:
                for member in server.members:
                    if member.id == user_entry["user_id"]:
                        return {
                            "response":"success",
                            "name":member.name,
                            "id":member.id,
                            "avatar":member.avatar_url[:member.avatar_url.rfind(".")] + ".png",
                        }
            return {"response":"user_not_found"}


