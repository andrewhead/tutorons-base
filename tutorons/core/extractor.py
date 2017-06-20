#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import re
from slimit.lexer import Lexer as JsLexer
import copy

from tutorons.core.util import get_descendants


logging.basicConfig(level=logging.INFO, format="%(message)s")
RARE_CHARACTER = '\u3222'  # A character we never expect to appear on an HTML page


class Region(object):
    '''
    Region of text that might be explainable.
    Properties:
    * node: an HTML node (BeautifulSoup subclass)
    * start_offset: character index where the region begins
    * end_offset: character index where the region ends
    * string: text of the region
    '''
    def __init__(self, node, start_offset, end_offset, string):
        self.node = node
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.string = string

    def __str__(self):
        return '<%s>[%d,%d]: "%s"' % \
            (self.node.name, self.start_offset, self.end_offset, self.string)

    def __repr__(self):
        return str(self)


class LineExtractor(object):

    def extract(self, node):
        ''' Given HTML node, extract all line Regions. '''

        text = node.text

        regions = []
        char_index = 0
        for line in text.split('\n'):
            first_char = char_index
            last_char = char_index + len(line) - 1
            r = Region(node, first_char, last_char, line)
            regions.append(r)
            char_index += (len(line) + 1)  # every line has at least 1 char: the newline

        return regions


class JavascriptStringExtractor(object):

    def extract(self, node):

        lexer = JsLexer()
        lexer.input(node.text)

        regions = []
        while True:
            try:
                tok = lexer.token()
                if not tok:
                    break
                if tok.type == "STRING":
                    start_char = tok.lexpos + 1
                    string = tok.value[1:-1]
                    end_char = start_char + len(string) - 1
                    r = Region(node, start_char, end_char, string)
                    regions.append(r)
            except (TypeError, AttributeError):
                logging.warn("Failed to parse text: %s...", node.text[:100])
                break

        return regions
