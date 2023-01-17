#!/usr/bin/env python3
import sys
import json

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
            joblist.append(ajob)
    return joblist





if __name__=="__main__":
    jobfile=paramget("-f")
    if not jobfile:
        print("missing: -f jobfile")
        exit(1)
    with open(jobfile,"r") as fh:
        jobtext=fh.read()

    joblist=jobtext2joblist(jobtext)
    print(json.dumps(joblist))
