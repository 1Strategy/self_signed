"""Self Signed Tests

This module tests the functionality of the Self_Signed module.
"""

# create_credential_scope
# create_authorization_header
# create_signed_headers
# build_headers


import pytest
import self_signed

class TestSelfSigned(object):

    """Test the functionality of the SelfSigned module"""

    def test_create_canonical_req(self):
        """Test the ouput of create_canonical_req"""

        request = self_signed.create_canonical_req()
        assert "content-type:" in request
        assert "x-amz-date:" in request
        assert "host" in request
        assert "POST" in request


    def test_payload_hash(self):
        """Test the output of payload_hash"""