
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

    $('#ip').html(ip)

    connection.socket.onerror = function(e){
        console.log(e)
        connection.socket.onclose = function(ee){
            console.log(ee)
        }
    }


    connection.socket.onopen = function(e){

        connection.sendRequest("StatisticsModule", {
            attr:"starttime"
        },
        function(data){
            var uptime = (Date.now() / 1000) -  data["response"]
            var h = Math.floor(uptime / 3600)
            var m = Math.floor((uptime - (h * 3600)) / 60)
            $("#uptime").html(h + "h " + m + "m")
        }
        )

        connection.sendRequest("StatisticsModule", {
            attr:"total_messages",
            channel_ids:[]
        },
        function(data){
            $("#total-messages").html(data["response"])
        })

        connection.sendRequest("StatisticsModule", {
            attr:"total_messages",
            channel_ids:["199174130296160256"]
        },
        function(data){
            $("#general-messages").html(data["response"])
        })

        connection.sendRequest("StatisticsModule", {
            attr:"total_messages",
            channel_ids:["216234263379443712"]
        },
        function(data){
            $("#dank-messages").html(data["response"])
        })

        connection.sendRequest("StatisticsModule", {
            attr:"total_messages",
            channel_ids:["236950342997245953"]
        },
        function(data){
            $("#jaa-messages").html(data["response"])
        })

        connection.sendRequest("StatisticsModule", {
            attr:"total_messages",
            channel_ids:["257193153042317312"]
        },
        function(data){
            $("#uverwutz-messages").html(data["response"])
        })


        connection.sendRequest("StatisticsModule", {
            attr:"shitpost"
        },
        function(data){
            $("#shitpost-img").attr("src", data["response"])

        })

        connection.sendRequest("StatisticsModule", {
            attr:"modlinks",
            amt:5
        },
        function(data){
            data["response"].forEach(function(obj){
                link = $('<a/>')
                link.attr("href", obj)
                link.html(obj.substr(obj.lastIndexOf("=") + 1))
                link.addClass("list-group-item")
                link.addClass("list-group-item-action")
                $("#modlist").append(link)
            })

        })



    }










})