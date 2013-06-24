
$(function() {
	
//	$('#id_item').autocomplete({
//		source: "/item_info/",
//		minLength:2,
//		select: function(event, ui){
//			get_item_price();
//		}
//	});
	
	$('#id_item').combobox();
	$('#id_item').change(get_item_price);
	
	$('<a id="x3link" href="#"> x3</a>').insertAfter($('#id_precap_bids'));
	$('<a id="x2link" href="#"> x2</a>').insertAfter($('#id_precap_bids'));
	
});

function get_item_price(){
	data = {'item_id' : $('#id_item').val()};
	$.post('/item_price/', data, update_precap_field, "json");
}

function update_precap_field(data){
	$('#id_precap_bids').val(data.price);
	
	$('#x3link').click(function(){
		$('#id_precap_bids').val(data.price * 3)
	});
	
	$('#x2link').click(function(){
		$('#id_precap_bids').val(data.price * 2)
	});
}

function dismissRelatedLookupPopup(win, chosenId) {
	var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
        elem.value += ',' + chosenId;
    } else {
        document.getElementById(name).value = chosenId;
        get_item_price();
    }
    win.close();
}