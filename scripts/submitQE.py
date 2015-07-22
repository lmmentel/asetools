#!/usr/bin/env python

'''Script used to generate the submission script for batch systems'''

from __future__ import print_function

import numpy as np
import os
import re
import socket
import subprocess
import operator
from asetools import get_template, get_config
from argparse import ArgumentParser
from datetime import datetime
from string import Template

def main(args):

    parser = ArgumentParser(usage='Script used to generate submission script for batch systems')
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('input',
                        default='input.py',
                        help='Name of input file(s) that you want copied to the compute node. Default=input.py')
    group.add_argument("-H", "--HOST",
                       default="",
                       help="destination hostname, default=''")
    group.add_argument("-n", "--nodes",
                       default="1",
                       help="number of nodes, default=1")
    parser.add_argument('-d', '--dryrun',
                        action='store_true',
                        help='Create sbatch script, but do not submit.')
    parser.add_argument("-e",
                        "--extrafiles",
                        nargs="+",
                        default=None,
                        help="additional files that need to be copied to the node/scratch")
    parser.add_argument('--nativeqe',
                        action="store_true",
                        default=False,
                        help='Runs internal espresso routines, instead of through the ase-espresso interface')
    parser.add_argument('-p', '--ppn',
                        default='16',
                        help='Number of cores. Default=16 (one full node)')
    parser.add_argument('--projectno',
                        default='nn4683k',
                        help='NOTUR project number. Retrieve it with PROJECT command.')
    parser.add_argument("-q",
                        "--queue",
                        default="default",
                        help="destination queue, default=default")
    parser.add_argument("-s", "--scratch",
                        action="store_true",
                        help="use node scratch directory (/scratch/$USER), default=False")
    parser.add_argument("-t", "--walltime",
                        default="120:00:00",
                        help="walltime in the format HH:MM:SS, default=120:00:00")
   
    if args: #arguments passed from other python code
	args = vars(parser.parse_args(args))
    else:  #run from command line
	args = vars(parser.parse_args())

    args['workdir'] = os.getcwd()
    args['jobname'] = os.path.splitext(args["input"])[0]
    args['outfile'] = args['jobname'] + ".out"
    args['script_name'] = "run." + args['jobname']

    submit(args)

def submit(args):
    '''
    Submit a job to the batch system defined by the "batch" variable with the
    job details specified in the args object.

    args: (dict)
        arguments specifying the job
    '''

    submitters = {"pbs" : submit_pbs,
                  "slurm" : submit_slurm,
                 }

    # get the site configuration from the $HOME/.asetools_site_config.py file
    # and merge it into the args dictionary

    site_config = get_config()
    args.update(site_config)

    submitter = submitters.get(args['batch'].lower(), None)
    if submitter is not None:
        submitter(args)
    else:
        raise NotImplementedError("support for '{0:s}' is not implemented \
                supported batch systems are: {1:s}".format(args['batch'], ", ".join(submitters.keys())))

def submit_pbs(args):
    '''
    Write the run script for PBS and submit it to the queue.
    '''

    with open(args['script_name'], 'w') as script:
        script.write("#PBS -S /bin/bash\n")
        if args['HOST'] != "":
            script.write("#PBS -l nodes={0}:ppn={1}\n".format(args['HOST'], args['ppn']))
        else:
            script.write("#PBS -l nodes={0}:ppn={1}\n".format(args['nodes'], args['ppn']))
        script.write("#PBS -l walltime={0}\n\n".format(args['walltime']))
        if args['lib_paths'] is not None and args['lib_paths'] != "":
            script.write('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{0:<s}\n\n'.format(":".join(args['lib_paths'])))
        if args['vars']:
            for name, value in args['vars']:
                script.write("export {n}={v}\n".format(n=name, v=value))
        script.write("#PBS -N {}\n".format(args["jobname"]))
        if args["queue"] != "default":
            script.write("#PBS -q {}\n".format(args["queue"]))
        script.write("cd $PBS_O_WORKDIR\n")
        if args['scratch']:
            wrkdir = os.path.join(args['scratch'], args['jobname'])
            script.write("mkdir -p {}\n".format(wrkdir))
            files = args['input']
            if args['extrafiles']:
                files += ' ' + ' '.join(args['extrafiles'])
            script.write('cp -t {0} {1}\n'.format(wrkdir, files))
            script.write('cd {0}\n'.format(wrkdir))
        if args['nativeqe']:
            execute = "\n/share/apps/bin/mpirun -np {0} {1:<s} -in {2:<s}\n".format(
                        args['ppn'], args['executable'], args['input'])
        else:
            execute = "\n{p:s} {i:s}".format(p=args['python'], i=args['input'])
        script.write(execute)

    # submit the job to the queue if requested
    if args['dryrun']:
        print("Created job script: {0}\n NOT submitting to the queue\nbye...".format(args['script_name']))
    else:
        print("Created job script: {0}\nsubmitting to the queue".format(args['script_name']))
        sublog = open(args['jobname'] + ".sublog", 'w')
        subprocess.Popen(["qsub", args['script_name']], stdout=sublog, stderr=sublog)
        sublog.close()

