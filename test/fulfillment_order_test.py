import shopify
from test.test_helper import TestCase
from pyactiveresource.activeresource import ActiveResource


class FulfillmentOrderTest(TestCase):
    def test_get_fulfillment_order(self):
        self.fake("fulfillment_orders/1046000778", method="GET", body=self.load_fixture("fulfillment_order"))
        fulfillment_order = shopify.FulfillmentOrder.find(1046000778)
        self.assertEqual(690933842, fulfillment_order.shop_id)
        self.assertEqual("open", fulfillment_order.status)

    def test_get_fulfillment_order_with_order_id(self):
        self.fake("orders/450789469/fulfillment_orders", method="GET", body=self.load_fixture("fulfillment_orders"))
        fulfillment_orders = shopify.FulfillmentOrder.find(order_id=450789469)
        self.assertIsInstance(fulfillment_orders[0], shopify.FulfillmentOrder)
        self.assertEqual(450789469, fulfillment_orders[0].order_id)
        self.assertEqual(1046000777, fulfillment_orders[0].id)
