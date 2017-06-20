#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import os.path
from django.core.management.templates import TemplateCommand
from django.conf import settings


logging.basicConfig(level=logging.INFO, format="%(message)s")


class Command(TemplateCommand):

    """
    def add_arguments(self, parser):
        parser.add_argument('name', help=(
            "Name of Tutoron.  May only contain alphanumeric characters " +
            "and underscores."
        ))
    """

    def handle(self, **options):

        app_name = options.pop('name')
        title_case_app_name = ''.join([c for c in app_name.title() if c != '_'])
        dest = os.path.join('tutorons', 'modules', app_name)

        options['extensions'] = ['html', 'py']
        options['template'] = os.path.join(
            'tutorons', 'core', 'templates', 'module')
        options['title_case_app_name'] = title_case_app_name

        super(Command, self).handle('app', app_name, dest, **options)

        message_lines = [
            "",
            "Created Tutoron `" + app_name + "` at " + dest,
            "To enable the Tutoron, follow these steps:",
            "",
            "1. In tutorons/settings/defaults.py, add " +
                "'tutorons.modules.{app_name}' to the list of `INSTALLED_APPS",
            ""
            "2. In tutorons/urls.py, add these two URL patterns:",
            "    url(r'^{app_name}$', 'tutorons.modules.{app_name}.views.scan', name='{app_name}'),",
            "    url(r'^{app_name}/', include('tutorons.modules.{app_name}.urls', namespace='{app_name}')),",
            "",
            "Then the Tutoron will be ready to detect and explain code.",
            ""
        ]
        indented_message_lines = ["    " + l for l in message_lines]
        message = '\n'.join(indented_message_lines).format(app_name=app_name)
        print(message)
