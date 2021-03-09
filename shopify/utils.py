import jwt
import re
import urllib


class SessionTokenUtility():
    ALGORITHM = "HS256"
    PREFIX = 'Bearer '
    REQUIRED_FIELDS = ['iss', 'dest', 'sub', 'jti', 'sid']
  
    @classmethod
    def get_decoded_session_token(self, authorization_header, api_key, secret):
        session_token = self.__extract_session_token(authorization_header)
        decoded_payload = self.__decode_session_token(session_token, api_key, secret)
        self.__validate_issuer(decoded_payload)
  
        return decoded_payload
  
    @classmethod
    def __extract_session_token(self, authorization_header):
        if not authorization_header.startswith(self.PREFIX):
            raise ValueError() # TODO: Throw a more meaningful error
  
        return authorization_header[len(self.PREFIX):]
  
    @classmethod
    def __decode_session_token(self, session_token, api_key, secret):
        return jwt.decode(
            session_token,
            secret,
            audience=api_key,
            algorithms=[self.ALGORITHM],
            options={'require': self.REQUIRED_FIELDS}
        )
  
    @classmethod
    def __validate_issuer(self, decoded_payload):
        self.__validate_issuer_hostname(decoded_payload)
        self.__validate_issuer_and_dest_match(decoded_payload)
  
    def __validate_issuer_hostname(decoded_payload):
        hostname_pattern = r'[a-z0-9][a-z0-9-]*[a-z0-9]'
        shop_domain_re = re.compile(fr'^https://{hostname_pattern}\.myshopify\.com/$')
  
        issuer_root = urllib.parse.urljoin(decoded_payload['iss'], '/')
  
        if not shop_domain_re.match(issuer_root):
            raise ValueError() # TODO: Throw a more meaningful error
  
    def __validate_issuer_and_dest_match(decoded_payload):
        issuer_root = urllib.parse.urljoin(decoded_payload['iss'], '/')
        dest_root = urllib.parse.urljoin(decoded_payload['dest'], '/')
  
        if issuer_root != dest_root:
            raise ValueError() # TODO: Throw a more meaningful error
  