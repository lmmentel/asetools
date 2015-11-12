#!/usr/local/bin/python2.7
#Template input for a structure relaxation with Quantum Espresso
from ase.io import read
from ase.optimize import BFGS
from espresso import espresso
from asetools import set_init_magmoms,smart_cell

calc = espresso(pw=$pw,dw=$dw,
                xc='$xc',
		london=$grimme, #DFT-D2 dispersion correction
                kpts = $kpts,
                sigma = $sigma, #Fermi smearing	
		isolated='$screening', #assuming the system to be isolated (a molecule or a cluster in a 3D supercell)
                convergence={'energy':1e-6}, #default
                spinpol=$spinpol,
		charge=$charge,
                )

atoms = read('$input')
set_init_magmoms(atoms,[$magmoms])
atoms.set_calculator(calc)
$extralines

qn = BFGS(atoms, logfile='qn.log',trajectory='$output')
qn.run(fmax=$fmax,steps=$steps)
