#!/usr/bin/env python2.4
while 1:
    code_str = raw_input("> ");
    code_obj = compile(code_str, 'single')
    exec(code_obj)
