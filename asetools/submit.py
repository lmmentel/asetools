#!/usr/bin/env python

'''Script used to generate the submission script for batch systems'''

from __future__ import print_function

import numpy as np
import os
import sys
import re
import socket
import subprocess
import operator
from asetools import get_template, get_config
from argparse import ArgumentParser
from datetime import datetime
from string import Template


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaning
    an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def main(args=None):

    parser = ArgumentParser(usage='script used to generate submission script for batch systems')
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('input',
                        default='input.py',
                        help='Name of input file(s) that you want copied to the compute node. Default=input.py')
    group.add_argument("-H", "--HOST",
                       default="",
                       help="destination hostname, default=''")
    group.add_argument("-n", "--nodes",
                       type=int,
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
    parser.add_argument('--program',
                        default='pythonqe',
                        help='Specify which program to run. pythonqe: prepares script for running quantum espresso through the ase-espresso interface. nativeqe: runs internal espresso routines. manual: specify executions manually. Default: pythonqe.')
    parser.add_argument('-m',
                        '--mem-per-cpu',
                        default='3700M',
                        help='Memory per cpu, default=3700M')
    parser.add_argument('-p', '--ppn',
                        type=int,
                        default=16,
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

def write_slurm_script(args):
    'Write a SLURM run script with variables from args dict'

    with open(args['script_name'], 'w') as script:
        script.write("#!/bin/bash\n")
        script.write("#SBATCH --job-name={}\n".format(args['workdir'][-8:]))
        script.write("#SBATCH --account={}\n".format(args["projectno"]))
        script.write("#SBATCH --time={}\n".format(args["walltime"]))
        script.write("#SBATCH --mem-per-cpu={}\n".format(args['mem_per_cpu']))
        script.write("#SBATCH --nodes={0} --ntasks-per-node={1}\n".format(args['nodes'], args['ppn']))
        script.write("#SBATCH --mail-type=FAIL\n")
        script.write("\n# Set up job environment\n")
	if args['program'] in ['pythonqe','nativeqe']:
           script.write("source {}\n".format(os.path.join(args["home"], ".bash_profile")))
        script.write("source /cluster/bin/jobsetup\n")
	if args['cleanup'] is not None:
                script.write("\n# Automatic copying of files and directories back to $SUBMITDIR\n")
                script.write("cleanup \"{}\"\n".format(args['cleanup']))
        script.write("\n# Do the work\n")
        script.write("{}\n".format(args['commands']))
        script.write("\n# update the list of completed jobs\n")
        script.write('echo `date +%F_%R` $JOB_ID $SUBMITDIR $JOB_NAME >> $HOME/completed_jobs.dat\n')

def submit_slurm(args):
    '''
    Write the run script for SLURM and submit it to the queue.
    '''

    if int(args["ppn"]) > 16:
        args['nodes'] = int(np.ceil(int(args["ppn"])/16.0)) #NB: means that for >16 CPUs, the script will automatically fully allocate all nodes, i.e. up to 15 more CPUs than requested
        args['ppn'] = 16

    if args['program'] == 'pythonqe':
	args['commands'] = "module load python2 espresso/5.0.3_beef\npython " + args["input"]
	args['cleanup'] = None
    elif args['program'] == 'nativeqe':
        args['commands'] = '\n'.join(['module load espresso/5.0.3_beef','cp *.inp $SCRATCH','cd $SCRATCH','mpirun pw.x < pw.inp > pw.out','mpirun ph.x < ph.inp > ph.out','mpirun dynmat.x < dynmat.inp > dynmat.out']) #5.0.3 is 5.0.2 with openmpi1.8
        args['cleanup'] = 'cp -r $SCRATCH/pw.out $SCRATCH/dyn.traj $SCRATCH/ph.out $SCRATCH/dynmat.dat $SCRATCH/dynmat.out $SCRATCH/dynmat.mold $SCRATCH/calc.save $SCRATCH/_ph0/calc.phsave $SUBMITDIR'
    elif args['program']  == 'lammps':
	commands = ['module purge','module load intelmpi.intel']
	files = ['$HOME/bin/lmp.double',args['input']]
	if args['extrafiles']:	
	   files += args['extrafiles']
	commands += ['cp '+' '.join(files)+' $SCRATCH']
	commands += ['cd $SCRATCH','mpirun -env KMP_AFFINITY scatter -env OMP_NUM_THREADS 1 -np {0} ./lmp.double -in {1} -screen none ##-log none'.format(args['ppn'],args['input'])]
	args['commands'] = '\n'.join(commands)

	args['cleanup'] = 'cp -r $SCRATCH/* $SUBMITDIR'
	
    if os.path.exists(args['script_name']):
        message = 'Run script: {} exists, overwrite?'.format(args['script_name'])
        if query_yes_no(message):
            write_slurm_script(args)
        else:
	        print('Using existing job script: {0}, without changes'.format(args['script_name']))
    else:
        print('Creating job script: {0}'.format(args['script_name']))
        write_slurm_script(args)

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

def header(args, skipped):

    out = "{0:^16s} {1:^12s} {2:^20s}".format("Date", "Job ID", "Submit dir")
    out += "".join(["{0:>15s}".format(k) for k in sorted(args.keys()) if not k in skipped])
    return out

if __name__ == "__main__":
    main(None)

