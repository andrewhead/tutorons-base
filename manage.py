#! /usr/bin/env python

import sys

from SocketServer import BaseServer
from wsgiref import handlers


def patch_broken_pipe_error():
    '''
    This function helps us avoid a bunch of nasty error messages that
    we don't want to see related to broekn pipes.  Written with code reused from:
    http://stackoverflow.com/questions/7912672/django-broken-pipe-in-debug-mode.
    '''

    handle_error_default = BaseServer.handle_error
    log_exception_default = handlers.BaseHandler.log_exception

    def is_error_from_broken_pipe():
        type_, exception, traceback = sys.exc_info()
        return exception is not None and "Broken pipe" in repr(exception)

    def handle_error_patched(self, request, client_address):
        if not is_error_from_broken_pipe():
            handle_error_default(self, request, client_address)

    def log_exception_patched(self, exc_info):
        if not is_error_from_broken_pipe():
            log_exception_default(self, exc_info)

    BaseServer.handle_error = handle_error_patched
    handlers.BaseHandler.log_exception = log_exception_patched


if __name__ == "__main__":

    patch_broken_pipe_error()

    from django.core.management import execute_from_command_line
    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        # We make sure to catch all exceptions and raised events while running
        # the main command.  This includes keyboard interrupts.
        print "Exception running command:", e
        pass
