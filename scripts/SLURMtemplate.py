#!/bin/bash
# Job name:
#SBATCH --job-name=$jobname
# Project:
#SBATCH --account=$projectno
# Wall clock limit:
#SBATCH --time=$time #in hh:mm:ss format
# Max memory usage:
#SBATCH --mem-per-cpu=3700M
# Core assignment
#SBATCH $cpupars
# Mail user if job fails
#SBATCH --mail-type=FAIL

## Set up job environment
source /usit/abel/u1/brogaard/.bash_profile
source /cluster/bin/jobsetup
module load $modules

# Automatic copying of files and directories back to $SUBMITDIR
chkfile "$chkfiles"
cleanup "$cleanupcommand"

## Do some work (including copying input files to scratch dir)
$commands
## Update list of succesfully completed jobs
echo `date +%F_%R`    $JOB_ID $SUBMITDIR >> $HOME/completed_jobs.dat
