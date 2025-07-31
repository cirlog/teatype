# Copyright (C) 2024-2025 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# Package imports
import pytest

def skip_on_fail_hook(function:callable, expected_failure_messages:any):
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(item):
        output = yield
        if output.excinfo:
            for potential_error_message in expected_failure_messages.keys():
                if output._excinfo[1].stacktrace and potential_error_message in output._excinfo[1].stacktrace:
                    pytest.skip(reason=expected_failure_messages[potential_error_message])