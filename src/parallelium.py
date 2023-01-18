#!/usr/bin/env python3
import sys
import json
import subprocess
import copy
import random
import time
import os

filename=""

def paramget(paramflag):
    args=sys.argv
    if paramflag in args:
        argvalue=args[args.index(paramflag)+1]
        return argvalue
    return None

def jobtext2joblist(jobtext):
    """take text from file parse it,
    apply tags and other directives
    create joblist for execution"""
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
    """take list of jobs todo and current, max parallel
    and random pick. If current is less that parallel,
    move from todo to current running"""
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
    """check all jobs currently running and use status
    to start, or handle their termination. return
    list of terminated jobs and remove them from current
    running joblist."""
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
                output=popenobj.stdout.read().decode('utf-8')
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


def logoutput(output,logdir,logfileprefix,linenumber):
    outfname=logdir+os.sep+logfileprefix+"_"+linenumber+".txt"
    outfname=outfname.replace(os.sep+os.sep,os.sep) #cater for double //
    with open(outfname,'w') as fh:
        fh.write(output)

def runjobs(joblist,parallel=4,randomize=False,logdir=None,logfileprefix=None):
    """Manage the full joblist. keep running set amount
    in parallel, and handle termination and output"""
    todo=copy.deepcopy(joblist)
    currentjoblist=[]
    cntr=0
    restperiod=0.01
    job_finish_count=0
    inittime=time.time()
    print("   RunTime   ToDo   Now   Fin")
    while len(todo)+len(currentjoblist)>0:
        cntr+=1
        loadjobs(todo,currentjoblist,parallel,randomize)
        completed_jobs=execute_jobs(currentjoblist)
        job_finish_count+=len(completed_jobs)
        for finishedjob in completed_jobs:
            output=finishedjob["output"]
            if logdir:
                lead0=str(1000000+finishedjob["line"])[-4:]
                logoutput(output,logdir,logfileprefix,lead0)
            else:
                print(output)
        if (cntr%(1.0/restperiod))==0:
            currtime=time.time()
            passtime=float(int((currtime-inittime)*1000))/1000
            padding="                   "
            formtime=(padding+str(passtime))[-10:]
            formlentodo=(padding+str(len(todo)))[-5:]
            formlencurr=(padding+str(len(currentjoblist)))[-5:]
            formfincnt=(padding+str(job_finish_count))[-5:]
            print("{}: {} {} {}".format(formtime,formlentodo,formlencurr,formfincnt))
        time.sleep(restperiod)
    currtime=time.time()
    passtime=float(int((currtime-inittime)*1000))/1000
    padding="                   "
    formtime=(padding+str(passtime))[-10:]
    formlentodo=(padding+str(len(todo)))[-5:]
    formlencurr=(padding+str(len(currentjoblist)))[-5:]
    formfincnt=(padding+str(job_finish_count))[-5:]
    print("{}: {} {} {}".format(formtime,formlentodo,formlencurr,formfincnt))


if __name__=="__main__":
    #--handle parameters
    maxprocs=paramget("-p")
    if maxprocs==None:
        import multiprocessing
        maxprocs=multiprocessing.cpu_count()
    else:
        maxprocs=int(maxprocs)
    jobfile=paramget("-f")
    logdir=paramget("-l")
    logfileprefix=None
    if logdir:
        logfileprefix=jobfile
        if not os.path.isdir(logdir):
            print("{} folder does not exist".format(logdir))
            sys.exit(2)
    #--end handle parameters

    if not jobfile:
        print("missing: -f jobfile")
        exit(1)
    with open(jobfile,"r") as fh:
        jobtext=fh.read()

    joblist=jobtext2joblist(jobtext)
    runjobs(joblist,parallel=maxprocs,logdir=logdir,logfileprefix=logfileprefix)
