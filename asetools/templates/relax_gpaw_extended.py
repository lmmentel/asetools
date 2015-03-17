#Template input for a structure relaxation, including a 
from ase.io import write,read
from gpaw import GPAW,Mixer
from ase.optimize import BFGS

atoms = read('$readpath')

calc = GPAW(maxiter=240,xc='$xc',h=$h,kpts=$kpts,txt='$txt')
atoms.set_calculator(calc)

#Extra lines to adjust parameters like initial magnetic moments
$extracalc

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=$fmax)
