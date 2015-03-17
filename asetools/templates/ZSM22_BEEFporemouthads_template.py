#Template input for a BEEF structure optimization on a poremouth (or other 2D pbc structure
from ase.io import write,read,PickleTrajectory
from ase.optimize import BFGS,FIRE
import numpy as np
from gpaw import GPAW,FermiDirac,Mixer

atoms = read('$readpath') #NB it is the users responsibility to provide a locked structure, such that the slab does not move during optimization.
atoms.set_pbc((1, 1, 0)) #only pbc in x and y direction

calc = GPAW(xc='BEEF-vdW',h=0.2,kpts=(1, 1, 1),txt='gpaw.txt')
atoms.set_calculator(calc)

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=0.03)
