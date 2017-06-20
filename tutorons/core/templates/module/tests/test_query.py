#! /usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import logging
import unittest
from django.core.urlresolvers import reverse
from django.test import Client

logging.basicConfig(level=logging.INFO, format="%(message)s")


class QueryServerForScanningTest(unittest.TestCase):

    def test_response_received_after_call_to_scan(self):

        client = Client()
        server_response = client.post(
            reverse('{{ app_name }}:scan'),
            data={
                'origin': 'www.test.com',
                'document': '\n'.join([
                    # Change the lines below if you want to simulate a
                    # different page's HTML getting uploaded for scanning.
                    "<html>",
                    "  <body>",
                    "    <p>Hello, world.</p>",
                    "  </body>",
                    "</html>",
                ])
            })

        # The actual test doesn't really test anything, because we wanted
        # to make it easy to modify the project template without breaking
        # this test.  You can change the assertions to check on more
        # complicated behavior than just getting a response.
        self.assertIsNotNone(server_response)
