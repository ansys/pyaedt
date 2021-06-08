##############################################################
#                           Imports
##############################################################
import os
import re
import socket
import subprocess
import time
import sys
import clr

# Importing HPC Scheduler interrface:
clr.AddReference("Microsoft.Hpc.Scheduler")
clr.AddReference("Microsoft.Hpc.Scheduler.Properties")
from Microsoft.Hpc.Scheduler import Scheduler
from Microsoft.Hpc.Scheduler.Properties import JobUnitType

# Importing proprietary ISchedulerPluginExtension:
from Ansys.Ansoft.SchedulerPluginDotNet import ISchedulerPluginExtension

##############################################################
#                            Constants
##############################################################
# String constants for environment variables:
kClusterNameEnvName = "CCP_CLUSTER_NAME"
kJobIdEnvName = "CCP_JOBID";
kTaskIdEnvName = "CCP_TASKID"

# String constants for debug logging:
kDebugMode = "ANSOFT_DEBUG_MODE"
kDebugLog = "ANSOFT_DEBUG_LOG"
kDebugLogSeparate = "ANSOFT_DEBUG_LOG_SEPARATE"

# Other string constants:
kMachineListOption = "-machinelist"


##############################################################
#       Helper functions; similar for different plugins
##############################################################
# --------------------------------------------------------------------------------------
# Logs debug info
def PyLogDebug(theStr):
    theStr = "PyScript:Info: " + theStr + "\r\n"
    LogDebug(theStr)


# --------------------------------------------------------------------------------------
# Logs error info
def PyLogError(theStr):
    theStr = "PyScript:Error: " + theStr + "\r\n"
    LogError(theStr)


# --------------------------------------------------------------------------------------
# Strips parameter string from 'garbage' symbols;
# If string is empty sets it to a single space string
def CleanArgument(theStr):
    # Strip off whitespace at the end/beggining of argument
    theStr = theStr.strip("\n\r\t\v ")

    # This is to fix IronPython bug when the empty string is not passed as a parameter
    if theStr == "":
        theStr = " "
    return theStr;


# --------------------------------------------------------------------------------------
# Called if the hostname is local; launches process on the local host.
def OpenSubprocess(argList):
    ret = 0
    try:
        p = subprocess.Popen(argList)
    except:
        ret = 1
        PyLogError("Exception occured on Popen; arg=" + argList[0])
        PyLogError(sys.exc_info()[1])
    return ret


# --------------------------------------------------------------------------------------
# Defines if the progarm runs on Unix or Windows.
# This plugin only need to run on Windows but code should be UNIX complient.
def IsWindows():
    PyLogDebug("IsWindows")
    return os.name == 'nt'


# --------------------------------------------------------------------------------------
# Returns '1' if hostname is local, otherwise returns 0.
def IsLocalHost(hostname):
    PyLogDebug("IsLocalHost")
    hostname = hostname.strip("\n\r\t\v ")
    if (hostname == ""):
        return 1
    try:
        hostAddr = socket.gethostbyname(hostname)
        localAddrsList = GetLocalIpAddrs()
        for addr in localAddrsList:
            if (addr == hostAddr):
                return 1
    except:
        PyLogError("Exception occured in IsLocalHost; hostname=" + hostname)
        PyLogError(sys.exc_info()[1])
        return 1
    return 0


# --------------------------------------------------------------------------------------
# Retuns list of local computer ip4 addresses.
# Done by parsing results of ipconfig/ifconfig command output.
def GetLocalIpAddrs():
    PyLogDebug("GetLocalIpAddrs")
    isWindows = IsWindows()
    if isWindows:
        cmd = "ipconfig"
    else:
        cmd = "/sbin/ifconfig"
    addrsList = []
    p = subprocess.Popen([cmd], -1, None, None, subprocess.PIPE, subprocess.PIPE)
    p.wait()
    if (p.returncode == 0):
        outdata = p.stdout.read()
        for line in outdata.splitlines():
            if isWindows:
                m = re.match('\s*IPv4 Address[^:]*\:\s*(\d+\.\d+\.\d+\.\d+)', line)
            else:
                m = re.match('\s*inet addr\:\s*(\d+\.\d+\.\d+.\d+)', line)
            if (m != None):
                addrsList.append(m.group(1).strip())

    return addrsList


