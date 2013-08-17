function Event(event, data, sender, receiver, transport, timestamp, id) {
    this.event = event;
    this.data = data;
    this.sender = sender;
    this.receiver = receiver;
    this.transport = transport;
    this.timestamp = timestamp;
    this.id = id;
};
// constants for messages and events
Event.prototype.TRANSPORT = new function () {
    this.PUBNUB = 'pubnub';
    this.REQUEST = 'request';
    this.COMBINED = 'combined';
}();

Event.prototype.SENDER = new function () {
    this.CLIENT_FB = 'client-fb-';
}();

Event.prototype.RECEIVER = new function () {
    this.SERVER = 'server';
}();

Event.prototype.EVENT = new function () {
    this.BIDDING__INITIALIZE = 'bidding:initialize';
}();

console.log('holaaa >-----------------');