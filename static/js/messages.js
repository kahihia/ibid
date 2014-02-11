function EventMessage(event, data, sender, receiver, transport, timestamp, id) {
    this.event = event;
    this.data = data;
    this.sender = sender;
    this.receiver = receiver;
    this.transport = transport;
    this.timestamp = timestamp;
    this.id = id;
};
// constants for messages and events
EventMessage.TRANSPORT = {}
EventMessage.TRANSPORT.PUBNUB = 'pubnub';
EventMessage.TRANSPORT.REQUEST = 'request';
EventMessage.TRANSPORT.COMBINED = 'combined';

EventMessage.SENDER = {}
EventMessage.SENDER.CLIENT_FB = 'client-fb-';

EventMessage.RECEIVER = {}
EventMessage.RECEIVER.SERVER = 'server';

EventMessage.EVENT = {}
EventMessage.EVENT.BIDDING__INITIALIZE = 'bidding:initialize';
EventMessage.EVENT.BIDDING__UPDATE_ACCESS_TOKEN = 'bidding:updateAccessToken';
EventMessage.EVENT.BIDDING__SEND_WALL_POSTS = 'bidding:sendWallPosts';


