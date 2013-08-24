function GlobalChatCtrl ($scope, $rootScope, $http, pubSub) {
	'use strict';

	var channel = 'global';
	$scope.isGlobalChatEnabled = true;
	$scope.isGlobalChatOpen = false;
	$scope.heightGrowth=0;
	$scope.messages = [];

	$scope.chatGrowth = function(){
		if ($scope.isGlobalChatOpen) {
			$scope.isGlobalChatOpen=false;
			$scope.heightGrowth= 0;
		}else{
			$scope.isGlobalChatOpen=true;
			$scope.heightGrowth= 67;
		};
	};

	/**
	 * Initializes global chat. Connects to global channel.
	 */
	$scope.initialize = function () {

		// Subscribe to open global chat event.
		$rootScope.$on('main:openGlobalChat', function (event, data) {
			$scope.isGlobalChatEnabled = true;
            //expand or keep it down.
            console.log(data);
            if(data.open){
                $scope.chatGrowth();
            };
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

	$scope.chatPosition=function () {
		FB.Canvas.getPageInfo(function(pageInfo){
			var num1 = parseInt(pageInfo.scrollTop) -  parseInt(pageInfo.offsetTop);
			var num2 = parseInt(pageInfo.clientHeight) - $("global-chat").outerHeight();
			var num3 = $scope.heightGrowth;
			if (num3) {
				num3+=$(".global-chat .chat-list").height();
			}
			$(".global-chat").animate({top: ((num1 + num2) - num3) }, 0);
			setTimeout($scope.chatPosition, 100);
		});
	};
	
}
