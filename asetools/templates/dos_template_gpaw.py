#!/usr/local/bin/python2.7
import numpy as np
from gpaw import GPAW
from gpaw.poisson import PoissonSolver
from gpaw.dipole_correction import DipoleCorrection
from ase.io import read
import pickle,os

if not os.path.isfile('gpaw.gpw'):
   atoms = read('$readpath')
   calc = atoms.get_calculator()
   atoms.set_calculator(calc)
   atoms.get_potential_energy()
   calc.write('gpaw.gpw','all')
else:
   calc = GPAW('gpaw.gpw')

atomlist = $atomno_list #list of atom numbers to print dos for
angulars = $angular_list #list of angular momenta in {s,p,d,f}

for atom in atomlist:
   for angular in angulars:
     if not os.path.isfile('pdos%s_%s.pkl' % (atom,angular)):
   	energy, pdos = calc.get_orbital_ldos(a=atom, angular=angular,npts=2001)
   	f = open('energy%s_%s.pkl' % (atom,angular),'w')
   	pickle.dump(energy,f)
   	f.close()
   	f = open('pdos%s_%s.pkl' % (atom,angular),'w')
   	pickle.dump(pdos,f)
   	f.close() 
