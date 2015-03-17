from ase.all import *
from gpaw import *

atoms = read('$input')

energy = atoms.get_potential_energy()
#atoms.get_calculator().write('$out.gpw',mode='all')
density = atoms.calc.get_all_electron_density() * Bohr**3
write('$out.cube',atoms,data=density)
