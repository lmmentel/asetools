#Template input for a structure relaxation
from ase.io import write,read
from gpaw import GPAW
from ase.optimize import BFGS

atoms = read('$readpath')

calc = GPAW(maxiter=240,xc='$xc',h=$h,kpts=$kpts,txt='$txt')
atoms.set_calculator(calc)

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=$fmax)
