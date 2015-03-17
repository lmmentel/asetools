#Template input for runnning a BEEF calculation
from ase.io import write,read,PickleTrajectory
from ase.optimize import BFGS,FIRE
import numpy as np
from gpaw import GPAW,FermiDirac,Mixer

atoms = read('$readpath')

calc = GPAW(xc='BEEF-vdW',h=0.2,kpts=(1, 1, 1),txt='gpaw.txt')
atoms.set_calculator(calc)

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=0.03)
