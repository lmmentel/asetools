import numpy as np
from ase.io import read
from ase.vibrations import Vibrations
from espresso.vibespresso import vibespresso
import os,pickle
from ase.parallel import rank

atoms = read('$readpath')
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
