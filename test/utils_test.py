from shopify.utils import *
from test.test_helper import TestCase
from datetime import datetime, timedelta

import jwt
import sys
if sys.version_info[0] < 3: # Backwards compatibility for python < v3.0.0
    import time

    def timestamp(date):
        return time.mktime(date.timetuple())
else:
    def timestamp(date):
        return date.timestamp()


class UtilsTest(TestCase):
    @classmethod
    def setUpClass(self):
        self.secret = "API Secret"
        self.api_key = "API key"

    @classmethod
    def setUp(self):
        current_time = datetime.now()
        self.payload = {
            "iss": 'https://test-shop.myshopify.com/admin',
            "dest": 'https://test-shop.myshopify.com',
            "aud": self.api_key,
            "sub": '1',
            "exp": timestamp((current_time + timedelta(0, 60))),
            "nbf": timestamp(current_time),
            "iat": timestamp(current_time),
            "jti": '4321',
            "sid": "abc123",
        }

    def test_SessionTokenUtility_getDecodedSessionToken_raises_if_auth_header_is_not_Bearer(self):
        authorization_header = "Bad auth header"

        with self.assertRaises(ValueError):
          SessionTokenUtility.get_decoded_session_token(authorization_header, api_key=self.api_key, secret=self.secret)

    def test_SessionTokenUtility_getDecodedSessionToken_raises_jwt_error_if_session_token_is_expired(self):
        self.payload["exp"] = timestamp((datetime.now() + timedelta(0, -10)))

        with self.assertRaises(jwt.exceptions.ExpiredSignatureError):
          SessionTokenUtility.get_decoded_session_token(
              self.build_auth_header(), api_key=self.api_key, secret=self.secret)

    def test_SessionTokenUtility_getDecodedSessionToken_raises_if_issuer_hostname_is_invalid(self):
        self.payload["iss"] = "bad_shop_hostname"

        with self.assertRaises(ValueError):
          SessionTokenUtility.get_decoded_session_token(
              self.build_auth_header(), api_key=self.api_key, secret=self.secret)

    def test_SessionTokenUtility_getDecodedSessionToken_raises_if_iss_and_dest_dont_match(self):
        self.payload["dest"] = "bad_shop.myshopify.com"

        with self.assertRaises(ValueError):
          SessionTokenUtility.get_decoded_session_token(
              self.build_auth_header(), api_key=self.api_key, secret=self.secret)

    def test_SessionTokenUtility_getDecodedSessionToken_returns_decoded_payload(self):
        decoded_payload = SessionTokenUtility.get_decoded_session_token(
            self.build_auth_header(), api_key=self.api_key, secret=self.secret)

        self.assertEqual(self.payload, decoded_payload)

    @classmethod
    def build_auth_header(self):
      mock_session_token = jwt.encode(self.payload, self.secret, algorithm="HS256")
      return "Bearer {session_token}".format(session_token=mock_session_token)