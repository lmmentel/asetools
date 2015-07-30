#!/bin/env python
import numpy as np
from ase.io import read
from ase.vibrations import Vibrations
from espresso.vibespresso import vibespresso
from ase.thermochemistry import HarmonicThermo,rotationalinertia
import os,pickle
from ase.parallel import rank
from ase import units,Atoms
from asetools import cm1_to_eV,set_init_magmoms

atoms = read('$input')

elecenergy = atoms.get_potential_energy()
set_init_magmoms(atoms,[$magmoms])

indices = $indices
if indices == []: #default: include all atoms in calculation
   indices = range(atoms.get_number_of_atoms())

# Create vibration calculator
calc = vibespresso(pw=$pw,dw=$dw,
                xc='$xc',
                kpts = $kpts,
		london=$grimme, #DFT-D2 dispersion correction
                sigma = $sigma, #Fermi smearing
                convergence={'energy':1e-10},
                spinpol=$spinpol,
                mode='scf', #single-point energy calculation per displacement
                )

atoms.set_calculator(calc)
vib = Vibrations(atoms,indices=indices,delta=$delta,nfree=$nfree)
vib.run()

if rank == 0:
   vib.summary(method='$method')
   vibenergies = vib.get_energies()
   with open('vibenergies.pckl','w') as file:
      pickle.dump(vibenergies,file)
# Make trajectory files to visualize normal modes:
   for mode in range(len(indices)*3):
        vib.write_mode(mode)
#Save a HarmonicThermo object
   #vibenergies[0] = 12*cm1_to_eV
   thermo = HarmonicThermo(vibenergies,elecenergy)
   if len(indices) > 0:
	thermofname = 'HarmonicThermo_partial.pckl'
   else:
	thermofname = 'HarmonicThermo.pckl'
   with open(thermofname,'w') as file:
       pickle.dump(thermo,file)
