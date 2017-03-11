import asyncio
import websockets
import json

#Class that handles communications with the website through html5 websocket
#Specs:
# -Every message recieved should be json string
# -Every message recieved should have module field, which contains the name of
# the module whom the request is directed to
# -Every message recieved should have data field for request-speceific arguments,
# it may be empty
# -Every message should have unique id(hash(module + data) for example)
#
# -All messages sent from here are json strings
# -All messages sent from here have fielf 'type', that is "response",
# "response_error" or "event"
# -All responses have id-field that contains id of the request-speceific
# -All responses have data field that contains response from the modules
# -Response_error is sent to answer request for nonexisting modules
# -All response_errors contain only the id of original request in addition
# to type
# -All events contain name field, module field, and data field
class Htmlsocketserver:

    def __init__(self, client):
        self.client = client
        self.server = None
        self.connected = set()

    #Set up and start the websocket server
    def start(self):

        #Websocket handler. This gets called once for every websocket(so every tab open)
        async def ws_handler(websocket, path):
            #Keep list of all sockets
            print("ACCEPTED CONNECTION")
            self.connected.add(websocket)
            try:
                while True:
                    if not websocket.open:
                        break
                    #If there are messages, handle them. If not, sleep.
                    try:
                        message = websocket.messages.get_nowait()
                    except asyncio.queues.QueueEmpty:
                        await asyncio.sleep(0.1)
                        continue

                    else:
                        #handle request/response
                        messageMap = json.loads(message)
                        messageId = messageMap["id"]
                        response = await self.client.try_request(messageMap["module"], messageMap["data"])
                        if response is not None:
                            await websocket.send(json.dumps({"type":"response", "id":messageId, "data":response}))
                        else:
                            await websocket.send(json.dumps({"type":"response_error", "id":messageId}))
            finally:
                self.connected.remove(websocket)

        #Setup the server and start it
        start_server = websockets.serve(ws_handler, self.client.args["ip"], self.client.args["wsPort"], loop=self.client.loop, max_queue=2 ** 20)
        self.server = self.client.loop.run_until_complete(start_server)

    # Send event to website
    async def send_event(self, module, eventName, data):
        for websocket in self.connected:
            await websocket.send(json.dumps({"type":"event", "name":eventName, "module":module, "data":data}))

    def stop(self):
        self.server.close()
