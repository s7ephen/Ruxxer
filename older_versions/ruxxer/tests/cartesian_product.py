#!/usr/bin/env python2.4

#M = [1,2,3]
#N = ['A','B','C','D']
#O = ['a','b']

B = ['X', 'Y', 'Z']
C = [1,2,3]
D = ['L', 'M', 'N']

def getvalue2(val):
    """ 
        With this method of element selection,
        we are able to jump forward and select
        the element from the product set that
        we want...this is the benefit of this method.
    """
    origval = val

    w = (val / (len(B) * len(C))) % len(D)

    x = val / (len(C)) % len(D)

    y = val % len(D)
    print "%d: [%d,%d,%d]" % (origval, w, x, y)

if __name__ == "__main__":
    for i in range(0, (len(B)*len(C)*len(D))):
        getvalue2(i)

    banner = """
            The numbers printed within the cartesian product
            are the index of the element to be selected from
            the child arrays, not the value selected.
            For the set: 
            [['X', 'Y', 'Z'], [1, 2, 3], ['L', 'M', 'N']] 
            [0, 0, 0] really means a set of:
            ['X', 1, 'L']
            In reality the cartesian product set is what 
            we are listing per element.
            
    """
    print banner
    print "\n\t%d elements in our cartesian product set." % (len(B)*len(C)*len(D))

