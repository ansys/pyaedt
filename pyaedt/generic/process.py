import time
from threading import Thread

import queue
from queue import Queue
import os.path
import subprocess
import clr
import os
import subprocess
from .general_methods import env_path, env_value
class AedtSolve(object):
    '''
    class dedicated for calling Aedt solvers. Only solving on local machines is supported for the moment.
    Examples
    >>>solver = process.AedtSolve()
    >>>solver.NonGraphical = True
    >>>solver.ProjectPath = edb_file
    >>>solver.solve()
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
                raise Exception("Either a valide aedt version or full path has to be provided")

    @property
    def ProjectPath(self):
        return self._project_path

    @ProjectPath.setter
    def ProjectPath(self, value):
        self._project_path = value
        self._logfile = os.path.splitext(self._project_path)[0] + ".log"

    @property
    def ExePath(self):
        return self._exe

    @ExePath.setter
    def ExePath(self,value):
        self._exe = value

    @property
    def Command(self):
        return  self._command

    @Command.setter
    def Command(self,value):
        self._command = value

    @property
    def NbCores(self):
        return self._nbcores

    @NbCores.setter
    def NbCores(self,value):
        self._nbcores = value

    @property
    def NonGraphical(self):
        return self._ng

    @NonGraphical.setter
    def NonGraphical(self,value):
        self._ng = value

    @property
    def Local(self):
        return self._local

    @Local.setter
    def Local(self,value):
        self._local = value

    @property
    def LogFile(self):
        return self._logfile

    @LogFile.setter
    def LogFile(self,value):
        self._logfile = value

    def solve(self):
        self.Command.append(os.path.join(self.installer_path,'ansysedt.exe'))
        if self.NonGraphical:
            self.Command.append('-Batchsolve')
            self.Command.append('-ng')
            self.Command.append('-Monitor')
            self.Command.append('-MachineList')
            # TODO Add batch option support
        if self.Local:
            pass

        #self.Command.append('-Auto')
        self.Command.append('-machinelist numcores={}'.format(self.NbCores))
        self.Command.append('-LogFile')
        self.Command.append(self.LogFile)
        self.Command.append(self.ProjectPath)
        print(self._command)
        p = subprocess.Popen(self.Command)
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
                raise Exception("Either a valide aedt version or full path has to be provided")


    @property
    def SiwaveExe(self):
        return self._exe

    @SiwaveExe.setter
    def SiwaveExe(self,value):
        self._exe = value

    @property
    def ProjectPath(self):
        return self._project_path
        self._exec_path = os.path.splitext(self._project_path[0]) + ".exec"

    @ProjectPath.setter
    def ProjectPath(self,value):
        self._project_path = value

    @property
    def ExecFile(self):
        return self._exec_path

    @ExecFile.setter
    def ExecFile(self,value):
        self._exec_path = value

    @property
    def NbCores(self):
        return self._nbcores

    @NbCores.setter
    def NbCores(self,value):
        self._nbcores = value

    @property
    def NonGraphical(self):
        return self._ng

    @NonGraphical.setter
    def NonGraphical(self,value):
        self._ng = value

    def solve(self):
        # supporting non graphical solve only
        if self.NonGraphical:
            exe_path = os.path.join(self.installer_path, 'siwave_ng.exe')
            exec_file = os.path.splitext(self._project_path)[0] + '.exec'
            if os.path.exists(exec_file):
                with open(exec_file,"r+") as f:
                    content = f.readlines()
                    if not 'SetNumCpus' in content:
                        f.writelines(str.format('SetNumCpus {}', str(self.NbCores)) + '\n')
                        f.writelines("SaveSiw")
                    else:
                        fstarts = [i for i in range(len(content)) if content[i].startswith('SetNumCpus')]
                        content[fstarts] = str.format('SetNumCpus {}', str(self.NbCores))
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



