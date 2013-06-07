/**
 * Created with PyCharm.
 * User: dnuske
 * Date: 5/27/13
 * Time: 6:55 PM
 * To change this template use File | Settings | File Templates.
 */

TweenLite.selector = jQuery;


function initWelcome(){
    showOverlay();
    jQuery('#welcome').center();

    setTimeout(function(){jQuery('#welcome').show(); TweenLite.from('#welcome', 1, {left:'-800px',ease:Back.easeOut});}, 1000);

    jQuery('.btn-welcome','#welcome').bind('click', function(e){
            TweenLite.to('#welcome', 0.4, {left:'-800px'});
            setTimeout(function(){jQuery('#welcome').hide();},500)
            hideOverlay();
            initTutorial();
            });

}

tutorialTexts = {
    slide2: 'Here you can see all available interactive auctions. Click <div class="btn-red-tutorial">start bidding</div> to participate',
    slide3: 'Here you can see how many players are participating. You can chill out now, the auction has not started yet. It will start when completion reaches 100%.',
    slide5: 'This is the auctioneer panel, Here I will inform you about who is joining the auction. You can click their names and see their FB profiles. Maybe someone you know has joined!',
    slide6: "This is the chat panel. Here you can chat with all of the bidders whether they are your friends or not!  Isn't this exciting?",
    slide7: 'Here you can see how many tokens you are spending to acquire bids. Each bid the bidders add raises the "completion." Quick...add <div class="btn-bid-plus-tutorial">+</div> more bids! until the auction starts',
    slide8: 'There we go. The auction has already started, Strategically click bid before the countdown hits 0.  Last Bid in... wins!',
    slide9: 'Here are the bids you previously bought for tokens. You choose how many, make a decision and plan your strategy. What is your lucky number?',
    slide10: "In the auctioneer panel, I'll  tell you who placed the last bid.  IIf  no one else bids the current bidder will win the prize.",
    slide11: 'Congratulations! That was your first auction. You have plenty of tokens to keep playing.',
    //slide12: 'You can either play for tokens or for real prizes like iPads, computers, etc...',
    //slide13: 'Playing for tokens allows you to win tokens that you can redeem for credits to play for real items.',
    //slide14: 'When playing for items, you are able to win actual items by using credits.',
    slide15: 'I will let you explore the rest. Remember you have the <a target="_blank" href="http://www.facebook.com/ibidgames">fan page</a> to ask anything, and you can run this tutorial again by clicking here.'
   }

var tutorialAuctionId = 0;
var tutorialActive = false;
function initTutorial(){

    tutorialAuctionId = determineFirstPrecapAuctionId();
    tutorialActive = true;


    setTimeout(function(){jQuery('#tooltip-help').show();TweenLite.from('#tooltip-help', 1, {left:'-800px',ease:Back.easeOut});},1000);
    //TweenLite.fromTo('#tooltip-help', 1, {scale:0},{scale:1});

    jQuery('#tooltip-help').bind('tutorialEventStart', function(e){displayTutorial(tutorialAuctionId,{text:tutorialTexts.slide2,  buttonDisplay:false, buttonEvent:'tutorialEvent2',     position:{top:-75, left:274},                                                                showOverlay:true, enlightSelector: '#auction-top',endefaultSelector:undefined });});
    jQuery('#tooltip-help').bind('tutorialEvent2', function(e){displayTutorial(    tutorialAuctionId,{text:tutorialTexts.slide3,  buttonDisplay:true, buttonEvent:'tutorialEvent2c',     position:{top:-145,left:94},   referencePositionFunction:determineFirstMineAuctionPosition,  showOverlay:true, enlightSelector: '#auction',endefaultSelector:'#auction-top'});});
    jQuery('#tooltip-help').bind('tutorialEvent2c', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide5,  buttonDisplay:true, buttonEvent:'tutorialEvent2d',     position:{top:-55, left:-111}, referencePositionFunction:determineFirstMineAuctionPosition,  showOverlay:true, enlightSelector: '#auction',endefaultSelector:undefined});});
    jQuery('#tooltip-help').bind('tutorialEvent2d', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide6,  buttonDisplay:true, buttonEvent:'tutorialEvent2e',     position:{top:40,  left:-111}, referencePositionFunction:determineFirstMineAuctionPosition,  showOverlay:true, enlightSelector: '#auction',endefaultSelector:undefined});});
    jQuery('#tooltip-help').bind('tutorialEvent2e', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide7,  buttonDisplay:false, buttonEvent:'tutorialEvent3',     position:{top:-101,left:284},  referencePositionFunction:determineFirstMineAuctionPosition});});
    jQuery('#tooltip-help').bind('tutorialEvent3', function(e){displayTutorial(    tutorialAuctionId,{text:tutorialTexts.slide8,  buttonDisplay:true, buttonEvent:'tutorialEvent4',      position:{top:-130,left:194},  referencePositionFunction:determineFirstMineAuctionPosition});});
    jQuery('#tooltip-help').bind('tutorialEvent4', function(e){displayTutorial(    tutorialAuctionId,{text:tutorialTexts.slide9,  buttonDisplay:true, buttonEvent:'tutorialEvent4b',     position:{top:-130,left:334},  referencePositionFunction:determineFirstMineAuctionPosition});});
    jQuery('#tooltip-help').bind('tutorialEvent4b', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide10, buttonDisplay:false, buttonEvent:'tutorialEvent5',     position:{top:-10, left:-111}, referencePositionFunction:determineFirstMineAuctionPosition});});
    jQuery('#tooltip-help').bind('tutorialEvent5', function(e){displayTutorial(    tutorialAuctionId,{text:tutorialTexts.slide11, buttonDisplay:true, buttonEvent:'tutorialEvent5e',     position:{top:-130,left:194},  referencePositionFunction:determineFirstMineAuctionPosition});});
    //jQuery('#tooltip-help').bind('tutorialEvent5b', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide12, buttonDisplay:true, buttonEvent:'tutorialEvent5c',     position:{top:-116,left:-106}, referencePositionFunction:determineBtnTokenPosition});});
    //jQuery('#tooltip-help').bind('tutorialEvent5c', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide13, buttonDisplay:true, buttonEvent:'tutorialEvent5d',     position:{top:-116,left:-106}, referencePositionFunction:determineBtnTokenPosition});});
    //jQuery('#tooltip-help').bind('tutorialEvent5d', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide14, buttonDisplay:true, buttonEvent:'tutorialEvent5e',     position:{top:-116,left:-106}, referencePositionFunction:determineBtnTokenPosition});});
    jQuery('#tooltip-help').bind('tutorialEvent5e', function(e){displayTutorial(   tutorialAuctionId,{text:tutorialTexts.slide15, buttonDisplay:true, buttonEvent:'tutorialEventFinish', position:{top:-112,left:224},  referencePositionFunction:determineBtnTokenPosition});});
    jQuery('#tooltip-help').bind('tutorialEventFinish', function(e){TweenLite.to('#tooltip-help', 0.4, {left:'-800px'}); tutorialActive = true;});
    //jQuery('#tooltip-help').trigger('tutorialEvent1')

    jQuery('#tooltip-help').trigger('tutorialEventStart');
}

