#Eventually these will be in their own file.
from lib.rux_core import *

class Ruxxer(Primitive):
    """
        
    """
    def __init__(self):
        Primitive.__init__(self)

    def _add_permutation(self, to_add):
        """

        """
        self._data.append(to_add)
        self.permutations = len(self._data)

    def get_rightpeer_count(self):
        """

        """
        parent = self.get_parent()
        right_count = parent._get_childs_rightpeer_count(self)
        return (right_count)

    def get_rightpeer_perms(self):
        """
            
        """
        parent = self.get_parent()
        right_perms = parent._get_childs_rightpeer_perms(self)
        if parent._get_childs_rightpeer_count(self) == 0:
            return 0

        return (right_perms)

    def get_iter_count(self):
        """

        """
        return (self.get_parent().iter_count)

    def is_rightmost(self):
        if self.get_rightpeer_count() == 0:
            return True
        else: return False

    def calc_permutation_selection(self):
        """
        """
        parent = self.get_parent()
        iter_count = parent.iter_count
        element = None

        #If we are the rightmost node:
        if self.is_rightmost():
            element = iter_count % self.permutations

        #If we are anyone other than the two rightmost
        if not self.is_rightmost():
            element = iter_count / self.get_rightpeer_perms() % self.permutations
        return element

    def step(self):
        """
            For every step we calculate which element we should select from
            our permutations.
        """
        self.step_index = self.calc_permutation_selection() 
#        print "%s (%d,%d)" % (repr(self), self.get_parent().iter_count, self.step_index)
    def set_iter_count(self, iter):
        self.iter_count = self.step_index = int(iter)
