#Template input for a single point energy calculation
from ase.io import write,read
from gpaw import GPAW

atoms = read('$readpath')

calc = GPAW(xc='$func',h=$h,kpts=$kpts,txt='$txt')
atoms.set_calculator(calc)

atoms.get_potential_energy()
write('$outfile',atoms)
