#!/usr/bin/python3
import json
import shutil
import socket
import logging
import unittest
import ipaddress
import subprocess
from staslib import iputil, log, stas, trid

IP = shutil.which('ip')


class Test(unittest.TestCase):
    '''iputil.py unit tests'''

    def setUp(self):
        log.init(syslog=False)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Retrieve the list of Interfaces and all the associated IP addresses
        # using standard bash utility (ip address). We'll use this to make sure
        # iputil.get_interface() returns the same data as "ip address".
        try:
            cmd = [IP, '-j', 'address', 'show']
            p = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
            self.ifaces = json.loads(p.stdout.decode().strip())
        except subprocess.CalledProcessError:
            self.ifaces = []

    def test_get_interface(self):
        '''Check that get_interface() returns the right info'''
        ifaces = iputil.net_if_addrs()
        for iface in self.ifaces:
            for addr_entry in iface['addr_info']:
                addr = ipaddress.ip_address(addr_entry['local'])
                # Link local addresses may appear on more than one interface and therefore cannot be used.
                if not addr.is_link_local:
                    self.assertEqual(iface['ifname'], iputil.get_interface(ifaces, addr))

        self.assertEqual('', iputil.get_interface(ifaces, iputil.get_ipaddress_obj('255.255.255.255')))
        self.assertEqual('', iputil.get_interface(ifaces, ''))
        self.assertEqual('', iputil.get_interface(ifaces, None))

    def test_mac2iface(self):
        for iface in self.ifaces:
            address = iface.get('address', None)
            if address:
                self.assertEqual(iface['ifname'], iputil.mac2iface(address))

    def test_remove_invalid_addresses(self):
        good_tcp = trid.TID({'transport': 'tcp', 'traddr': '1.1.1.1', 'subsysnqn': '', 'trsvcid': '8009'})
        bad_tcp = trid.TID({'transport': 'tcp', 'traddr': '555.555.555.555', 'subsysnqn': '', 'trsvcid': '8009'})
        any_fc = trid.TID({'transport': 'fc', 'traddr': 'blah', 'subsysnqn': ''})
        bad_trtype = trid.TID({'transport': 'whatever', 'traddr': 'blah', 'subsysnqn': ''})

        l1 = [
            good_tcp,
            bad_tcp,
            any_fc,
            bad_trtype,
        ]
        l2 = stas.remove_invalid_addresses(l1)

        self.assertNotEqual(l1, l2)

        self.assertIn(good_tcp, l2)
        self.assertIn(any_fc, l2)  # We currently don't check for invalid FC (all FCs are allowed)

        self.assertNotIn(bad_tcp, l2)
        self.assertNotIn(bad_trtype, l2)

    def test__data_matches_ip(self):
        self.assertFalse(iputil.ip_equal(None, None))


if __name__ == "__main__":
    unittest.main()
