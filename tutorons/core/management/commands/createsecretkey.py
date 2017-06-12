#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.conf import settings


class Command(BaseCommand):
    """
    This command assumes you have write access to create
    the directory in which the key is created, and then
    to create the key as a file in that directory.
    """

    def handle(self, *args, **kwargs):

        # Create a directory for holding the key
        key_filename = settings.SECRET_KEY_FILE
        key_dir = os.path.dirname(key_filename)

        try:
            if not os.path.exists(key_dir):
                os.makedirs(key_dir)
        except Exception as e:
            raise SystemExit(
                "Exception: " + repr(e) + "\n" + 
                "Do you have write access to " + key_dir + "?\n" +
                "If not, change the SECRET_KEY_FILE setting in " +
                "the tutorons.settings.default file"
            )

        # Generate key and write to file
        with open(key_filename, 'w') as key_file:

            # Generate a secret key using the technique in the
            # Django `startproject` command
            # (https://github.com/django/django/blob/1.8/django/core/management/commands/startproject.py)
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            secret_key = get_random_string(50, chars)
            key_file.write(secret_key)
