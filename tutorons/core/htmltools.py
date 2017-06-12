#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format="%(message)s")


class HtmlDocument(BeautifulSoup):
    ''' Subclass of BeautifulSoup that cleans HTML documents for our processing purposes. '''

    def __init__(self, text, *args, **kwargs):
        # Parse with html5lib to "parse the page the same way a web browser does".
        # Source: http://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # Lxml parser takes liberties in removing newlines, which makes it hard to get
        # absolute character positions of explainable regions in the original doc
        super(self.__class__, self).__init__(text, 'html5lib', *args, **kwargs)


def get_css_selector(tag):
    ''' Create a CSS selector that can choose this tag from the document. '''

    elements = []

    element = tag
    while element.name != '[document]':

        parent = element.parent
        type_siblings = parent.find_all(element.name, recursive=False)
        index = -1
        for i, s in enumerate(type_siblings):
            if id(s) == id(element):
                index = i + 1  # in CSS, nth-of-type index starts at 1
                break

        elements.insert(0, {'name': element.name, 'index': index})
        element = parent

    element_selectors = []
    for i, el in enumerate(elements):
        tag_name = el['name'].upper()
        if i == 0 and el['name'] == 'html':
            element_selectors.append(tag_name)
        else:
            element_selectors.append(
                '%s:nth-of-type(%d)' % (tag_name, el['index'])
            )
    return ' > '.join(element_selectors)
