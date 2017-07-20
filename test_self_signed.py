"""Self Signed Tests

This module tests the functionality of the Self_Signed module.
"""


import datetime
import self_signed

class TestSelfSigned(object):
    """Test the functionality of the SelfSigned module"""
    SERVICE = 'es'
    REGION = 'us-west-2'
    TIME = datetime.datetime.utcnow()
    AMZ_DATE = TIME.strftime('%Y%m%dT%H%M%SZ')
    DATE_STAMP = "20170720"

    def test_create_canonical_req(self):
        """Test the ouput of create_canonical_req"""

        request = self_signed.create_canonical_req()
        assert "content-type:" in request
        assert "x-amz-date:" in request
        assert "host" in request


    def test_create_credential_scope(self):
        """Test the output of create_credential_scope"""

        scope = self_signed.create_credential_scope()
        assert scope == "20170720/us-west-2/es/aws4_request"

    
    def test_build_headers(self):
        """Test the output of build_headers"""

        headers = self_signed.build_headers()
        assert 'Content-Length' in headers
        assert 'X-Amz-Date' in headers
        assert 'Host' in headers
        assert 'X-Amz-Security-Token' in headers
        assert 'Content-Type' in headers
        assert 'Authorization' in headers