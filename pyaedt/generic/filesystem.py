import os
import shutil
from distutils.dir_util import copy_tree
import tempfile
import re
from .string_handling import alphanumeric_hash_code


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

def process_list(process, username):
    processID = []
    with os.popen('tasklist /FI "IMAGENAME eq {}" /v'.format(process)) as tasks_list:
        data_table = tasks_list.readlines()
        for row in data_table:
            pattern = r'(?i)^(?:{})\s+?(\d+)\s+.+[\s|\\](?:{})\s+'.format(process, username)
            found_process = re.search(pattern, row)
            if found_process:
                test = row.split()
                processID.append(found_process.group(1))
    return processID


class Scratch():

    """Scratch class

     Provides a mechanism for creating and cleaning up a ''"scratch"'' dorectpry within a specified temp directory

    Parameters
    ----------
    temp_dir : str, optional
        Path of the specified temp directory, if not specified then use tempdir.gettempdir()
    permission : octal, default=0o777
        Permissions for the directory
    volatile : bool
        If ''"True"'' automatically clean up once the Scratch object no longer exists

    """

    @property
    def path(self):
        """Path of this scratch directory"""
        return self._scratch_path

    def __init__(self, temp_dir=None, permission=0o777, volatile=False):
        self._volatile = volatile
        self._scratch_path = None
        if not temp_dir:
            temp_dir = tempfile.gettempdir()
        defined_scratch = os.path.normpath(os.path.join(temp_dir, 'scratch_' + alphanumeric_hash_code()))
        try:
            os.mkdir(defined_scratch)
            os.chmod(defined_scratch, permission)
            self._scratch_path = defined_scratch
        except IOError:
            pass

    def remove(self):
        """ """
        if self._scratch_path:
            try:
                shutil.rmtree(self._scratch_path, ignore_errors=True)
                return True
            except IOError:
                pass
            return False

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
