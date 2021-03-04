from ..base import ShopifyResource


class FulfillmentOrder(ShopifyResource):
    _prefix_source = "orders/$order_id/"

    @classmethod
    def _prefix(cls, options={}):
        order_id = options.get("order_id")
        if order_id:
            return "%s/orders/%s" % (cls.site, order_id)
        else:
            return cls.site
