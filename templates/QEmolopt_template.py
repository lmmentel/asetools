#!/usr/local/bin/python2.7
#Template input for a structure relaxation with Quantum Espresso
from ase.io import read
from ase.optimize import BFGS
from espresso import espresso
from mypython import set_init_magmoms

calc = espresso(pw=$pw,dw=$dw,
                xc='$xc',
                kpts = '$kpts',
                sigma = $sigma, #Fermi smearing
                convergence={'energy':1e-6}, #default
                spinpol=$spinpol,
                )

atoms = read('$readpath')
set_init_magmoms(atoms,[$idxs])
atoms.set_calculator(calc)
smart_cell(atoms,vac=$vac,h=0.01) #create cell with equal vacuum spacing of vac Aa in all directions. NB! grid spacing parameter h only matters for a real-space code!


qn = BFGS(atoms, logfile='qn.log',trajectory='dyn.traj')
qn.run(fmax=$fmax)

