import shopify
from test.test_helper import TestCase
from pyactiveresource.activeresource import ActiveResource


class FulfillmentOrderTest(TestCase):
    def test_get_fulfillment_order(self):
        self.fake("fulfillment_orders/1046000778", method="GET", body=self.load_fixture("fulfillment_order"))
        fulfillment_order = shopify.FulfillmentOrder.find(1046000778)
        self.assertEqual(690933842, fulfillment_order.shop_id)
        self.assertEqual("open", fulfillment_order.status)
