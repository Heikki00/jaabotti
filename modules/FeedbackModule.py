from Module import Module

# Pretty much hello world
class FeedbackModule(Module):

    async def on_command(self, command, message):
        if command[0] == "feedback":
            self.dbexec("INSERT INTO Feedback VALUES(?)", " ".join(command[1:]))

    async def on_request(self, data):
        self.client.dbexec("INSERT INTO Feedback VALUES(?)", (data["feedback"],))
        return {}
