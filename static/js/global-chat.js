function GlobalChatCtrl ($scope, $rootScope, $http, pubSub) {
	'use strict';

	var channel = 'global';
	$scope.isGlobalChatEnabled = true;
	$scope.isGlobalChatOpen = true;
	$scope.messages = [];

	$scope.chatGrowth = function(){
		if ($scope.isGlobalChatOpen) {
			$scope.isGlobalChatOpen=false;
			$(".global-chat").data("height_growth", 0);
		}else{
			$scope.isGlobalChatOpen=true;
			$(".global-chat").data("height_growth", 67);
		};
	};

	/**
	 * Initializes global chat. Connects to global channel.
	 */
	$scope.initialize = function () {
		// Subscribe to open global chat event.
		$rootScope.$on('main:openGlobalChat', function () {
			$scope.isGlobalChatEnabled = true;
			// Subscribe to global chat communication channel.
			pubSub.subscribe({
				channel: channel,
				message: function (messages) {
					_.forEach(messages, function (message) {
						$scope.$apply(function () {
							$scope.messages.push(message.data);
						});
					});
				}
			});
		});
	};

	/**
	 * Sends message.
	 */
	$scope.sendMessage = function () {
		$http.post('/api/globalMessage/', {text: $scope.message});
		$scope.message = null;
	};
}
