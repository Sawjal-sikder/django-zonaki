from django import template
register = template.Library()

@register.filter
def low_price_product(value):
    product_dict = {}
    for i in value:
        if i.product and i.flashsale_price:
            product_id = i.product.id
            if product_id not in product_dict or i.flashsale_price < product_dict[product_id].flashsale_price:
                product_dict[product_id] = i

    product_list = list(product_dict.values())
    return product_list

