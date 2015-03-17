#Template input for restarting previously run RPBE single point calculations
from ase.io import write,read,PickleTrajectory
from ase.optimize import BFGS,FIRE
import numpy as np
from gpaw import GPAW,FermiDirac,Mixer

lc = $lc #optimized lattice constants from the unit cell
zrep = $zrep #repeating of cell in z direction (along big channel)

#create the primitive (super) cell from the unit cell parameters
cell = np.array([[lc[0]*0.5,lc[1]*0.5,0],[-lc[0]*0.5,lc[1]*0.5,0],[0,0,zrep*lc[2]]])

atoms = read('$readpath')
atoms.set_cell(cell,scale_atoms=True)

calc = GPAW(xc='BEEF-vdW',h=0.2,kpts=(1, 1, 1),txt='gpaw.txt')
atoms.set_calculator(calc)

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=0.03)
