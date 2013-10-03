$(window).load(function() {
  $("#tour-steps").joyride({
    autoStart: true,
    template: {
    	link: '<a href="#close" class="joyride-close-tip">×</a>',
      button: '<a href="#" class="joyride-next-tip btn"></a>',
      wrapper: '<div class="joyride-content-wrapper" role="dialog"><img class="joyride-kenny" src="/static/images/tooltip-action-kenny.png" alt=""></div>'
    }
  });
});
