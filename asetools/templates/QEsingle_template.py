#!/usr/local/bin/python2.7
#Template input for a structure relaxation with Quantum Espresso
from ase.io import read
from ase.optimize import BFGS
from espresso import espresso
from asetools import set_init_magmoms, smart_cell

calc = espresso(pw=$pw,dw=$dw,
                xc='$xc',
		vdw_corr=$vdw,
                kpts = '$kpts',
                sigma = $sigma, #Fermi smearing
                convergence={'energy':1e-6}, #default
                spinpol=$spinpol,
                )

atoms = read('$readpath')
set_init_magmoms(atoms,[$idxs])
atoms.set_calculator(calc)
$extralines

qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(steps=1)
