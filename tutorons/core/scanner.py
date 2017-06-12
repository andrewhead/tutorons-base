#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import re
import copy
from bs4 import Tag


logging.basicConfig(level=logging.INFO, format="%(message)s")
RARE_CHARACTER = '\u3222'  # A character we never expect to appear on an HTML page


class InvalidCommandException(Exception):
    ''' Exception when an invalid command cannot be read or processed. '''

    def __init__(self, cmd, exception):
        self.cmd = cmd
        self.exception = exception


class NodeScanner(object):
    ''' Scans document for explainable regions inside node types.'''

    def __init__(self, extractor, tags):
        self.extractor = extractor
        self.tags = tags

    def scan(self, document):
        return self.visit(document)

    def visit(self, node):

        regions = []
        children_with_regions = []

        if hasattr(node, 'children'):
            for c in node.children:
                child_regions = self.visit(c)
                regions.extend(child_regions)
                if len(child_regions) >= 1:
                    children_with_regions.append(c)

        # To avoid sensing the same explainable region twice, we literally
        # 'blank out' tags in which regions have been detected when examining
        # their parent for regions.
        if type(node) is Tag and node.name in self.tags and self.extract_allowed(node):
            node_clone = copy.copy(node)
            for c in node_clone.children:
                if c in children_with_regions:
                    c.replace_with(' ' * len(c.text))

            # As the clone is detached from the rest of the document, we need
            # to reset the region's parent node to the original node, even though
            # the text and position of the region found is the same
            node_regions = self.extractor.extract(node_clone)
            for r in node_regions:
                r.node = node

            regions.extend(node_regions)

        return regions

    def extract_allowed(self, node):
        '''
        Check preconditions before extracting from this node.
        Override this for your subclasses of scanner.
        '''
        return True
