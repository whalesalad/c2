import sys
import pprint
import socket

from datetime import datetime

import netaddr
from OpenSSL import SSL

class SSLCertificateService(object):
    """
    A service used for validating the SSL certificates of remote machines.

    Call svc.validate(list_of_addresses) to get the following info:
        - start: the 'not before' time of the cert
        - end: the 'not after' time of the cert
        - common_name: the domain/common_name of the cert
        - days_left: the days remaining until expiration
        - expired: boolean for whether or not the cert has expired

    """

    def __init__(self, method=None):
        self.context = SSL.Context(SSL.TLSv1_METHOD)
        self.context.set_options(SSL.OP_NO_SSLv2)
        # self.context.set_verify(SSL.VERIFY_NONE, self.callback)

    def validate(self, addresses):
        return [ self.validate_address(a) for a in addresses ]

    def callback(self, conn, cert, errno, depth, result):
        pprint.pprint(args)

    def parse_timestamp(self, timestamp):
        return datetime.strptime(timestamp, '%Y%m%d%H%M%SZ')

    def validate_address(self, address):
        response = {
            'address': address,
            'success': True
        }

        try:
            ip_address = netaddr.IPAddress(address)
        except netaddr.AddrFormatError:
            response['success'] = False
            response['reason'] = 'Not a valid IP Address.'
            return response

        sock = socket.socket()
        conn = SSL.Connection(self.context, sock)

        try:
            conn.connect((address, 443))
        except:
            conn.shutdown()
            response['success'] = False
            response['reason'] = 'No route to host. Not running on port 443?'
            return response

        conn.do_handshake()

        cert = conn.get_peer_certificate()

        conn.close()

        response['common_name'] = cert.get_subject().commonName.decode()

        response['expired'] = cert.has_expired()
        response['start'] = self.parse_timestamp(cert.get_notBefore())
        response['end'] = self.parse_timestamp(cert.get_notAfter())

        response['days_left'] = int((response['end'] - datetime.utcnow()).days)

        return (address, response)