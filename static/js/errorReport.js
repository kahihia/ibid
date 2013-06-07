
jQuery(document).ready(function(){

    jQuery('#activateReportAnError').bind('click',function(e){
        //activate report an error widget
        jQuery('#reportAnError').show();
    })

    jQuery('#reportAnErrorBtn').bind('click',function(e){
        //send report
        console.log("ok, did it", gameState, jQuery.toJSON(gameState));

        jQuery.post('/api/reportAnError/', {message:jQuery('#reportAnErrorMessage').val(), gameState:jQuery.toJSON(gameState)});
    })


})
