from lib import stomp

class ChannelListener(object):
    def on_message(self, headers, message):
        print "received a message %s" % message

conn = stomp.Connection([('localhost', 61613)])
conn.add_listener(ChannelListener())
conn.start()
conn.connect()
conn.subscribe(destination='/topic/auction/', ack='auto')

while True:
    x=10

conn.disconnect()