function displayTutorial(referenceAuctionId, data){
    dataDefault = {
        text: 'test',
        buttonDisplay: false,
        buttonText: 'next',
        buttonEvent: '-',
        position: {left:0,top:0},
        referencePositionFunction:determineFirstPrecapAuctionPosition,
        showOverlay:false,
        enlightSelector: undefined,
        endefaultSelector:undefined,
        arrowPoition:undefined
    };

    jQuery.extend(dataDefault, data);
    console.log('----');
    console.log(dataDefault);

        var referencePosition = dataDefault.referencePositionFunction(referenceAuctionId);

        jQuery('.text','#tooltip-help').html(dataDefault['text']);
        if(dataDefault.buttonDisplay){
            jQuery('#btn-tutorial','#tooltip-help').show();
            jQuery('#btn-tutorial','#tooltip-help').unbind('click');
            jQuery('#btn-tutorial','#tooltip-help').bind('click',function(e){jQuery('#btn-tutorial','#tooltip-help').trigger(dataDefault['buttonEvent']);})
        }else{
            jQuery('#btn-tutorial','#tooltip-help').hide();
        }
        console.log('dataDefault',dataDefault);
        console.log('data',data);
        TweenLite.to('#tooltip-help', 0.2, {left:referencePosition.left+dataDefault.position.left, top: referencePosition.top+dataDefault.position.top,ease:Back.easeOut});
        //jQuery('#tooltip-help').css("left",referencePosition.left+dataDefault.position.left);
        //jQuery('#tooltip-help').css("top",referencePosition.top+dataDefault.position.top);

        if ( ovarlayCount >0){hideOverlay();};
        if (dataDefault.showOverlay){
            //show overlay
            showOverlay();
            //enlight selector
            if(typeof dataDefault.enlightSelector != 'undefined'){jQuery(dataDefault.enlightSelector).css('z-index',1001);}
            if(typeof dataDefault.endefaultSelector != 'undefined'){jQuery(dataDefault.endefaultSelector).css('z-index','inherit');}
        }

    /*catch(err){
    //Handle errors here
        if ( ovarlayCount >0){hideOverlay();};
        console.log('error trapped',err, 'closing tutorial');
        jQuery('#tooltip-help').hide();
    }*/
}

function determineFirstPrecapAuctionId(){
    console.log('------determineFirstPrecapAuctionId----');
    console.log(jQuery(jQuery('.auction-id', '#upcoming-auctions')[0]).val());
    return jQuery(jQuery('.auction-id', '#upcoming-auctions')[0]).val();
}

function determineFirstPrecapAuctionPosition(auctionId){
    console.log('-----determineFirstPrecapAuctionPosition-----');
    console.log("input[value='"+auctionId+"']")
    console.log(jQuery(jQuery(jQuery("input[value='"+auctionId+"']", '#upcoming-auctions')[0]).next()[0]).offset());
    //main-wrapper
    return jQuery(jQuery(jQuery("input[value='"+auctionId+"']", '#upcoming-auctions')[0]).next()[0]).offset();
}

function determineFirstMineAuctionPosition(auctionId){
    console.log('-----determineFirstMineAuctionPosition-----');
    console.log("input[value='"+auctionId+"']")
    console.log(jQuery(jQuery(jQuery("input[value='"+auctionId+"']", '#user-auctions')[0]).next()[0]).offset());
    return jQuery(jQuery(jQuery("input[value='"+auctionId+"']", '#user-auctions')[0]).next()[0]).offset();
}

function determineBtnTokenPosition(auctionId){
    console.log('-----determineBtnTokenPosition-----');
    console.log(jQuery(jQuery('.btn-tokens')[0]).offset());
    return jQuery(jQuery('.btn-tokens')[0]).offset();
}



window.onload = function(){
    //initTutorial();
    jQuery('#interactiveTutotialBtn').click(function(e){initTutorial();});
}



