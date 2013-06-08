
jQuery(document).ready(function(){

    jQuery('#activateReportAnError').bind('click',function(e){
        //activate report an error widget
        jQuery('#reportAnError').show();
    })

    jQuery('#reportAnErrorBtn').bind('click',function(e){
        //send report
        var data = {message:jQuery('#reportAnErrorMessage').val(), gameState:jQuery.toJSON(gameState)};

        jQuery.post('/api/reportAnError/', data, function(){
            console.log("ok, did it", gameState, jQuery.toJSON(gameState));
            jQuery('#reportAnError').html('Thank you!');
            setTimeout(function(){
                jQuery('#reportAnErrorBtn').hide();
                jQuery('#reportAnError').hide();
            },4000);

        });
    })

})
