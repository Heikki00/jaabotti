



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



    connection.init("ws://" + ip + ":1025")



    var playerData = {}









    function updateQueue(){

        var htmls = " "

        for(var i = 0; i < playerData.audios.length; i++){

            var audio = playerData.audios[i]



            var ohtml = $("#song-list-template")[0].outerHTML



            ohtml = ohtml.replace("%title%", audio["title"])

            ohtml = ohtml.replace("%id%", audio["id"])

            if(audio["times"] >= 0){

                ohtml = ohtml.replace("%times%", audio["times"])

            }

            else{

                ohtml = ohtml.replace("%times%", "&#8734;")

            }



            ohtml = ohtml.replace("%display%", i == 0 ? "block" : "none")



            var ohtml = ohtml.replace("id=\"song-list-template\"", "")

            htmls = htmls.concat(ohtml)

        }

        $('#song-list').html(htmls)

        $(".songRemoveButton").each(function(i) {

            $(this).click(function(e){

                if($(this).parent().parent().attr("id") != "song-list-template"){

                    connection.sendRequest("PlayerModule", {

                        action:"removeaudio",

                        index:i

                    },

                    function(data){

                    console.log("Tried " + i + " " + JSON.stringify(data))

                }

                )

                }

            })

        })

    }





    connection.onEvent = function(e){


            switch (e["name"]) {

                case "PlayerQueueChanged":

                    playerData.audios = e["data"]

                    updateQueue();

                    break;
                case "PlayerVolumeChange":
                    $("#volumeslider").slider('setValue', e["data"]["volume"])

                    break;

                default:

                    console.log("Unknown event from PlayerModule: " + e["name"])

                    break;

            }

        }






    $('#submitAudio').click(function(e){

        e.preventDefault()



        var aud_url = $('#urlField').val()


        if(aud_url == ""){

            return

        }



        connection.sendRequest("PlayerModule", {

            action:"addaudio",

            url:aud_url,

            times: 1

        },

        function(data){

            if(data["response"] != "success"){

                console.log("Fuccccccc")

            }

        }

        )



    })



    $('#extraSubmitAudio').click(function(e){



        if($('#extraUrlField').prop("enabled")){

            var aud_url = $('#extraUrlField').val()

        }

        else{

            var aud_url = $("#shortcutSelect").find(":selected").attr("href")

        }

        var aud_times = $('#extraTimesField').val()



        if(aud_url == ""){

            return

        }



        var times_num = Math.floor(Number(aud_times))



        if(isNaN(times_num) || (times_num < 0 && times_num != -1)){

            return

        }





        connection.sendRequest("PlayerModule", {

            action:"addaudio",

            url:aud_url,

            times: times_num

        })



    })



    $("#togglePauseButton").click(function(e){

        connection.sendRequest("PlayerModule", {

            action:"togglepause"

        })

    })







    $("#stopButton").click(function(e){

        connection.sendRequest("PlayerModule", {

            action:"stop"

        })

    })



    $("#skipButton").click(function(e){

        connection.sendRequest("PlayerModule", {

            action:"skip"

        })

    })



    $('#volumeslider').on("slideStop", function(e){

        connection.sendRequest("PlayerModule", {

            action:"setvolume",

            volume:e.value

        })

    })





    connection.socket.onopen = function(){

        connection.sendRequest("PlayerModule", {

            action:"get"

        },

        function(data){

            playerData = data

            updateQueue()
            
            
            $("#volumeslider").slider('setValue', data["volume"])
        })





        connection.sendRequest("DatabaseModule", {

            request:"globalShortcuts"

        },

        function(data){







            data.response.forEach(function(obj){

                opt = $("<option/>")

                opt.html(obj["name"])

                opt.attr("href", obj["url"])







                $('#shortcutSelect').append(opt)

            })










            $('#shortcutSelect').change(function(e){

                //console.log($(this).find(":selected").attr("href"))

                if($(this).find(":selected").attr("href") == "#"){

                    $("#extraUrlField").prop("disabled", false)

                }

                else{

                    $("#extraUrlField").prop("disabled", true)

                    $("#extraUrlField").val("")

                }

            })

        })

 


        }







})

