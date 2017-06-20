#! /usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import logging
import unittest

from tutorons.modules.{{ app_name }}.views import explain_code


logging.basicConfig(level=logging.INFO, format="%(message)s")


class FooExplanationTest(unittest.TestCase):

    def test_explain_that_foos_do_bar(self):
        explanation = explain_code("foo")
        self.assertIn("bar", explanation)
