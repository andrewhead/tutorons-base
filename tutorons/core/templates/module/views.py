#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context

from tutorons.core.scanner import NodeScanner
from tutorons.core.views import pagescan, snippetexplain
from detect import {{ title_case_app_name }}Extractor


logging.basicConfig(level=logging.INFO, format="%(message)s")


def detect_code(html_doc):
    '''
    Detects explainable code in an HTML document.
    
    Args:
        html_doc: an `HTMLDocument`, representing a web page whose element
                  tree should be traversed to find explainable code.

    Returns:
        A list of `Region`s, one for each piece of code found
    '''

    # You will need to implement this class in the `detect.py` file.
    # The extractor takes in an HTML element and extracts pieces of code
    # that you want to explain.
    extractor = {{ title_case_app_name }}Extractor()

    # The NodeScanner picks elements from an HTML document where code should be
    # detected, and iterates through them.  It does a pre-order (children-first)
    # traversal: if a piece of code is extracted from a child node, it won't
    # be found a second time in the parent node.
    scanner = NodeScanner(extractor, [
        # Add extra HTML tags to this list (e.g., 'p', 'div') if you want to
        # detect code entities in HTML elements besides those listed here.
        'code',
        'pre',
    ])

    # The scanner will return a list of regions of explainable code.
    # Each region includes the text of the code found as well as a pointer
    # to its location (HTML element and text offset).
    # See `Region` in `tutorons.core.detect`
    explainable_regions = scanner.scan(html_doc)

    return explainable_regions


def explain_code(code_string):
    '''
    Generate explanation of a piece of code.

    Args:
        code_string: A string containing the code to be explained.  Depending
                     on the complexity of code you want to explain, this
                     could be single tokens or entire programs.

    Returns:
        String description explaining the code.
    '''

    # Create an explanation of the code.  This should be unique for
    # each unique region and tell someone something they should know
    # about the code.  This logic can be very complex (e.g., natural language
    # generation or example synthesis) or very simple (e.g., template lookup).
    explanation = "This variable, among other things, fuzzes and bars."

    return explanation


def render_explanation_as_html(code_string, explanation):
    '''
    Render an HTML tooltip that will be used to explain a piece of code.

    Args:
        code_string: the text of code for which an explanation was generated
        explanation: a String explaining what the code does

    Returns:
        A string containing HTML that will be shown in a tooltip
    '''

    # Render an explanation as HTML.  This rendered HTML will be overlaid
    # on the web page as a tooltip once the code is clicked.  You
    # shouldn't have to change anything here, but may have to change
    # the template based on how you want the explanation to be displayed.
    template = get_template('explanation.html')
    context = {
        'code_string': code_string,
        'explanation': explanation,
    }
    explanation_html = template.render(Context(context))
    return explanation_html


@csrf_exempt
@pagescan
def scan(html_doc):
    '''
    Create annotations for all explainable code in a web page.

    Args:
        html_doc: an `HTMLDocument`, representing a web page whose element
                  tree should be traversed to find explainable code.

    Return:
        A list of tuples.  Each tuple is a pair, where the first element is
        a `Region` representing detected code, and the second element is a
        string of the HTML that should be shown in a tooltip when a user
        wants an explanation for that code.
    '''

    # This list will eventually contain pairs (tuples) of two elements:
    # 1. A region where explainable code was detected
    # 2. HTML that should be shown in a tooltip next to that code
    rendered_regions = []

    # Detect all explainable code in the document
    explainable_regions = detect_code(html_doc)

    # Loop through each of the the instances of explainable code.
    for region in explainable_regions:

        # Get the code that was detected for this region
        code_string = region.string

        # Create an explanation for the code
        explanation = explain_code(code_string)

        # Render the explanation as HTML that can be viewed in a tooltip
        explanation_html = render_explanation_as_html(code_string, explanation)

        # Link the explainable code to the HTML of its explanation
        rendered_regions.append((region, explanation_html))

    return rendered_regions


def example(request):
    '''
    Render an example page that shows that this Tutoron works.

    Args:
        request: the Django request that resulted in this view function
                 being called.
    '''
    return render(request, 'example.html', {})
