#!/usr/bin/python3
import os
import logging
import unittest
from staslib import conf

TEST_DIR = os.path.dirname(__file__)
EXPECTED_DCS = [
    {
        'subsysnqn': 'nqn.2014-08.org.nvmexpress.discovery',
        'traddr': '100.71.103.50',
        'transport': 'tcp',
        'trsvcid': '8009',
        'host-nqn': 'nqn.1988-11.com.dell:PowerEdge.R760.1234567',
    }
]
EXPECTED_IOCS = [
    {
        'data-digest': False,
        'hdr-digest': False,
        'subsysnqn': 'nqn.1988-11.com.dell:powerstore:00:2a64abf1c5b81F6C4549',
        'traddr': '100.71.103.48',
        'transport': 'tcp',
        'trsvcid': '4420',
        'host-nqn': 'nqn.1988-11.com.dell:PowerEdge.R760.1234567',
    },
    {
        'data-digest': False,
        'hdr-digest': False,
        'subsysnqn': 'nqn.1988-11.com.dell:powerstore:00:2a64abf1c5b81F6C4549',
        'traddr': '100.71.103.49',
        'transport': 'tcp',
        'trsvcid': '4420',
        'host-nqn': 'nqn.1988-11.com.dell:PowerEdge.R760.1234567',
    },
]


class Test(unittest.TestCase):
    """Unit tests for class NbftConf"""

    def test_dir_with_nbft_files(self):
        conf.NbftConf.destroy()  # Make sure singleton does not exist
        with self.assertLogs(logger=logging.getLogger(), level='DEBUG') as captured:
            nbft_conf = conf.NbftConf(TEST_DIR)
            self.assertNotEqual(-1, captured.records[0].getMessage().find("NBFT location(s):"))
            self.assertEqual(nbft_conf.dcs, EXPECTED_DCS)
            self.assertEqual(nbft_conf.iocs, EXPECTED_IOCS)

    def test_dir_without_nbft_files(self):
        conf.NbftConf.destroy()  # Make sure singleton does not exist
        with self.assertNoLogs(logger=logging.getLogger(), level='DEBUG'):
            nbft_conf = conf.NbftConf('/tmp')
            self.assertEqual(nbft_conf.dcs, [])
            self.assertEqual(nbft_conf.iocs, [])


if __name__ == "__main__":
    unittest.main()
