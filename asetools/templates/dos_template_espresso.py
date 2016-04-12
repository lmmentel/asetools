#!/usr/bin/env python
from ase.io import read
import pickle
from espresso import Espresso
from asetools import set_init_magmoms

atoms = read('$readpath')

calc = $calculator
atoms.set_calculator(calc)
atoms.get_potential_energy()

dos = calc.calc_pdos(nscf=False,Emin=-8.0,Emax=8.0,ngauss=0,sigma=0.2,DeltaE=0.01,tetrahedra=False)
f = open('dos.pckl', 'w')
pickle.dump(dos, f)
f.close()

