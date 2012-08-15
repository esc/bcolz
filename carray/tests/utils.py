########################################################################
#
#       License: BSD
#       Created: August 15, 2012
#       Author:  Francesc Alted - faltet@pytables.org
#
########################################################################


import unittest
import tempfile
import os, os.path
import glob
import shutil


# Useful superclass for disk-based tests
class MayBeDiskTest(unittest.TestCase):

    disk = False

    def setUp(self):
        if self.disk:
            prefix = 'carray-' + self.__class__.__name__
            self.rootdir = tempfile.mkdtemp(prefix=prefix)
            os.rmdir(self.rootdir)  # tests needs this cleared
        else:
            self.rootdir = None

    def tearDown(self):
        if self.disk:
            # Remove every directory starting with rootdir
            for dir_ in glob.glob(self.rootdir+'*'):
                shutil.rmtree(dir_)


