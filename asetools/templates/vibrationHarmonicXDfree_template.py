#!/bin/env python
import numpy as np
from ase.io import read
from ase.vibrations import Vibrations
from espresso.vibespresso import vibespresso
from ase.thermochemistry import HarmonicThermo,rotationalinertia
import os,pickle
from ase.parallel import rank
from ase import units,Atoms
from mypython import cm1_to_eV,set_init_magmoms

atoms = read('$readpath')

elecenergy = atoms.get_potential_energy()
set_init_magmoms(atoms,[$idxs])

indices = $indices
if indices == []: #default: include all atoms in calculation
   indices = range(atoms.get_number_of_atoms())

# Create vibration calculator
calc = vibespresso(pw=$pw,dw=$dw,
                xc='$xc',
                kpts = $kpts,
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
   f = open('vibenergies.pckl','w')
   pickle.dump(vibenergies,f)
   f.close()
# Make trajectory files to visualize normal modes:
   for mode in range(len(indices)*3):
        vib.write_mode(mode)
#Save a HarmonicThermo object corresponding to an immobilized adsorbate
   #vibenergies[0] = 12*cm1_to_eV
   thermo_immo = HarmonicThermo(vibenergies,elecenergy)
   f = open('ImmoThermo.pckl','w')
   pickle.dump(thermo_immo,f)
   f.close()
#Save a HarmonicThermo object corresponding to a mobile adsorbate
# NB NB inspect vibrations manually, to select which harmonic frequencies to remove
   #vibenergies = np.delete(vibenergies,0,0)
   #thermo_xDfree = HarmonicThermo(vibenergies,elecenergy)
   #f = open('xDfreeThermo.pckl','w')
   #pickle.dump(thermo_xDfree,f)
   #f.close()
#Save moments of inertia, to be used when rotational entropy is considered. User should fill in the indices and choose which moments to save
   #complex = Atoms(atoms[X:Y])
   #inertias = rotationalinertia(complex)[0:]
   f = open('inertias.pckl','w')
   #pickle.dump(inertias,f)
   f.close()
#Save mass, for use in get_entropyXDfree
   #mass = sum(complex.get_masses())
   f = open('mass.pckl','w')
   #pickle.dump(mass,f)
   f.close()
