#! /usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import logging
import unittest

from tutorons.core.htmltools import HtmlDocument
from tutorons.modules.{{ app_name }}.views import detect_code


logging.basicConfig(level=logging.INFO, format="%(message)s")


class CodeDetectionTest(unittest.TestCase):

    def test_detect_foo(self):

        html_doc = HtmlDocument('\n'.join([
            "<html>",
            "  <body>",
            "    <div>",
            "      <code>import foo</code>",
            "    </div>",
            "  </body>",
            "</html>",
        ]))
        code_regions = detect_code(html_doc)

        self.assertEqual(1, len(code_regions))
        code_region = code_regions[0]
        self.assertEqual("foo", code_region.string)
        self.assertEqual("code", code_region.node.name)
        self.assertEqual(7, code_region.start_offset)
        self.assertEqual(9, code_region.end_offset)
