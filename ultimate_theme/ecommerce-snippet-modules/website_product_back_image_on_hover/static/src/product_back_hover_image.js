function load_image(prod_id)
{
	var prod_image_id = prod_id.getAttribute('prod-id');
	var prod_hover = prod_id.getAttribute('prod-hover');
	if (prod_hover){
	    $('div.oe_lines_image').find("[prod-id='" + prod_image_id + "']").attr('src', '/web/image/product.template/'+prod_id.getAttribute('prod-id')+'/product_back_hover_image');
	}
}

function unload_image(prod_id)
{
	var prod_image_id = prod_id.getAttribute('prod-id');
	$('div.oe_lines_image').find("[prod-id='" + prod_image_id + "']").attr('src', '/web/image/product.template/'+prod_id.getAttribute('prod-id')+'/image_1920');
}
