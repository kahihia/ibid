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
MessageEvent.prototype.TRANSPORT = new function () {
    this.PUBNUB = 'pubnub';
    this.REQUEST = 'request';
    this.COMBINED = 'combined';
}();

MessageEvent.prototype.SENDER = new function () {
    this.CLIENT_FB = 'client-fb-';
}();

MessageEvent.prototype.RECEIVER = new function () {
    this.SERVER = 'server';
}();

MessageEvent.prototype.EVENT = new function () {
    this.BIDDING__INITIALIZE = 'bidding:initialize';
    this.BIDDING__UPDATE_ACCESS_TOKEN = 'bidding:updateAccessToken';
    this.BIDDING__SEND_STORED_WALL_POSTS = 'bidding:sendStoredWallPosts';
}();

