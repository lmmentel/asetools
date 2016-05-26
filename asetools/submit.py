
'''Utilities used to generate the submission script for batch systems'''

from __future__ import print_function, absolute_import


import os
import sys
import re
import subprocess
from argparse import ArgumentParser
from datetime import datetime

from .asetools import get_config

# keep backwards compatibility with python2
if sys.version[0] == "3":
    raw_input = input


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaning
    an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
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
            sys.stdout.write("Please respond with 'yes' or 'no' "
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
    parser.add_argument('-d', '--nosubmit',
                        action='store_true',
                        help='Create job script, but do not submit.')
    parser.add_argument("-e",
                        "--extrafiles",
                        nargs="+",
                        default=None,
                        help="additional files that need to be copied to the node/scratch")
    parser.add_argument('--program',
                        default='pythonqe',
                        help='Specify which program to run. pythonqe: prepares script for running '
                        'quantum espresso through the ase-espresso interface. nativeqe: '
                        'runs internal espresso routines. To be defined in $HOME/.asetools_site_config.py.'
                        'Default: pythonqe.')
    parser.add_argument('-m',
                        '--mem-per-cpu',
                        default='3700M',
                        help='Memory per cpu, default=3700M')
    parser.add_argument('-p', '--ppn',
                        type=int,
                        default=16,
                        help='Number of cores. Default=16 (one full node)')
    parser.add_argument('--account',
                        default='nn4683k',
                        help='Project account. Retrieve it with PROJECT command.')
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

    if args:  # arguments passed from other python code
        args = vars(parser.parse_args(args))
    else:     # run from command line
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

    submitters = {"pbs" : {'directives_writer':create_pbs_directives, 'executable':'qsub'},
                  "slurm" : {'directives_writer': create_slurm_directives, 'executable':'sbatch'}
                 }

    # get the site configuration from the $HOME/.asetools_site_config.py file
    # and merge it into the args dictionary

    site_config = get_config()
    args.update(site_config)

    submitter = submitters.get(args['batch'].lower(), None)
    if submitter is not None:
        write_and_submit_script(args, submitter)
    else:
        raise NotImplementedError("support for '{0:s}' is not implemented, supported batch "
            "systems are: {1:s}".format(args['batch'], ", ".join(submitters.keys())))


def write_and_submit_script(args,submitter):
    '''
    Writes and submits the job script and saves the job specs in $HOME/submitted_jobs.dat.

    Args:
        args: (dict)
            arguments specifying the job
        submitter: (dict)
            specifications of the batch submitter. For now should include
            'directives_writer': name of function to write the batch
            directives, and  'executable': the command responsible for
            submission.
    '''

    if os.path.exists(args['script_name']):
        message = 'Job script: {} exists, overwrite?'.format(args['script_name'])
        if query_yes_no(message):
            write_job_script(args,submitter['directives_writer'])
        else:
            print('Using existing job script: {0}, without changes'.format(args['script_name']))
    else:
        print('Creating job script: {0}'.format(args['script_name']))
        write_job_script(args,submitter['directives_writer'])

    # submit the job to the queue if requested
    if args['nosubmit']:
        print("NOT submitting {} to the queue\nbye...".format(args['script_name']))
    else:
        output = subprocess.check_output([submitter['executable'], args['script_name']])
        patt = re.compile(r"[a-zA-Z\.]*(\d+)[a-zA-Z\.]*")
        match = patt.search(output)
        if match:
            pid = str(match.group(1))
            with open(os.path.join(args['home'], "submitted_jobs.dat"), "a") as dat:
                dat.write('{0} {1:>12s} {2:>20s}\n'.format(
                    pid, os.getcwd(), str(datetime.now().strftime("%Y-%m-%d+%H:%M:%S"))))
        else:
            pid = None

        print("Submitted batch job {0}".format(pid))


def write_job_script(args, directives_writer):
    '''
    Writes the job script for the batch system.

    Args:
        args: (dict)
            arguments specifying the job.
        directives_writer: (function)
            function creating a string of directives for the batch system.
    '''

    if not args['program'] in args['jobspec']:
        sys.exit('Dont know the job specifications for program: {0}. Exiting...'.format(args['program']))
    else:
        jobspec = args['jobspec'][args['program']]
    	with open(args['script_name'], 'w') as script:
            script.write("#!/bin/bash\n")
            script.write(directives_writer(args) + '\n')
            if 'lib_paths' in args and args['lib_paths'] != "":
                script.write('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{0:<s}\n\n'.format(":".join(args['lib_paths'])))
            if 'modules' in jobspec:
                script.write(jobspec['modules'] + '\n')
            if args['vars']:
            	for name, value in args['vars']:
                    script.write("export {n}={v}\n".format(n=name, v=value))
            if 'precmd' in jobspec:
            	script.write('\n' + jobspec['precmd'].format(**args) + '\n')
            if args['scratch']:
            	wrkdir = os.path.join(args['scratch'], args['jobname'])
            	script.write("mkdir -p {}\n".format(wrkdir))
            	files = args['input']
            	if args['extrafiles']:
                   files += ' ' + ' '.join(args['extrafiles'])
            	script.write('cp -t {0} {1}\n'.format(wrkdir, files))
       	    	script.write('cd {0}\n'.format(wrkdir))
	    script.write("\n# Do the work\n")
            script.write(jobspec['cmd'].format(**args) + '\n')
            if 'postcmd' in jobspec:
            	script.write(jobspec['postcmd'])


def create_pbs_directives(args):
    '''
    Creates the PBS directives for a job script.

    Args:
        args: (dict)
            arguments specifying the job.

    Returns:
        directives: (str)
            the PBS directives that can be written to a job script.
    '''

    directives = '\n'.join(["#PBS -N {}".format(args['workdir'][-8:]),
                            "#PBS -A {0}".format(args['account']),
                            "#PBS -l walltime={}".format(args['walltime']),
                            "#PBS -l pmem={}\n".format(args['mem_per_cpu'])
                            ])

    if args['HOST'] != "":
        directives += "#PBS -l nodes={0}:ppn={1}\n".format(args['HOST'], args['ppn'])
    else:
        directives += "#PBS -l nodes={0}:ppn={1}\n".format(args['nodes'], args['ppn'])
    if args["queue"] != "default":
        directives += "#PBS -q {}\n".format(args["queue"])

    directives += "#PBS -j oe\n"

    return directives


def create_slurm_directives(args):
    '''
    Creates the SLURM directives for a job script.

    Args:
        args: (dict)
            arguments specifying the job.

    Returns:
        directives: (str)
            the SLURM directives that can be written to a job script.
    '''

    directives = '\n'.join(["#SBATCH --job-name={}".format(args['workdir'][-8:]),
                            "#SBATCH --account={}".format(args['account']),
                            "#SBATCH --time={}".format(args["walltime"]),
                            "#SBATCH --mem-per-cpu={}".format(args['mem_per_cpu']),
                            "#SBATCH --nodes={0} --ntasks-per-node={1}".format(args['nodes'], args['ppn']),
                            "#SBATCH --mail-type=FAIL\n"
                            ])

    return directives

if __name__ == "__main__":
    main(None)
