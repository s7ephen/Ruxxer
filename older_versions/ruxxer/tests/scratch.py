#!/usr/bin/env python2.4
from lib.rux_types import *
#lng = Long()
#lng.setval(0x777)
strn1 = String()
strn = String()
strn1.setval("blingin")
strn.setval("testing")
strc = Structure()
strc.push(strn1)
strc.push(strn)
print repr(strc)

