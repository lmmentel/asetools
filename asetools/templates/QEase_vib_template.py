import numpy as np
from ase.io import read
from ase.vibrations import Vibrations
from espresso.vibespresso import Vibespresso
import os,pickle
from ase.parallel import rank
from asetools import set_init_magmoms

atoms = read('$input')

elecenergy = atoms.get_potential_energy()
set_init_magmoms(atoms,[$magmoms])

indices = $indices
if indices == []: #default: include all atoms in calculation
   indices = range(atoms.get_number_of_atoms())

# Create vibration calculator
calc = Vibespresso(pw=$pw,dw=$dw,
                xc='$xc',
                kpts = $kpts,
		london=$grimme, #DFT-D2 dispersion correction
                sigma = $sigma, #Fermi smearing
                convergence={'energy':1e-10},
                spinpol=$spinpol,
		calculation='scf',
                ion_dynamics='None',
		charge=$charge,
		isolated='$screening',
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
