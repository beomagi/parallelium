# parallelium
Run shell commands in parallel while limiting the number of processes for CPU to cope

Usage:
./parallelium -f jobfile [-l logs-folder] [-p parallel-jobs] (future) [-t tag1,tag2,tag3...]

* -f jobfile       : Required. A list of commands, one per line. Comments can be used as job control parameters.
* -l logs-folder   : Optional. Output to screen if not preset. If present, then for each job in the jobfile, an output log ./logs-folder/jobfile_linenumber.txt
* -p parallel-jobs : Optional. Used to specify a strict number of parallel jobs. If not present, then machine CPU count is used.
* -t tag1,..tagn   : Optional. Commands in jobfile can be tagged. If present, this option only runs commands with this tag.


## Jobfile format:
command1

command2

command3

#optional comment

command4

#### Note:

\#comments are optional, and can control execution somewhat.

\#tag Thisisatag run5mins rundaily <-- All jobs after carry these tags.

\#cpu n              <-- Specify the load on the cpu for all following jobs. Default is 1.(future)


Sample Run:
![Sample Run](./images/parallelium_sample_run.png)