def submit_slurm(args):
    '''
    Write the run script for SLURM and submit it to the queue.
    '''
    modules = ['python2','espresso/5.0.3_beef'] #5.0.3 is 5.0.2 with openmpi1.8

    if int(args["ppn"]) >= 16:
        ncpu_per_node = 16
    else:
        ncpu_per_node = int(args["ppn"])
    nnodes = int(np.ceil(int(args["ppn"])/16.0)) #NB: means that for >16 CPUs, the script will automatically fully allocate all nodes, i.e. up to 15 more CPUs than requested

    if args["nativeqe"]:
        commands = 'cp *.inp $SCRATCH\ncd $SCRATCH\nmpirun pw.x < pw.inp > pw.out\nmpirun ph.x < ph.inp > ph.out\nmpirun dynmat.x < dynmat.inp > dynmat.out'
        cleanup = 'cp -r pw.out dyn.traj ph.out dynmat.dat dynmat.out dynmat.mold calc.save _ph0/calc.phsave $SUBMITDIR'
    else:
        commands = "python " + args["input"]
        cleanup = ""

    skipped = ['batch', 'extrafiles', 'home', 'HOST', 'local_scr', 'vars']
    strargs = "".join(["{0:>15s}".format(str(args[k])) for k in sorted(args.keys())
                      if not k in skipped])

    if os.path.isfile(args['script_name']):
	print('Using existing job script: {0}'.format(args['script_name']))
    else:
	print('Creating job script: {0}'.format(args['script_name']))
    	with open(args['script_name'], 'w') as script:
        	script.write("#!/bin/bash\n")
        	script.write("#SBATCH --job-name={}\n".format(args['workdir'][-8:]))
        	script.write("#SBATCH --account={}\n".format(args["projectno"]))
        	script.write("#SBATCH --time={}\n".format(args["walltime"]))
        	script.write("#SBATCH --mem-per-cpu=3700M\n")
        	script.write("#SBATCH --nodes={0} --ntasks-per-node={1}\n".format(nnodes, ncpu_per_node))
        	script.write("#SBATCH --mail-type=FAIL\n")
        	script.write("\n# Set up job environment\n")
        	script.write("source {}\n".format(os.path.join(args["home"], ".bash_profile")))
        	script.write("source /cluster/bin/jobsetup\n")
        	script.write("module load {}\n".format(" ".join(modules)))
        	script.write("\n# Automatic copying of files and directories back to $SUBMITDIR\n")
        	if cleanup != "":
            	   script.write("cleanup {}\n".format(cleanup))
        	script.write("\n# Do the work\n")
        	script.write("{}\n".format(commands))
        	script.write("\n# update the list of completed jobs\n")
        	script.write('echo `date +%F_%R` $JOB_ID $SUBMITDIR $JOB_NAME >> $HOME/completed_jobs.dat\n')

    # submit the job to the queue if requested
    if args['dryrun']:
        print("NOT submitting to the queue\nbye...".format(args['script_name']))
    else:
        output = subprocess.check_output(["sbatch", args['script_name']])
	
        patt = re.compile(r"Submitted batch job\s*(\d+)")
        m = patt.search(output)
        if m:
            pid = str(m.group(1))
            with open(os.path.join(args['home'], "submitted_jobs.dat"), "a") as dat:
		dat.write('{0} {1:>12s} {2:>20s}\n'.format(
                   pid, os.getcwd(), str(datetime.now().strftime("%Y-%m-%d+%H:%M:%S"))))
        else:
            pid = None
	
	print("Submitted batch job {0}".format(pid))

        # save the sublog file for reference
        #with open(args['jobname'] + ".sublog", 'w') as slog:
        #    slog.write(output)

def header(args, skipped):

    out = "{0:^16s} {1:^12s} {2:^20s}".format("Date", "Job ID", "Submit dir")
    out += "".join(["{0:>15s}".format(k) for k in sorted(args.keys()) if not k in skipped])
    return out

if __name__ == "__main__":
    main(None)