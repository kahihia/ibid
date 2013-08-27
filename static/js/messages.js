function MessageEvent(event, data, sender, receiver, transport, timestamp, id) {
    this.event = event;
    this.data = data;
    this.sender = sender;
    this.receiver = receiver;
    this.transport = transport;
    this.timestamp = timestamp;
    this.id = id;
};
// constants for messages and events
MessageEvent.TRANSPORT = {}
MessageEvent.TRANSPORT.PUBNUB = 'pubnub';
MessageEvent.TRANSPORT.REQUEST = 'request';
MessageEvent.TRANSPORT.COMBINED = 'combined';

MessageEvent.SENDER = {}
MessageEvent.SENDER.CLIENT_FB = 'client-fb-';

MessageEvent.RECEIVER = {}
MessageEvent.RECEIVER.SERVER = 'server';

MessageEvent.EVENT = {}
MessageEvent.EVENT.BIDDING__INITIALIZE = 'bidding:initialize';
MessageEvent.EVENT.BIDDING__UPDATE_ACCESS_TOKEN = 'bidding:updateAccessToken';
MessageEvent.EVENT.BIDDING__SEND_STORED_WALL_POSTS = 'bidding:sendStoredWallPosts';


