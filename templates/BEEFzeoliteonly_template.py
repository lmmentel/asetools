#Template input for reoptimizing a silicious structure without a hydrocarbon adsorbate
from ase.io import write,read,PickleTrajectory
from ase.optimize import BFGS,FIRE
import numpy as np
from gpaw import GPAW,FermiDirac,Mixer
from mypython import get_selected_atom_indices

atoms = read('$readpath')

#Delete the hydrocarbon molecule
indices = get_selected_atom_indices(atoms,['C','H'])
for i in indices:
  del atoms[i]

write('startguess.traj',atoms)

calc = GPAW(xc='BEEF-vdW',h=0.2,kpts=(1, 1, 1),txt='gpaw.txt')
atoms.set_calculator(calc)

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=0.03)
