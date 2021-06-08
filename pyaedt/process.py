import time
from threading import Thread

import queue
from queue import Queue
import os.path
import subprocess
import clr

clr.AddReference('System')
import System
from System.Threading import ThreadStart, Thread

class WorkerThread():

    def __init__(self):
        self.ProjectList = None
        self.NbThreads = 1
        self.PathToAedt = None
        self.PathSiwave_ng = None
        self.BatchExtractScript = None
        self.SetupParameters = None
        self.DCWorkDir = None
        self.SolveNg = True
        self.RunValcheck = True



    def AddSParamFile(self, File):
        FileTable = self.DataSet.Tables['SParamFiles']
        if not FileTable.Rows.Find(File):
            FileTable.Rows.Add(File, True)
        # FileTable.ClearSelection()

    def worker(self):
        while True:
            item = self.q.get()
            if item is None:
                self.q.task_done()
                break
            else:
                self.AddLog('Info: Starting simulation for project {0}'.format(item))
                self.CommandLine(self.PathToAedt, item, False, True)
                self.q.task_done()
                self.LogLineCounter = 0



    def StartThreadsAndProcessQueue(self):
        # start worker thread
        self.q = Queue()
        for i in range(self.NbThreads):
            self.t = threading.Thread(target=self.worker)
            self.t.start()

        # Add item to queue
        # self.NbSteps = round(100/len(self.ProjectList))
        for item in self.ProjectList:
            self.q.put(item)
        self.q.join()

        # Stop all workers
        for i in range(self.NbThreads):
            self.q.put(None)

    def Start_DC_ThreadsAndProcessQueue(self):
        # start worker thread
        self.q = Queue()
        for i in range(self.NbThreads):
            self.t = threading.Thread(target=self.DC_worker)
            self.t.start()

        # Add item to queue
        # self.NbSteps = round(100/len(self.ProjectList))
        for item in self.ProjectList:
            self.q.put(item)
        self.q.join()

        # Stop all workers
        for i in range(self.NbThreads):
            self.q.put(None)

    def CommandLine(self, DesktopLocationInfo, InputProjectFile, BatchExtract=False, NoGraphics=False):
        # Add Check for lock file
        ProjectTable = self.DataSet.Tables['HFSSProjectQueue']

        if os.path.exists(InputProjectFile):
            if os.path.exists(DesktopLocationInfo):

                # wmic computersystem get numberoflogicalprocessors
                installDir = os.path.dirname(DesktopLocationInfo)
                pjtDir = os.path.dirname(InputProjectFile)
                pjtName = os.path.splitext(InputProjectFile)[0]
                LogFile = pjtName + '_HFSSsimulation.log'
                process = [DesktopLocationInfo]

                if NoGraphics or BatchExtract:
                    #	cmd = '"{0}" -ng -BatchSolve -monitor -Distributed -MachineList list=localhost:-1:{1} -auto -LogFile "{2}" "{3}"'.format(DesktopLocationInfo,SetupParameters['NumCpusToUse'],LogFile,InputProjectFile)
                    # process.append(cmd)
                    process.append('-ng')

                process.append('-Batchsolve')
                process.append('-Monitor')
                process.append('-Local')
                process.append('-MachineList')
                process.append('list=localhost:-1:{0}:90%'.format(self.SetupParameters['NumCpusToUse']))
                process.append('-Auto')
                process.append('-batchoptions')
                process.append("'HFSS 3D Layout Design/HPCLicenseType'='{0}' 'tempdirectory'='{1}'".format(
                    self.SetupParameters['HPCLicense'], self.SetupParameters['TempDir']))
                process.append('-LogFile')
                process.append(LogFile)

                # if not self.BatchExtractScript == None:
                #	BatchExtract = True

                # if BatchExtract is True:
                #	process.append('-BatchExtract')
                #	process.append(self.BatchExtractScript)

                process.append(InputProjectFile)

                p = subprocess.Popen(process)
                p.wait()

                # self.LogLineCounter = 0
                try:
                    if p.returncode == 0:
                        self.AddLog('Info: Project {0} succeesfully solved'.format(
                            os.path.splitext(InputProjectFile)[0] + '.aedt'))
                        try:
                            RowFound = ProjectTable.Rows.Find(os.path.splitext(InputProjectFile)[0] + '.aedt')
                            RowFound['Status'] = 'Solved'
                        # self.HFSSPostProcess(os.path.splitext(InputProjectFile)[0]+'.aedt')
                        except:
                            self.AddLog('Error: failed to find Project {0} in DataTable'.format(
                                os.path.splitext(InputProjectFile)[0] + '.aedt'))
                        try:
                            self.ExportSparam(InputProjectFile)
                        except:
                            self.AddLog('Error: failed to Extract S parameter for project {0}'.format(
                                os.path.splitext(InputProjectFile)[0] + '.aedt'))
                    else:
                        # self.HFSSProjectsStatusDict[InputProjectFile] = 'Simulation Failed'
                        self.AddLog('Error: Project {0} simulation failed with Exit code {1}'.format(
                            os.path.splitext(InputProjectFile)[0] + '.aedt', p.returncode))
                # self.UpdateProgessBar()
                # read(ThreadStart(update))
                # tr.Start()
                except:
                    self.AddLog('Error: Failed to collect Exit code for Project {0}, project status unknown'.format(
                        os.path.splitext(InputProjectFile) + '.aedt'))
                # self.UpdateProgessBar(SetProgress)

    def StartDCSolver(self):
        try:
            ProjectTable = self.DataSet.Tables['DCProjectQueue']
            RunValcheck = True
            SIwaveDCIR.RunDCIR(self.DCWorkDir, '', True, self._textBoxLog, RunValcheck, self.DataSet,
                               self.AddSolderMask, self.DCAedb)
            RowFound = ProjectTable.Rows.Find(self.DCAedb)
            RowFound['Status'] = 'Solved'
        # self.HFSSPostProcess(os.path.splitext(InputProjectFile)[0]+'.aedt')
        except:
            self.AddLog('Error: failed to find Project {0} in DataTable'.format(
                os.path.splitext(InputProjectFile)[0] + '.aedt'))

    def HFSSPostProcess(self, InputProjectFile):
        self.AddLog('Info: Doing postprocessing for project {0}'.format(InputProjectFile))
        try:
            if not self.IsAedtOpen:
                self.Desktop = AedtProcess.GetDesktop()
                if not self.Desktop == None:
                    self.IsAedtOpen = True
            # self.Desktop = AedtProcess.GetDesktop()
            self.Desktop.OpenProject(InputProjectFile)
            # self.UpdateReports(InputProjectFile)
            # self.AddLog('Info: plots updated on project {0}'.format(InputProjectFile))

            self.ExportMatrixFromNDE(InputProjectFile)
            self.AddLog('Info: Toucshtone file exported at {0} for project {1}'.format(
                os.path.join(os.path.dirname(InputProjectFile)), 'TouchstoneFiles', InputProjectFile))
            self.oProject = self.Desktop.GetActiveProject()
            self.oProject.Save()
            self.oProject.Close()
        except:
            self.AddLog('Error: Project {0} failed during postprocessing'.format(InputProjectFile))
            try:
                self.oProject.Save()
                self.oProject.Close()
            except:
                pass

    def UpdateReports(self, InputProjectFile):
        try:
            self.Desktop.RestoreWindow()
            self.oProject = self.Desktop.GetActiveProject()
            self.oDesign = self.oProject.GetDesigns()[0]
            self.oModule = self.oDesign.GetModule("ReportSetup")
            self.oModule.UpdateAllReports()
        except:
            self.AddLog('Error: Project {0} failed to update plots'.format(InputProjectFile))

    def ExportMatrixFromNDE(self, InputProjectFile):
        try:
            self.AddLog('Info: Exporting Touchstone model for project {0} at {0}, using State Space fitting'.format(
                InputProjectFile, os.path.join(os.path.dirname(InputProjectFile), 'TouchstoneFiles')))
            oProject = self.Desktop.GetActiveProject()
            projectPath = oProject.GetPath()
            projectName = oProject.GetName()
            designlist = oProject.GetTopDesignList()
            design = designlist[0].split(";")[1]
            oDesign = oProject.SetActiveDesign(design)
            oModuleSetup = oDesign.GetModule("SolveSetups")
            setup = oModuleSetup.GetSetups()[0]
            oModuleBoundary = oDesign.GetModule("Excitations")
            excitations = oModuleBoundary.GetAllPortsList()
            sweep = oModuleSetup.GetSweeps(setup)
            oDefinitionManager = oProject.GetDefinitionManager()
            oNdExplorerManager = oDefinitionManager.GetManager("NdExplorer")
            blockname = design
            if not os.path.isdir(os.path.join(projectPath, 'TouchstoneFiles')):
                os.mkdir(os.path.join(projectPath, 'TouchstoneFiles'))

            Matrix_FileName = os.path.join(projectPath, 'TouchstoneFiles',
                                           '{0}.s{1}p'.format(projectName, str(len(excitations))))

            if not os.path.isdir(os.path.join(projectPath, 'Profiles')):
                os.mkdir(os.path.join(projectPath, 'Profiles'))

            # oDesign.ExportNetworkData('""',[setup+":"+sweep[0]], 3, Matrix_FileName, ["ALL"], False, 50, "S", -1, 0, 15, False, False)
            oNdExplorerManager.ExportFullWaveSpice(design, False, "{0} : Sweep1".format(setup), "",
                                                   ["NAME:Frequencies"],
                                                   [
                                                       "NAME:SpiceData",
                                                       "SpiceType:="	, "TouchStone1.0",
                                                       "EnforcePassivity:="	, True,
                                                       "EnforceCausality:="	, False,
                                                       "UseCommonGround:="	, True,
                                                       "Renormalize:="		, False,
                                                       "RenormImpedance:="	, 50,
                                                       "FittingError:="	, 0.01,
                                                       "MaxPoles:="		, 10000,
                                                       "PassivityType:="	, "IteratedFittingOfPV",
                                                       "ColumnFittingType:="	, "Matrix",
                                                       "SSFittingType:="	, "TWA",
                                                       "RelativeErrorToleranc:=", False,
                                                       "EnsureAccurateZfit:="	, True,
                                                       "TouchstoneFormat:="	, "MA",
                                                       "TouchstoneUnits:="	, "Hz",
                                                       "TouchStonePrecision:="	, 8,
                                                       "SubcircuitName:="	, "",
                                                       "SYZDataInAutoMode:="	, False,
                                                       "ExportDirectory:="	, "D:/temp",
                                                       "ExportSpiceFileName:="	, Matrix_FileName,
                                                       "FullwaveSpiceFileName:=", Matrix_FileName,
                                                       "UseMultipleCores:="	, True,
                                                       "NumberOfCores:="	, 4
                                                   ])
            # if not self.DataSet.Tables['SParamFile'].Rows.Find(Matrix_FileName):
            self.AddSParamFile(Matrix_FileName)
        except:
            self.AddLog('Error: failed to export Touchstone file for project {0}'.format(InputProjectFile))
        Profile_File = os.path.join(projectPath, 'Profiles', '{0}.prof'.format(projectName))
        Convergence_File = os.path.join(projectPath, 'Profiles', '{0}_meshing.conv'.format(projectName))
        oDesign.ExportProfile(setup ,"", Profile_File)
        oDesign.ExportConvergence(setup ,"", Convergence_File)


    def LoadSUtility(self ,Projects):
        try:
            SUtility_exe = os.path.normpath(self.PathToSUtility)
            proc = [SUtility_exe]
            for proj in Projects:
                proc.append(proj)
            p = subprocess.Popen(proc)

        except:
            self.AddLog('Error: Failed to launch SUtility tool')



    def startProgress(self, s, e):
        def update():
            for i in range(100):
                print i
                def step():
                    self.ProgessBar.Value = i + 1
                self.Invoke(CallTarget0(step))
                Thread.Sleep(30)

    def ExportSparam(self ,InputProjectFile):
        ProjectFN = os.path.splitext(InputProjectFile)[0 ] +'.aedt'
        proc = [self.PathToAedt]
        proc.append('-iconic')
        proc.append('-runscriptandexit')
        # scriptFN = os.path.join(os.path.dirname(ProjectFN),'BatchFiles','export_Sparam.py')
        PrjectDir = os.path.abspath(os.path.join(ProjectFN ,"../.."))
        scriptFN = os.path.join(PrjectDir, 'BatchFiles', 'export_Sparam.py')
        proc.append(scriptFN)
        proc.append('-scriptargs')
        proc.append(ProjectFN)
        aedtproc = subprocess.Popen(proc)
        aedtproc.wait()
        TouchstoneFileList = []
        # TouchstoneFN = os.path.basename(os.path.splitext(ProjectFN)[0]+)
        TouchstoneFileFolder = os.path.join(os.path.dirname(ProjectFN), 'TouchstoneFiles')
        for f in os.listdir(TouchstoneFileFolder):
            ProjectName = os.path.splitext(os.path.basename(ProjectFN))[0]
            if re.match(ProjectName, f):
                if not os.path.splitext(f)[1] == '.txt':
                    TouchstoneFileList.append(os.path.join(TouchstoneFileFolder, f))

        if not TouchstoneFileList == []:
            SParamTable = self.DataSet.Tables['SParamFiles']
            for file in TouchstoneFileList:
                try:
                    if not SParamTable.Rows.Find(file):
                        SParamTable.Rows.Add(os.path.abspath(file), os.path.basename(file), True)
                    else:
                        self.AddLog('Info: Touchstone file {0} already defined'.format(file))
                except:
                    self.AddLog('Error: Touchstone file {0} not found'.format(file))























