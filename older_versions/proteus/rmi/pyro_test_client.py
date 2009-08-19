#!/usr/bin/env python
import Pyro.core, pprint, threading

a = Pyro.core.getProxyForURI("PYROLOC://10.0.0.102:7766/overlord")

a.doit() 
