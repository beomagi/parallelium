#!/usr/bin/env python3
import sys
import json
import subprocess
import copy
import random
import time

def paramget(paramflag):
    args=sys.argv
    if paramflag in args:
        argvalue=args[args.index(paramflag)+1]
        return argvalue
    return None

def jobtext2joblist(jobtext):
    joblist=[]
    tags=[]
    joblines=jobtext.split("\n")
    linenumber=0
    for jobdesc in joblines:
        linenumber+=1
        #if line empty move on
        if jobdesc.strip()=="": continue
        #if line starts with "#" then this controls jobs
        if jobdesc.startswith("#"):
            #get directive command and params
            syscmd=jobdesc[1:].split(" ")[0]
            try:
                sysparams=jobdesc.split(" ")[1:]
                while "" in sysparams:
                    sysparams.remove("")
            except BaseException:
                sysparams=None
            #Have job directive command and params, handle job directives
            if syscmd=="tag":
                tags=sysparams
            continue #directive handled, next line
        else: #Not blank, nor a directive, assume a command
            ajob={}
            ajob["cmd"]=jobdesc
            ajob["tags"]=tags.copy()
            ajob["line"]=linenumber
            ajob["processes"]=1
            ajob["status"]=0
            joblist.append(ajob)
    return joblist


def loadjobs(todo,currentjoblist,parallel,randomize):
    proc_used=0
    for ajob in currentjoblist:
        proc_used+=ajob["processes"]
    if len(todo)>0:
        if proc_used<parallel:
            if randomize:
                pulljobindex=int(random.random()*len(todo))
            else:
                pulljobindex=0
            pulledjob=todo.pop(pulljobindex)
            currentjoblist.append(pulledjob)

def execute_jobs(currentjoblist):
    finished_jobs=[]
    jobcount=len(currentjoblist)

    jobidx=0
    while jobidx<jobcount:
        jobstatus=currentjoblist[jobidx]["status"]
        if jobstatus==0: #job waiting to be started
            jobcmd=currentjoblist[jobidx]["cmd"]
            popenobj=subprocess.Popen(jobcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            currentjoblist[jobidx]["popenobj"]=popenobj
            currentjoblist[jobidx]["status"]=1
            currentjoblist[jobidx]["starttime"]=time.time()
        if jobstatus==1: #job is running, handle termination
            popenobj=currentjoblist[jobidx]["popenobj"]
            chkalive=popenobj.poll()
            if chkalive!=None:
                output=popenobj.stdout.read()
                currentjoblist[jobidx]["output"]=output
                currentjoblist[jobidx]["endtime"]=time.time()
                currentjoblist[jobidx]["status"]=2
        if jobstatus==2: #job is finished, pop from running and move to finished_jobs
            finishedjob=currentjoblist.pop(jobidx)
            finished_jobs.append(finishedjob)
            jobcount=len(currentjoblist)
        else:
            jobidx+=1
    return finished_jobs


def runjobs(joblist,parallel=4,randomize=False):
    todo=copy.deepcopy(joblist)
    currentjoblist=[]
    cntr=0
    restperiod=0.01
    while len(todo)+len(currentjoblist)>0:
        cntr+=1
        loadjobs(todo,currentjoblist,parallel,randomize)
        completed_jobs=execute_jobs(currentjoblist)
        for finishedjob in completed_jobs:
            output=finishedjob["output"]
            print(output)
        if (cntr%(1.0/restperiod))==0:
            print("jobcountstatus: {} {} {}".format(len(todo),len(currentjoblist),0))
        time.sleep(restperiod)


if __name__=="__main__":
    jobfile=paramget("-f")
    if not jobfile:
        print("missing: -f jobfile")
        exit(1)
    with open(jobfile,"r") as fh:
        jobtext=fh.read()

    joblist=jobtext2joblist(jobtext)
    runjobs(joblist,parallel=28)
