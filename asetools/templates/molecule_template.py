#Template input for running molecule geometry optimization
from ase.io import read
from ase.optimize import BFGS
from gpaw import GPAW
from sys import path
path.insert(0,'/nfs/slac/g/suncatfs/brogaard/bin/mypython')
from mypython import smart_cell

atoms = read('$readpath')
atoms.set_pbc($pbc)
smart_cell(atoms,vac=$vac,h=$h) #create cell with equal vacuum spacing of vac Aa in all directions

calc = GPAW(xc='$xc',h=$h,kpts=(1, 1, 1),txt='gpaw.txt')
atoms.set_calculator(calc)

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=0.01)
