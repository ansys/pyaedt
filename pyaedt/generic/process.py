import time
from threading import Thread

import queue
from queue import Queue
import os.path
if os.name == 'posix':
	import subprocessdotnet as subprocess
else:
	import subprocess
import clr
import os
if os.name == 'posix':
	import subprocessdotnet as subprocess
else:
	import subprocess
from .general_methods import env_path, env_value
class AedtSolve(object):
    '''
    class dedicated for calling Aedt solvers. Only solving on local machines is supported for the moment.
    Examples
    --------
    >>> from pyaedt import AedtSolve
    >>> solver = process.AedtSolve()
    >>> solver.NonGraphical = True
    >>> solver.ProjectPath = edb_file
    >>> solver.solve()
    '''
    def __init__(self,aedt_version="2021.1", aedt_installer_path=None):
        self._project_path = ""
        self._command = []
        self._nbcores = 4
        self._ng = True
        self._local = True
        self._logfile = ""
        if aedt_installer_path:
            self.installer_path = aedt_installer_path
        else:
            try:
                self.installer_path = env_path(aedt_version)
            except:
                raise Exception("Either a valid aedt version or full path has to be provided")

    @property
    def projectpath(self):
        return self._project_path

    @projectpath.setter
    def projectpath(self, value):
        self._project_path = value
        self._logfile = os.path.splitext(self._project_path)[0] + ".log"

    @property
    def exepath(self):
        return self._exe

    @exepath.setter
    def exepath(self,value):
        self._exe = value

    @property
    def command(self):
        return  self._command

    @command.setter
    def command(self,value):
        self._command = value

    @property
    def nbcores(self):
        return self._nbcores

    @nbcores.setter
    def nbcores(self,value):
        self._nbcores = value

    @property
    def nongraphical(self):
        return self._ng

    @nongraphical.setter
    def nongraphical(self,value):
        self._ng = value

    @property
    def local(self):
        return self._local

    @local.setter
    def local(self,value):
        self._local = value

    @property
    def logfile(self):
        return self._logfile

    @logfile.setter
    def logfile(self,value):
        self._logfile = value

    def solve(self):
        if os.name == "posix":
                self.command.append(os.path.join(self.installer_path,'ansysedt'))
        else:
               self.command.append(os.path.join(self.installer_path,'ansysedt.exe'))
        if self.nongraphical:
            self.command.append('-Batchsolve')
            self.command.append('-ng')
            self.command.append('-Monitor')
            self.command.append('-MachineList')
            # TODO Add batch option support
        if self._local:
            pass

        #self.Command.append('-Auto')
        self.command.append('-machinelist numcores={}'.format(self.nbcores))
        self.command.append('-LogFile')
        self.command.append(self.logfile)
        self.command.append(self.projectpath)
        print(self._command)
        p = subprocess.Popen(self.command)
        p.wait()

class SiwaveSolve(object):
    def __init__(self, aedt_version="2021.1", aedt_installer_path=None):
        self._project_path = ""
        self._exec_path = ""
        self._nbcores = 4
        self._ng = True
        if aedt_installer_path:
            self.installer_path = aedt_installer_path
        else:
            try:
                self.installer_path = env_path(aedt_version)
            except:
                raise Exception("Either a valid aedt version or full path has to be provided")


    @property
    def siwave_exe(self):
        return self._exe

    @siwave_exe.setter
    def siwave_exe(self,value):
        self._exe = value

    @property
    def projectpath(self):
        return self._project_path
        self._exec_path = os.path.splitext(self._project_path[0]) + ".exec"

    @projectpath.setter
    def projectpath(self,value):
        self._project_path = value

    @property
    def execfile(self):
        return self._exec_path

    @execfile.setter
    def execfile(self,value):
        self._exec_path = value

    @property
    def nbcores(self):
        return self._nbcores

    @nbcores.setter
    def nbcores(self,value):
        self._nbcores = value

    @property
    def nongraphical(self):
        return self._ng

    @nongraphical.setter
    def nongraphical(self,value):
        self._ng = value

    def solve(self):
        # supporting non graphical solve only
        if self.nongraphical:
            if os.name == "posix":
                exe_path = os.path.join(self.installer_path, 'siwave_ng')
            else:
                 exe_path = os.path.join(self.installer_path, 'siwave_ng.exe')     
            exec_file = os.path.splitext(self._project_path)[0] + '.exec'
            if os.path.exists(exec_file):
                with open(exec_file,"r+") as f:
                    content = f.readlines()
                    if not 'SetNumCpus' in content:
                        f.writelines(str.format('SetNumCpus {}', str(self.nbcores)) + '\n')
                        f.writelines("SaveSiw")
                    else:
                        fstarts = [i for i in range(len(content)) if content[i].startswith('SetNumCpus')]
                        content[fstarts] = str.format('SetNumCpus {}', str(self.nbcores))
                        f.closed()
                        os.remove(exec_file)
                        f = open(exec_file,"w")
                        f.writelines(content)
            command = [exe_path]
            command.append(self._project_path)
            command.append(exec_file)
            command.append('-formatOutput -useSubdir')
            p = subprocess.Popen(command)
            p.wait()
