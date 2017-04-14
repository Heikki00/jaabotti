from Module import Module

# Pretty much hello world
class FeedbackModule(Module):

    async def on_command(self, command, message):
        if command[0] == "feedback":
            self.client.db.feedback.insert({"feedback", " ".join(command[1:])})

    async def on_request(self, data):
        self.client.db.feedback.insert({"feedback", data["feedback"]})
        return {}
