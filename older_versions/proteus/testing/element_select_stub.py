#!/usr/bin/env python2.4

#M = [1,2,3]
#N = ['A','B','C','D']
#O = ['a','b']

L = ['Q', 'R', 'S']
M = [1,2,3]
N = ['A', 'B', 'C']
O = ['a']

def getvalue2(val):
    origval = val
    w = (val / (len(M) * len(N) * len(O))) % len(L)
    x = val / (len(N) * len(O)) % len(M)
    y = val / (len(O)) % len(N)
    z = val % len(O)
    print "%d: [%d,%d,%d,%d]" % (origval, w, x, y, z)

for i in range(0, (len(L)*len(M)*len(N)*len(O))):
    getvalue2(i)
print "\n\t%d possible permutations." % (len(L)*len(M)*len(N)*len(O))

