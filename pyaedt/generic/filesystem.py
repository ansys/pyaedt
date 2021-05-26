import os
import shutil
from distutils.dir_util import copy_tree
import random
import string

def my_location():
    """ """
    return os.path.normpath(os.path.dirname(__file__))

def files_in_directory(path='.',ext=''):
    """

    Parameters
    ----------
    path :
         (Default value = '.')
    ext :
         (Default value = '')

    Returns
    -------

    """
    result = []
    if os.path.exists(path):
        for dir in os.listdir(path):
            bd = os.path.join(path, dir)
            if os.path.isfile(bd) and dir.endswith("." + ext):
                result.append(bd)
    return result


class Scratch():
    """ """

    @property
    def path(self):
        """ """
        return self._scratch_path

    @property
    def is_empty(self):
        """ """
        return self._cleaned

    def __init__(self, local_path, permission=0o777, volatile=False):
        self._volatile = volatile
        self._cleaned = True
        char_set = string.ascii_uppercase + string.digits
        self._scratch_path = os.path.normpath(os.path.join(local_path, 'scratch' + ''.join(random.sample(char_set, 6))))
        if os.path.exists(self._scratch_path):
            try:
                self.remove()
            except:
                self._cleaned = False
        if self._cleaned:
            try:
                os.mkdir(self.path)
                os.chmod(self.path, permission)
            except:
                pass

    def remove(self):
        """ """
        try:
            # TODO check why on Anaconda 3.7 get errors with os.path.exists
            shutil.rmtree(self._scratch_path, ignore_errors=True)
        except:
            pass


    def copyfile(self, src_file):
        """

        Parameters
        ----------
        src_file :
            

        Returns
        -------

        """
        dst_file = os.path.join(self.path, os.path.basename(src_file))
        shutil.copyfile(src_file, dst_file)
        return dst_file

    def copyfolder(self, src_folder, destfolder):
        """

        Parameters
        ----------
        src_folder :
            
        destfolder :
            

        Returns
        -------

        """
        copy_tree(src_folder, destfolder)
        return True

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type or self._volatile:
            self.remove()
