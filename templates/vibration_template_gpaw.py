#!/bin/env python
import numpy as np
from gpaw import GPAW, FermiDirac
from ase.io import read
from os import system
from ase.infrared import InfraRed
from gpaw import GPAW
import os,pickle
from ase.parallel import rank

atoms = read('$readpath')
indices = $indices
if indices == []: #default: include all atoms in calculation
   indices = range(atoms.get_number_of_atoms())

# Create vibration calculator
calc = GPAW(xc='$xc',h=$h,txt='gpaw.txt',kpts=$kpts)
$extracalcpar
atoms.set_calculator(calc)
vib = InfraRed(atoms,indices=indices,delta=$delta,nfree=$nfree)
vib.run()

if rank == 0:
   vib.summary(method='$method')
   vibenergies = vib.get_energies()
   f = open('vibenergies','w')
   pickle.dump(vibenergies,f)
   f.close()
# Make trajectory files to visualize normal modes:
   for mode in range(len(indices)*3):
        vib.write_mode(mode)
   vib.write_spectra(start=500,end=4000)
