import numpy as np
from ase.io import read
from espresso.vibespresso import vibespresso
from ase.vibrations import Vibrations
from ase.thermochemistry import IdealGasThermo,rotationalinertia
import os,pickle
from ase.parallel import rank
from mypython import set_init_magmoms

T = 298.15
p = 101325

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
# Do calculation of thermochemistry
   thermo = IdealGasThermo(vibenergies,'nonlinear',elecenergy,atoms,symmetrynumber=1,spin=0)
   print '\nPrinciple moments of inertia (amu*angstroms**2): %s\n' % rotationalinertia(atoms)
   thermo.get_free_energy(T,p)
