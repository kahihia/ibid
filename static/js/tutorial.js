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

tutorialImages = {
    slide1: '/static/images/tutorial/1.png',
    slide2: '/static/images/tutorial/2.png',
    slide3: '/static/images/tutorial/3.png',
    slide4: '/static/images/tutorial/4.png',
    slide5: '/static/images/tutorial/5.png',
    slide6: '/static/images/tutorial/6.png',
    slide7: '/static/images/tutorial/7.png',
    slide8: '/static/images/tutorial/8.png',
    slide9: '/static/images/tutorial/9.png',
    slide10: '/static/images/tutorial/10.png',
    slide11: '/static/images/tutorial/11.png',
    slide12: '/static/images/tutorial/12.png',
    slide13: '/static/images/tutorial/13.png',
    slide14: '/static/images/tutorial/14.png',
    slide15: '/static/images/tutorial/15.png'
    }

preloadImage(tutorialImages.slide1);
preloadImage(tutorialImages.slide2);
preloadImage(tutorialImages.slide3);
preloadImage(tutorialImages.slide4);
preloadImage(tutorialImages.slide5);
preloadImage(tutorialImages.slide6);
preloadImage(tutorialImages.slide7);
preloadImage(tutorialImages.slide8);
preloadImage(tutorialImages.slide9);
preloadImage(tutorialImages.slide10);
preloadImage(tutorialImages.slide11);
preloadImage(tutorialImages.slide12);
preloadImage(tutorialImages.slide13);
preloadImage(tutorialImages.slide14);
preloadImage(tutorialImages.slide15);

var tutorialActive = false;
function initTutorial(){

    setTimeout(function(){TweenLite.to('#tutorial-dialog', 1, {opacity:1,left:'0px',ease:Back.easeOut});},600);
    //TweenLite.fromTo('#tutorial-dialog', 1, {scale:0},{scale:1});

    jQuery('#tutorial-dialog').bind('tutorialEventStart', function(e){displayTutorial({img:tutorialImages.slide1,  nextEvent:'tutorialEvent1'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent1', function(e){displayTutorial(    {img:tutorialImages.slide2,  prevEvent:'tutorialEventStart',  nextEvent:'tutorialEvent2'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent2', function(e){displayTutorial(    {img:tutorialImages.slide3,  prevEvent:'tutorialEvent1',  nextEvent:'tutorialEvent3'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent3', function(e){displayTutorial(    {img:tutorialImages.slide4,  prevEvent:'tutorialEvent2',  nextEvent:'tutorialEvent4'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent4', function(e){displayTutorial(    {img:tutorialImages.slide5,  prevEvent:'tutorialEvent3',  nextEvent:'tutorialEvent5'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent5', function(e){displayTutorial(    {img:tutorialImages.slide6,  prevEvent:'tutorialEvent4',  nextEvent:'tutorialEvent6'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent6', function(e){displayTutorial(    {img:tutorialImages.slide7,  prevEvent:'tutorialEvent5',  nextEvent:'tutorialEvent7'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent7', function(e){displayTutorial(    {img:tutorialImages.slide8,  prevEvent:'tutorialEvent6',  nextEvent:'tutorialEvent8'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent8', function(e){displayTutorial(    {img:tutorialImages.slide9,  prevEvent:'tutorialEvent7',  nextEvent:'tutorialEvent9'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent9', function(e){displayTutorial(    {img:tutorialImages.slide10,  prevEvent:'tutorialEvent8',  nextEvent:'tutorialEvent10'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent10', function(e){displayTutorial(   {img:tutorialImages.slide11,  prevEvent:'tutorialEvent9',  nextEvent:'tutorialEvent11'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent11', function(e){displayTutorial(   {img:tutorialImages.slide12,  prevEvent:'tutorialEvent10',  nextEvent:'tutorialEvent12'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent12', function(e){displayTutorial(   {img:tutorialImages.slide13,  prevEvent:'tutorialEvent11',  nextEvent:'tutorialEvent13'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent13', function(e){displayTutorial(   {img:tutorialImages.slide14,  prevEvent:'tutorialEvent12',  nextEvent:'tutorialEvent14'});});
    jQuery('#tutorial-dialog').bind('tutorialEvent14', function(e){displayTutorial(   {img:tutorialImages.slide15,  prevEvent:'tutorialEvent13',  nextEvent:'tutorialEventFinish'});});
    jQuery('#tutorial-dialog').bind('tutorialEventFinish', hideTutorial);

    jQuery('#tutorial-dialog').trigger('tutorialEventStart');

    jQuery('.close','#overlay-tutorial').click(hideTutorial);
}

function displayTutorial(data){
    dataDefault = {
        buttonText: 'next',
        nextEvent: undefined,
        prevEvent: undefined,
        img: 'img1.jpg'
    };

    jQuery.extend(dataDefault, data);

    showOverlayTutorial();

    TweenLite.to(('.tutorial-img','#tutorial-dialog'), 0.2, {left:2000, opacity: 0});
    jQuery('.tutorial-img','#tutorial-dialog').attr('src', dataDefault.img);
    setTimeout(function(){ jQuery('.tutorial-img','#tutorial-dialog').attr('src', dataDefault.img);TweenLite.fromTo(('.tutorial-img','#tutorial-dialog'), 0.2, {left:-1000, opacity: 0},{left:0, opacity: 1});},200);

    jQuery('#next','#tutorial-dialog').unbind('click');
    jQuery('#prev','#tutorial-dialog').unbind('click');

    if(typeof dataDefault.nextEvent != 'undefined'){
        jQuery('#next','#tutorial-dialog').css('opacity',1);
        jQuery('#next','#tutorial-dialog').bind('click',function(e){
            console.log(dataDefault['nextEvent']);
            jQuery('#tutorial-dialog').trigger(dataDefault['nextEvent']);
        })
    }else{
        jQuery('#next','#tutorial-dialog').css('opacity',0);
    }

    if(typeof dataDefault.prevEvent != 'undefined'){
        jQuery('#prev','#tutorial-dialog').css('opacity',1);
        jQuery('#prev','#tutorial-dialog').bind('click',function(e){
            console.log(dataDefault['prevEvent']);
            jQuery('#tutorial-dialog').trigger(dataDefault['prevEvent']);
        })
    }else{
        jQuery('#prev','#tutorial-dialog').css('opacity',0);
    }

}

function hideTutorial(){
    TweenLite.to('#tooltip-dialog', 0.2, {left:'-800px'});
    //setTimeout(function(){jQuery('#tutorial-dialog').show()}, 400);

    hideOverlayTutorial();
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

function showOverlayTutorial(){
    jQuery('#overlay-tutorial').show();
    TweenLite.to('#overlay-tutorial', 0.6, {opacity:1});
}

function hideOverlayTutorial(){
    TweenLite.to('#overlay-tutorial', 0.6, {opacity:0, onComplete:function(){jQuery('#overlay-tutorial').hide()}});
}

window.onload = function(){
    //initTutorial();
    jQuery('#interactiveTutotialBtn').click(function(e){initTutorial();});
}