# --------------------------------------------------------------------------------------
# Concatenates 2 strings, puts a single space between them, retuns concatenated string.
def AppendToString(toString, toAppendString):
    if (toString == None or toString == "") and toAppendString != None:
        toString = toAppendString
    elif toAppendString != None and toAppendString != "":
        toString = " ".join([toString, toAppendString])
    return toString


##############################################################
#                       The Plugin Extension Class
##############################################################
class SchedulerExtension(ISchedulerPluginExtension):

    # ---------------------------------------------------------------------------------
    # Constructor.
    def __init__(self):
        PyLogDebug("SampleWinPlugin: start initialization")
        self.mSchedulerInitialized = False
        self.mScheduler = None
        self.mJob = None
        self.mMachineListInitialized = False
        self.mMachineListStr = ""
        PyLogDebug("SampleWinPlugin initialized")

    # ---------------------------------------------------------------------------------
    # Destructor.
    def __del__(self):
        PyLogDebug("SampleWinPlugin delete called")
        self.ReleaseScheduler()

    # ---------------------------------------------------------------------------------
    # Clean up function called from destructor.
    def ReleaseScheduler(self):
        PyLogDebug("try to ReleaseScheduler")
        if self.mScheduler == None:
            PyLogDebug("scheduler is None")
        if self.mJob:
            self.mJob = None
        if self.mScheduler:
            PyLogDebug("Really ReleaseScheduler")
            self.mScheduler = None

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Returns plugin name string.
    def GetName(self):
        PyLogDebug("SampleWinPlugin GetName")
        return "SampleWinPlugin"

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Returns plugin description string.
    def GetDescription(self):
        PyLogDebug("SampleWinPlugin GetDescription")
        return "Sample python script plugin for Win HPC scheduler"

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Returns True if it is HPC scheduler environment, False otherwise.
    # Checks if 3 environement variables created by HPC scheduler exist.
    # [To test on local computer set the variables manually].
    def IsProductLaunchedInYourEnvironment(self):
        PyLogDebug("SampleWinPlugin: IsProductLaunchedInYourEnvironmentt")
        if os.environ.get(kClusterNameEnvName) == None or os.environ.get(kJobIdEnvName) == None or os.environ.get(
                kTaskIdEnvName) is None:
            return False
        return True

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Returns plugin name to display (string).
    def GetSchedulerDisplayName(self):
        PyLogDebug("SampleWinPlugin GetSchedulerDisplayName")
        return "Windows HPC Scheduler"

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Returns current HPC job id string, returns empty string on failure.
    def GetThisJobID(self):
        PyLogDebug("SampleWinPlugin GetThisJobID")
        if not self.IsProductLaunchedInYourEnvironment():
            return ""
        res = os.environ.get(kJobIdEnvName)
        if res is None:
            res = ""
        return res

        # ---------------------------------------------------------------------------------

    # ISchedulerPluginExtension API implementation.
    # Returns empty string for HPC scheduler.
    def GetTempDirectory(self):
        PyLogDebug("SampleWinPlugin GetTempDirectory")
        return ""

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Obsolete function, returns empty string.
    def GetMessageStringForSigTerm(self):
        PyLogDebug("SampleWinPlugin GetMessageStringForSigTerm")
        return ""

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # This must return True because we can only add one task per host on Windows HPC.
    def GetUseRSMForEngineLaunch(self):
        PyLogDebug("SampleWinPlugin GetUseRSMForEngineLaunch")
        return True

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Returns list of nodes used for the task, returns empty string on failure.
    # Called once for the lifetime of SampleWinPlugin object.
    def GetMachineListAvailableForDistribution(self):
        PyLogDebug("SampleWinPlugin GetMachineListAvailableForDistribution")
        if not self.IsProductLaunchedInYourEnvironment():
            return ''
        if self.mMachineListInitialized:
            PyLogDebug("GetMachineListAvailableForDistribution(): already initialized");
        else:
            self.InitScheduler()
            self.GetMachineList()
        return self.mMachineListStr

    # ---------------------------------------------------------------------------------
    # ISchedulerPluginExtension API implementation.
    # Launches process either on local machine or on HPC server depending on hostname value.
    def LaunchProcess(self, hostName, exePathName, arg1, arg2):
        PyLogDebug("SampleWinPlugin LaunchProcess")
        ret = 1
        if not self.IsProductLaunchedInYourEnvironment():
            PyLogError("Calling LaunchProcess when not in HPC environment")
            return 1

        # clean all arguments including exePathName
        argList = [exePathName]
        if arg1 != None:
            argList.append(arg1)
        if arg2 != None:
            argList.append(arg2)
        for i in range(len(argList)):
            argList[i] = CleanArgument(argList[i])

        PyLogDebug("LaunchProcess: ExePathName = " + exePathName)

        if IsLocalHost(hostName):
            # If running on local host, subprocess on local host
            PyLogDebug("LaunchProcess: hostName = " + hostName + " is the local host")
            ret = OpenSubprocess(argList)
        else:
            # Launches task on HPC server (job is already launched by Desktop)
            PyLogDebug("LaunchProcess: hostName = " + hostName + " is not the local host")
            ret = self.LaunchRemoteProcess(hostName, argList)
        return ret

    # ---------------------------------------------------------------------------------
    # Launches process either on local machine or on HPC server depending on hostname value.
    def GetMachineList(self):
        PyLogDebug("GetMachineList(): Starting")

        self.mMachineListStr = ""
        self.mMachineListInitialized = True
        maxNumTasks = 0

        if self.mJob == None:
            PyLogError("GetMachineList(): Failed to get job")
            return 1

        coreData = []
        coreData = self.GetCoreData()
        if coreData == None:
            PyLogError("GetMachineList(): Failed to get core data")
            return 1

        # If Job Unit Type is "Core", then each machine appears once per core.
        # If Job Unit Type is "Node", then each machine appears once.
        # A Job Unit Type of "Socket"  or no job unit type is treated the same as "Node"
        jobUnitType = self.mJob.UnitType
        if jobUnitType == JobUnitType.Core:
            PyLogDebug("GetMachineList(): Job unit type is \"Core\"")
            # Append each node to list once per core
            self.FilterCoreData(coreData)
            for eachCore in coreData:
                maxNumTasks = maxNumTasks + eachCore[1]  # One task per core assigned to job
                for i in xrange(eachCore[1]):
                    self.mMachineListStr = AppendToString(self.mMachineListStr, eachCore[0])
        elif jobUnitType == JobUnitType.Socket:
            PyLogDebug("GetMachineList(): Job unit type is \"Socket\"");
            # Append each node to list once per socket
            origData = coreData
            self.FilterCoreData(coreData)
            theLen = min(len(origData), len(coreData))
            for i in xrange(theLen):
                numSockets = self.GetNodeSocketCount(coreData[i][0])
                coresPerSocket = 0
                allocatedSockets = 0;
                if numSockets != 0:
                    coresPerSocket = origData[i][1] / numSockets;
                    if coresPerSocket != 0:
                        allocatedSockets = origData[i][1] / coresPerSocket
                maxNumTasks = maxNumTasks + allocatedSockets  # One task per socket assigned to job
                for i in xrange(allocatedSockets):
                    self.mMachineListStr = AppendToString(self.mMachineListStr, coreData[i][0])
        else:
            PyLogDebug("GetMachineList(): Job unit type is undefined");
            maxNumTasks = len(coreData)  # One task per node assigned to job
            # Append each node to list once
            for eachData in coreData:
                self.mMachineListStr = AppendToString(self.mMachineListStr, eachData[0])

        cmdLine = self.GetCurrentTaskCmdLine()
        numEngines = self.ParseNumEnginesFromDesktopTaskCmdLine(cmdLine)

        # If numEngines is NOT specified, maxNumTasks is same as the number of resource units.
        # MaxNumTasks cannot exceed the number of allocated compute resource units.
        # If more comengines are launched than the number of allocated units,
        # comengines get queued and fail.
        # For these reasons, maxNumTasks must be the lesser of number of compute
        # units, number of parallel engines. It is a common use case to run
        # less number of engines than the number of allocated cores

        if (numEngines > 0 and numEngines < maxNumTasks):
            maxNumTasks = numEngines

        PyLogDebug("GetMachineList(): list=" + self.mMachineListStr);

        # ---------------------------------------------------------------------------------

    # Connects to job created by Desktop; should be called once.
    def ConnectToJob(self):
        PyLogDebug("ConnectToJob(): Starting");
        self.mJob = None
        if self.mScheduler == None:
            PyLogError("ConnectToJob(): error - scheduler is NULL");
            return 1;

        jobId = os.environ.get(kJobIdEnvName)
        if jobId == None or jobId == "":
            PyLogError("ConnectToJob(): error - no job id");
            return 1;

        PyLogDebug("ConnectToJob: jobId:" + jobId)
        try:
            ljobId = long(jobId)
            if ljobId > 0:
                self.mJob = self.mScheduler.OpenJob(ljobId);
        except:
            PyLogError("ConnectToJob(): exception")
            PyLogError(sys.exc_info()[1])
            return 1

        if self.mJob != None:
            PyLogDebug("ConnectToJob(): Done")
            return 0
        else:
            PyLogError("ConnectToJob(): unable to open job")
            return 1

    # ---------------------------------------------------------------------------------
    # Initializes HPC scheduler; should be called once.
    def InitScheduler(self):
        if self.mSchedulerInitialized:
            return
        self.mSchedulerInitialized = True

        PyLogDebug("ConnectToScheduler(): Starting");

        clusterName = os.environ.get(kClusterNameEnvName);
        if clusterName == None:
            PyLogError("ConnectToScheduler(): no cluster name")
            return 1
        PyLogDebug("InitScheduler: cluster name from environment var:" + clusterName)

        self.mScheduler = Scheduler()
        if self.mScheduler == None:
            PyLogError("ConnectToScheduler(): failed to create scheduler")
            return 1

        try:
            self.mScheduler.Connect(clusterName)
        except:
            PyLogError("InitScheduler(): No connection to cluster")
            return 1
        PyLogDebug("ConnectToScheduler(): connected to scheduler")
        ret = self.ConnectToJob()
        if ret:  # error
            PyLogError("ConnectToScheduler(): unable to connect to job")
            self.ReleaseScheduler()
        PyLogDebug("ConnectToScheduler: done")
        return ret

    # ---------------------------------------------------------------------------------
    # Launches remote process using Windows HPC scheduler.
    def LaunchRemoteProcess(self, hostName, argList):
        PyLogDebug("LaunchRemoteProcess(): starting")
        for args in argList:
            PyLogDebug(args)
        ret = self.InitScheduler()
        if ret or self.mScheduler == None or self.mJob == None:
            PyLogError("LaunchRemoteProcess(): scheduler or job not found")
            return 1

        PyLogDebug("LaunchRemoteProcess(): scheduler initialized")

        # Create the task
        task = self.mJob.CreateTask()
        if task == None:
            PyLogError("LaunchRemoteProcess(): unable to create task");
            return 1
        PyLogDebug("LaunchRemoteProcess(): task created")

        # set the machine we're running on
        pNodes = self.mScheduler.CreateStringCollection()
        if pNodes == None:
            return 1
        pNodes.Add(hostName);
        task.RequiredNodes = pNodes

        # Set the task command line
        for i in xrange(len(argList)):
            if " " in argList[i]:
                argList[i] = '"' + argList[i] + '"'
        task.CommandLine = " ".join(argList)

        PyLogDebug("LaunchRemoteProcess(): task command line")
        PyLogDebug(task.CommandLine)
        if self.CopyComputeResourceUnitsFromFirstTask(task):  # error
            PyLogError("LaunchRemoteProcess(): CopyComputeResourceUnitsFromFirstTask returned false");
            # Instead of failing, use 1 resource unit for task
            # (resort to earlier behavior before this code change)
            task.MinimumNumberOfCores = 1
            task.MaximumNumberOfCores = 1
        PyLogDebug("LaunchRemoteProcess(): CopyComputeResourceUnitsFromFirstTask")

        strEnd = argList[0].rfind("\\")
        if strEnd == -1:
            workDir = ""
        else:
            workDir = argList[0][:strEnd]

        task.WorkDirectory = workDir
        PyLogDebug("LaunchRemoteProcess(): set work directory to:" + workDir)

        # Set the task display name
        task.Name = "Remote Engine Task"

        # Code to set env vars for logging
        PyLogDebug("LaunchRemoteProcess(): trying to set task env variables");

        self.SetTaskEnvironmentVar(task, kDebugMode)
        self.SetTaskEnvironmentVar(task, kDebugLog)
        self.SetTaskEnvironmentVar(task, kDebugLogSeparate);

        # Submit the task
        self.mJob.SubmitTask(task)
        PyLogDebug("LaunchRemoteProcess(): successfully submitted task");
        return 0

    # ---------------------------------------------------------------------------------
    # Sets environment variable to task.
    def SetTaskEnvironmentVar(self, task, envName):
        PyLogDebug("SetTaskEnvironmentVar(): name: " + envName)
        envValue = os.environ.get(envName)
        if envValue != None:
            task.SetEnvironmentVariable(envName, envValue)
            PyLogDebug("SetTaskEnvironmentVar(): set to: " + envValue)
        else:
            PyLogError("SetTaskEnvironmentVar(): unable to set ")

    # ---------------------------------------------------------------------------------
    # Opens task on Windows HPC Scheduler.
    def GetCurrentTask(self):
        PyLogDebug("GetCurrentTask begin");

        taskIdString = os.environ.get(kTaskIdEnvName)
        if self.mScheduler == None or self.mJob == None or taskIdString == None or taskIdString == "":
            return None

        PyLogDebug("GetCurrentTask: taskId:" + taskIdString)
        try:
            jobTaskId = long(taskIdString)
        except:
            PyLogError("GetCurrentTask(): exception")
            PyLogError(sys.exc_info()[1])
            return None
        if jobTaskId <= 0:
            return None

        taskId = None
        try:
            taskId = self.mScheduler.CreateTaskId(jobTaskId)
        except:
            PyLogError("Exception occured in CreateTaskId")
            PyLogError(sys.exc_info()[1].message)
            return None

        task = self.mJob.OpenTask(taskId)
        if task != None:
            PyLogDebug("Successful return from GetCurrentTask")
        return task

    # ---------------------------------------------------------------------------------
    # Copies resources from existing task to a new one.
    def CopyComputeResourceUnitsFromFirstTask(self, newTask):
        PyLogDebug("CopyComputeResourceUnitsFromFirstTask: start")
        fTask = self.GetCurrentTask()  # Current task is the desktop task, which is the first task
        if fTask == None:
            PyLogError("CopyComputeResourceUnitsFromFirstTask(): Unable to get desktop task of job")
            return 1
        jobUnitType = self.mJob.UnitType
        if jobUnitType == JobUnitType.Core:
            PyLogDebug("CopyComputeResourceUnitsFromFirstTask(): Job unit type is \"Core\"");
            newTask.MinimumNumberOfCores = fTask.MinimumNumberOfCores
            newTask.MaximumNumberOfCores = fTask.MaximumNumberOfCores
        elif jobUnitType == JobUnitType.Socket:
            PyLogDebug("CopyComputeResourceUnitsFromFirstTask(): Job unit type is \"Socket\"");
            newTask.MinimumNumberOfSockets = fTask.MinimumNumberOfSockets
            newTask.MaximumNumberOfSockets = fTask.MaximumNumberOfSockets
        elif jobUnitType == JobUnitType.Node:
            PyLogDebug("CopyComputeResourceUnitsFromFirstTask(): Job unit type is \"Node\"");
            newTask.MinimumNumberOfNodes = 1
            newTask.MaximumNumberOfNodes = 1
        else:
            PyLogError("CopyComputeResourceUnitsFromFirstTask(): Unable to define job unit type")
            return 1
        PyLogDebug("CopyComputeResourceUnitsFromFirstTask: done")
        return 0

    # ---------------------------------------------------------------------------------
    # Returns current task command line.
    def GetCurrentTaskCmdLine(self):
        task = self.GetCurrentTask();
        if task == None: return None

        commandLine = task.CommandLine
        PyLogDebug("GetCurrentTaskCmdLine is: " + commandLine)

        return commandLine

    # ---------------------------------------------------------------------------------
    # Returns list of [nodes, number of cores] for each node .
    def GetCoreData(self):
        coreData = []
        nodeCount = 0

        if self.mJob == None:
            PyLogError("GetCoreData(): no job available")
            return None

        # get allocated nodes for the job from MS HPC scheduler
        jobNodeCollection = self.mJob.AllocatedNodes
        if jobNodeCollection == None:
            PyLogError("GetCoreData(): failed to get job node collection");
            return None
        PyLogDebug("GetCoreData(): got job node collection");

        nodeCount = jobNodeCollection.Count

        for i in xrange(nodeCount):
            nodeName = jobNodeCollection.Item[i]
            nodeCores = self.GetNodeCoreCount(nodeName)
            coreData.append([nodeName, nodeCores])
            PyLogDebug("GetCoreData(): added:" + nodeName)

        self.SortCoreData(coreData)
        return coreData

    # ---------------------------------------------------------------------------------
    # Filters coreData list.
    def FilterCoreData(self, coreData):
        self.InitScheduler()
        if self.mScheduler == None or self.mJob == None:
            PyLogError("FilterCoreData(): scheduler or job interface not found")
            return

        thisJobId = self.mJob.Id
        if not thisJobId:
            PyLogError("FilterCoreData(): cannot get job id")
            return
        status = True
        coreCount = 0
        dataCopy = []
        for data in coreData:
            nodeName = data[0]
            nodeCores = data[1]
            allocatedCores = 0;
            node = self.mScheduler.OpenNodeByName(nodeName)
            if node == None:
                PyLogError("FilterCoreData(): unable to open node")
                return
            coreCollection = node.GetCores()
            if coreCollection == None:
                PyLogError("FilterCoreData(): unable to get cores of node")
            return
            for eachCore in coreCollection:
                jobId = eachCore.JobId
                if jobId == thisJobId:
                    PyLogDebug("FilterCoreData(): job id matches this this job id ")
                    allocatedCores = allocatedCores + 1

            dataCopy.append([nodeName, allocatedCores])

        coreData = dataCopy

    # ---------------------------------------------------------------------------------
    # Returns number of cores for specified node.
    def GetNodeCoreCount(self, nodeName):
        if self.mScheduler == None:
            return 0
        node = self.mScheduler.OpenNodeByName(nodeName)
        if node == None:
            PyLogError("GetNodeCoreCount(): Unable to open node by name")
            return 0

        result = node.NumberOfCores
        PyLogDebug("GetNodeCoreCount(): success")
        return result

    # ---------------------------------------------------------------------------------
    # Returns number of sockets for specified node.
    def GetNodeSocketCount(self, nodeName):
        if self.mScheduler == None:
            return 0
        node = self.mScheduler.OpenNodeByName(nodeName)
        if node == None:
            PyLogError("GetNodeSocketCount(): Unable to open node by name")
            return 0
        result = node.NumberOfSocket
        PyLogDebug("GetNodeSocketCount(): success")
        return result

    # ---------------------------------------------------------------------------------
    # Ensures that the local host is the first host in the collection.
    def SortCoreData(self, coreData):
        for i in xrange(len(coreData)):
            if IsLocalHost(coreData[i][0]):
                if i == 0:  # done
                    return
                theData = coreData.pop(i)
                coreData.insert(0, theData)
                return

    # ---------------------------------------------------------------------------------
    # Parses command line for the job to find number of engines (format: "-machinelist num=#")
    # Return of -1 from this function means one of the following:
    #   Commandline is incorrect;
    #   Job is serial;
    #   Job is pure DSO and engines run on each allocated compute resource unit;
    def ParseNumEnginesFromDesktopTaskCmdLine(self, commonArgs):
        PyLogDebug("ParseNumEnginesFromDesktopTaskCmdLine  :" + commonArgs)
        iFrom = commonArgs.find(kMachineListOption)
        if iFrom < 0:
            return -1

        rgtSide = commonArgs[iFrom + len(kMachineListOption):]
        splitList = rgtSide.split("=", 1)

        if splitList[0].strip() == "num" and len(splitList) > 1:
            numList = splitList[1].split()
            try:
                num = long(numList[0])
            except:
                PyLogError("ParseNumEnginesFromDesktopTaskCmdLine: exception - not a number")
                return -1
            PyLogDebug("ParseNumEnginesFromDesktopTaskCmdLine:" + numList[0])
            return num

        PyLogError("ParseNumEnginesFromDesktopTaskCmdLine failed")
        return -1



