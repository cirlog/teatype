# Copyright (C) 2024-2026 Burak Günaydin
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

# Third-party imports
from teatype.enum import EscapeColor

if __name__ == '__main__':
    # Example usage and test cases
    from teatype.logging import *
    println()
    # Output: document-o-c-r-detection
    print(f'{EscapeColor.RESET}DocumentOCRDetection ' + f'{EscapeColor.CYAN} -> kebabify                        -> ' + f'{EscapeColor.GREEN}' + kebabify('DocumentOCRDetection'))
    # Output: document-ocr-detection
    print(f'{EscapeColor.RESET}DocumentOCRDetection ' + f'{EscapeColor.CYAN} -> kebabify + preserve_capitals    -> ' + f'{EscapeColor.GREEN}' + kebabify('DocumentOCRDetection', preserve_capitals=True))
    # Output: camel-case-example
    print(f'{EscapeColor.RESET}CamelCaseExample     ' + f'{EscapeColor.CYAN} -> kebabify                        -> ' + f'{EscapeColor.GREEN}' + kebabify('CamelCaseExample'))
    # Output: pascal-case-example
    print(f'{EscapeColor.RESET}PascalCaseExample    ' + f'{EscapeColor.CYAN} -> kebabify                        -> ' + f'{EscapeColor.GREEN}' + kebabify('PascalCaseExample'))
    # Output: test-string-examples
    print(f'{EscapeColor.RESET}TestString           ' + f'{EscapeColor.CYAN} -> kebabify + plural               -> ' + f'{EscapeColor.GREEN}' + kebabify('TestString', plural=True))
    # Output: sample-name
    print(f'{EscapeColor.RESET}SampleName           ' + f'{EscapeColor.CYAN} -> kebabify + remove(ple)          -> ' + f'{EscapeColor.GREEN}' + kebabify('SampleName', remove='ple'))
    # Output: demo-text
    print(f'{EscapeColor.RESET}DemoText             ' + f'{EscapeColor.CYAN} -> kebabify + replace(demo,prod)   -> ' + f'{EscapeColor.GREEN}' + kebabify('DemoText', replace=('demo', 'prod')))
    # Output: kebab-case-example
    print(f'{EscapeColor.RESET}kebab-case-example   ' + f'{EscapeColor.CYAN} -> unkebabify                      -> ' + f'{EscapeColor.GREEN}' + unkebabify('kebab-case-example'))
    # Output: pascalcaseexample
    print(f'{EscapeColor.RESET}pascalcaseexample    ' + f'{EscapeColor.CYAN} -> unkebabify                      -> ' + f'{EscapeColor.GREEN}' + unkebabify('pascalcaseexample'))
    print(EscapeColor.RESET)