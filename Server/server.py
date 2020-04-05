###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import sys
import uuid
import datetime

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from twisted.web.wsgi import WSGIResource

from flask import Flask, render_template, request

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
last_handwash = datetime.datetime.now()
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "{} from {}".format(payload.decode('utf8'), self.peer)
            self.factory.broadcast(msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):

    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.tickcount = 0
        self.tick()

    def tick(self):
        self.tickcount += 1
        # self.broadcast("tick %d from server" % self.tickcount)
        reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))




class BroadcastPreparedServerFactory(BroadcastServerFactory):

    """
    Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage.
    """

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))
        preparedMsg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(preparedMsg)
            print("prepared message sent to {}".format(c.peer))


@app.route('/')
def page_home():
    return render_template('index.html')

candy_in_ram = {}
candy_amount = candy_in_ram

def register_candy_receiver(id):
    candy_in_ram[id] = 1

def add_candy(id):
    if id in candy_in_ram:
        candy_in_ram[id] += 1
    else:
        register_candy_receiver(id)




if __name__ == '__main__':

    log.startLogging(sys.stdout)

    ServerFactory = BroadcastServerFactory
    # ServerFactory = BroadcastPreparedServerFactory

    wsFactory = ServerFactory("ws://127.0.0.1:9000")
    wsFactory.protocol = BroadcastServerProtocol
    listenWS(wsFactory)
    wsResource = WebSocketResource(wsFactory)
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

    # routing into broadcast

    @app.route('/yee/<id>', methods=['POST'])
    def broadcast_wash_of_hands(id):
        # TODO: global is a no no
        global last_handwash
        if (datetime.datetime.now() - last_handwash).seconds > 5:

            # content = request.json
            # print(request.form.get("yee", ""))
            add_candy(id)
            msg = f"Thank you for washing your hands, {id}\n{id} now has {candy_amount[id]} candies"
            #    return jsonify({"uuid":uuid})
            wsFactory.broadcast(msg)
        else:
            pass
        last_handwash = datetime.datetime.now()
        return f"Thanks for washing the hands, {id}\n"
    # create a root resource serving everything via WSGI/Flask, but
    # the path "/ws" served by our WebSocket stuff
    rootResource = WSGIRootResource(wsgiResource, {b'ws': wsResource})

    # create a Twisted Web Site and run everything
    site = Site(rootResource)

    webdir = File(".")
    web = Site(webdir)
    reactor.listenTCP(8080, site)

    reactor.run()
