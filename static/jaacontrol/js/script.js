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
                    console.log("Recieved a response without assinged callback function: " + data.toSource())
                }
            }
              else if(data["type"] == "event"){
                if(connection.onEvent != null){
                  connection.onEvent(data)
                }
              }
            }

        },

        sendRequest: function(module, data, onSuccess=function(data){}){
            datastring = JSON.stringify(data)
            hash = (module + datastring).hashCode()

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



    $("#submitFeedback").click(function(e){
        connection.sendRequest("FeedbackModule", {
            feedback:$("#feedbackField").val()
        })

    })
    
    

    connection.socket.onopen = function(){
      if($("#context_token").attr("content") != "0"){
      connection.sendRequest("AuthenticationModule",{
        action:"get",
        token: $("#context_token").attr("content") 
    },
      function(data){
        var root = $("<div/>")

        var head = $("<h4/>")
        head.text(data["name"])
        head.css("margin-bottom", "0px")

        var hr = $("<hr/>")
        hr.css("margin", "5px")
        
        var img = $("<img/>")
        img.attr("src", data["avatar"])
        var size = 50
        img.attr("width", size)
        img.attr("height", size)

        root.append(head)
        root.append(hr)
        root.append(img)

       $("#userlink").popover({
        html:true,
        placement:"bottom",
         content: root[0].outerHTML
       })

      $("#userlink").text(data["name"])
      }
      )
      }
    
    }


})
