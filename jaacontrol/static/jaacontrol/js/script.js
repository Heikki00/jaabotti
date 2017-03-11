$(document).ready(function(){
    String.prototype.hashCode = function(){
    var hash = 0;
    if (this.length == 0) return hash;
    for (i = 0; i < this.length; i++) {
        char = this.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
    }


    var connection = {
        init : function(path){
            this.socket = new WebSocket(path)
            this.successFunctions = {}
            this.socket.onmessage = function(e){
                data = JSON.parse(e.data)

                if(data["type"] == "response"){
                    if(connection.successFunctions[data["id"]] != null){
                        connection.successFunctions[data["id"]](data["data"])
                    }
                    else{
                        console.log("Recieved a response without assinged callback function: " + e.data)
                    }
                }
                else if(data["type"] == "event"){
                    console.log(e.data)
                    if(connection.onEvent != null){
                        connection.onEvent(data)

                    }
                }
                else{
                    console.log("Recieved a websocket message without known type: " + e.data)
                }
            }
        },

        sendRequest: function(module, data, onSuccess=function(data){}){
            dataJson = JSON.stringify(data)
            hash = (module + dataJson).hashCode()

            messageJson = JSON.stringify({
                module:module,
                data:data,
                id:hash
            })

            this.successFunctions[hash] = onSuccess

            this.socket.send(messageJson)

        }

    }

    var ip = "139.59.211.4"


    connection.init("ws://" + ip + ":80")

    $("#submitFeedback").click(function(e){
        connection.sendRequest("FeedbackModule", {
            feedback:$("#feedbackField").val()
        })

    })


})