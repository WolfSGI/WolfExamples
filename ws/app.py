import pathlib
import svcs
import structlog
from wolf.app.resolvers import RouteResolver
from wolf.app import Application
from wolf.app.render import html
from websockets.sync.server import serve


logger = structlog.get_logger("wolf.examples.websockets")


class WebsocketApp(Application):

    def handler(self, websocket):
        path = websocket.request.path
        with svcs.Container(self.services) as context:
            logger.info(f'Websocket ready to respond on {path}.')
            for message in websocket:
                websocket.send(f"App {self} responds: {message}.")


app = WebsocketApp(resolver=RouteResolver())


def websocket_runner():
    with serve(app.handler, "localhost", 9999) as server:
        server.serve_forever()


@app.resolver.router.register('/')
@html
def chat(request):
    return """
<html>
  <head>
    <link rel="icon" href="https://zany.sh/favicon.svg?text=ws" />
  </head>
  <body>
<!-- message form -->
<form name="publish">
  <input type="text" name="message">
  <input type="submit" value="Send">
</form>

<!-- div with messages -->
<div id="messages"></div>

    <script language="javascript">
let socket = new WebSocket("ws://localhost:9999");

// envoyer un message depuis le formulaire
document.forms.publish.onsubmit = function() {
  let outgoingMessage = this.message.value;

  socket.send(outgoingMessage);
  return false;
};

// message reçu - affiche le message dans div#messages
socket.onmessage = function(event) {
  let message = event.data;

  let messageElem = document.createElement('div');
  messageElem.textContent = message;
  document.getElementById('messages').prepend(messageElem);
}
    </script>

</body>
</html>
"""
