from Module import Module

# Pretty much hello world
class LennyModule(Module):

    async def on_command(self, command, message):
        if len(command) == 1 and command[0] == "lenny":
            await self.client.send_message(message.channel, "( ͡° ͜ʖ ͡° )")

    async def on_request(self, data):
        return {"Face": "( ͡° ͜ʖ ͡° )"}
