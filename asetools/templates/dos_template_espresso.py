#!/usr/bin/env python
import numpy as np
from ase.io import read
import pickle,os
from espresso import espresso
from mypython import set_init_magmoms

atoms = read('$readpath')

calc = $calculator
atoms.set_calculator(calc)
atoms.get_potential_energy()

dos = calc.calc_pdos(nscf=False,Emin=-8.0,Emax=8.0,ngauss=0,sigma=0.2,DeltaE=0.01,tetrahedra=False)
f = open('dos.pckl', 'w')
pickle.dump(dos, f)
f.close()

