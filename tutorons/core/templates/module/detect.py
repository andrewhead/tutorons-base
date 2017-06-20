#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging

from tutorons.core.extractor import Region

logging.basicConfig(level=logging.INFO, format="%(message)s")


class {{ title_case_app_name }}Extractor(object):
    ''' Finds regions of explainable code in HTML elements. '''

    def extract(self, node):
        '''
        Detect explainable regions of code in an HTML element.

        Args:
            node: an HTML element (it's a node created by BeautifulSoup
                  parsing HTML)

        Returns:
            A list of `Region`s, each containing a piece of detected code and
            a link to its unique location in the page.
        '''
        
        # Get the text contained in the HTML element
        text = node.text

        # Detect code in the element.  However you detect it, you need to make
        # sure to save the character offset of the piece of code within the 
        # text of this HTML element. Most code parsers will give you a line
        # and offset of each symbol.  If you use such a parser, you can find
        # the character offset of the code by sum up the number of characters 
        # in each line before the one where code was detected, and
        # then add the within-line offset.  In this example, we just use the
        # standard Python string API to look for everywhere the symbol `foo` 
        # appears in the element.
        pattern = "foo"
        last_match_end = 0

        # We'll store all of the detected code in this list.
        regions = []

        while True:

            # Although the pattern detection shown here is specific to this
            # example, this code computes offsets and makes regions in a way 
            # you'll have to do in your own code.

            # You need to detect the index of the character where the code
            # was detected.
            match_start = text.find(pattern, last_match_end)
            if match_start == -1:
                break

            # You also need to detect the index where the code stops.  Make
            # sure this points to the last character in the code and not
            # to the first character after the code.
            match_end = match_start + len(pattern) - 1

            # Every region needs to include a reference to the node it was 
            # extracted from, the index of the first character where the code
            # was detected within that element, the index of the last character
            # of the detected code, and the code itself.
            matching_region = Region(
                node=node,
                start_offset=match_start,
                end_offset=match_end,
                string=pattern,
            )

            regions.append(matching_region)

            # Save the end index of this match so it can be used to advance
            # the text search in the next loop iteration.
            last_match_end = match_end

        return regions
