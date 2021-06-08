import sys
import clr
import os
import inspect


clr.AddReferenceToFile("Microsoft.Hpc.Scheduler")
clr.AddReferenceToFile("Microsoft.Hpc.Scheduler.Properties")
from Microsoft.Hpc.Scheduler import *
from Microsoft.Hpc.Scheduler.Properties import *


class hpc_scheduler(object):
    def __init__(self):
        self.schedulername = None
        self.JobName = None
        self.CommandLine = None
        self.SendNotificationEmails = None
        self.EmailAddress = None
        self.UseExclusiveNodes = None
        self.NodeInfoTable = None
        self.JobInfoTable = None
        self.UseCredential = False
        self.Login = None
        self.Password = None
        self.JobTemplate = None

    def GetClusterInfo(self):
        self.NodeInfoTable.Rows.Clear()
        scheduler = Scheduler()
        try:
            scheduler.Connect(self.schedulername)
            if self.UseCredential:
                scheduler.SetCachedCredentials(self.Login, self.Password)
        except:
            self.AddLog('Failed to connect on clusterhead node {0}'.format(self.schedulername))
        try:
            NodeList = self.GetNodeList(scheduler)
            for node in NodeList:
                self.NodeInfoTable.Rows.Add(node.Name, node.NumberOfCores.ToString(), self.GetNodeLoad(node),
                                            node.State.ToString())
        except:
            pass
        # JobTemplates = list(scheduler.GetJobTemplateList())
        scheduler.Dispose()

    # return JobTemplates

    def GetClusterJobTemplate(self):
        scheduler = Scheduler()
        scheduler.Connect(self.schedulername)
        JobTemplates = list(scheduler.GetJobTemplateList())
        scheduler.Dispose()
        return JobTemplates

    def GetJobsInfo(self):
        self.JobInfoTable.Rows.Clear()
        scheduler = Scheduler()
        scheduler.Connect(self.schedulername)
        if self.UseCredential:
            scheduler.SetCachedCredentials(self.Login, self.Password)
        JobList = self.GetJobList(scheduler)
        for job in JobList:
            self.JobInfoTable.Rows.Add(job.Id, job.Owner, job.StartTime.ToString())
        scheduler.Dispose()

    def GetNodeList(self, scheduler):
        filter = IScheduler.CreateFilterCollection(scheduler)
        filter.Add(FilterOperator.GreaterThanOrEqual, PropId.Node_NumCores, 1)
        sortOn = scheduler.CreateSortCollection()
        sortOn.Add(SortProperty.SortOrder.Ascending, PropId.Node_NumCores)
        nodes = scheduler.GetNodeList(filter, sortOn)
        return nodes

    def GetJobList(self, scheduler):
        JobList = scheduler.GetJobList(None, None)
        ActiveJobs = [job for job in JobList if job.State.ToString() == 'Running']
        return ActiveJobs

    def GetNodeLoad(self, node):
        Cores = node.GetCores()
        NbCoresBusy = 0
        for core in Cores:
            if not core.State.ToString() == 'Idle':
                NbCoresBusy += 1
        NodeLoad = (NbCoresBusy / Cores.Count) * 100
        return str(NodeLoad)

    def CreateJob(self, scheduler):
        job = scheduler.CreateJob()
        job.Name = self.JobName
        job.IsExclusive = True
        job.AutoCalculateMax = True
        job.AutoCalculateMin = True
        job.SetJobTemplate(self.JobTemplate)
        task = job.CreateTask()
        task.CommandLine = self.CommandLine
        job.AddTask(task)
        scheduler.SubmitJob(job, None, None)
        print
        "Job has been submitted. ID: ", job.Id
        return job.Id

    def GetJobStatus(self, jobid):
        scheduler = Scheduler()
        scheduler.Connect(self.schedulername)
        if self.UseCredential:
            scheduler.SetCachedCredentials(self.Login, self.Password)
        job = scheduler.OpenJob(jobid)
        scheduler.Dispose()
        return job.State.ToString()

    def SubmitHpcJob(self):
        scheduler = Scheduler()
        if not self.schedulername == None:
            scheduler.Connect(self.schedulername)
            if self.UseCredential:
                scheduler.SetCachedCredentials(self.Login, self.Password)
            jobId = self.CreateJob(scheduler)
            return jobId




