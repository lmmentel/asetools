#!/bin/env python
import numpy as np
from gpaw import GPAW, FermiDirac
from ase.optimize import BFGS
from ase.io import read
from ase.data.molecules import molecule
from os import system
from ase.infrared import InfraRed
from ase.thermochemistry import IdealGasThermo,rotationalinertia
import os,pickle
from ase.parallel import rank
from sys import argv

T = 298.15
p = 101325

atoms = read('$readpath')
elecenergy = atoms.get_potential_energy()
indices = $indices
if indices == []: #default: include all atoms in calculation
   indices = range(atoms.get_number_of_atoms())

# Create vibration calculator
atoms.set_calculator(GPAW(xc='$xc',h=$h,txt='gpaw.txt',convergence={'energy':1e-7}))
vib = InfraRed(atoms,indices=indices,delta=$delta,nfree=$nfree)
vib.run()

if rank == 0:
   vib.summary(method='$method')
   vibenergies = vib.get_energies()
   f = open('vibenergies.pckl','w')
   pickle.dump(vibenergies,f)
   f.close()
# Make trajectory files to visualize normal modes:
   for mode in range(len(indices)*3):
        vib.write_mode(mode)
# Write IR spectrum to file
   vib.write_spectra(start=500,end=4000)
# Do calculation of thermochemistry
   thermo = IdealGasThermo(vibenergies,'nonlinear',elecenergy,atoms,symmetrynumber=1,spin=0)
   print '\nPrinciple moments of inertia (amu*angstroms**2): %s\n' % rotationalinertia(atoms)
   thermo.get_free_energy(T,p)
