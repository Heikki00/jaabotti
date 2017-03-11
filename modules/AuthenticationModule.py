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
            try:
                self.client.dbexec("INSERT INTO MemberTokens (user_id, token) VALUES (?,?)", (message.author.id, token))
            except:
                self.client.dbexec("UPDATE MemberTokens SET token=? WHERE user_id=?", (token, int(message.author.id)))

            await self.client.send_message(message.author, "http://91.153.14.235:6702/jaacontrol/login/" + token)

    async def on_request(self, data):
        if "action" not in data.keys():
            return {}
