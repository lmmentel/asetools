#Template input for calculation of an adsorption energy
from ase.io import write,read
from gpaw import GPAW
import numpy as np
from sys import path
path.insert(0,'/nfs/slac/g/suncatfs/brogaard/bin/asetools')
from asetools import smart_cell
from gpaw.poisson import PoissonSolver
from gpaw.dipole_correction import DipoleCorrection

substrate = read('$spath')
molecule = read('$mpath')
ads = read('$apath')

scalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='substrate_h%s.txt' % $h,poissonsolver=DipoleCorrection(PoissonSolver(), 2))
acalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='ads_h%s.txt' % $h,poissonsolver=DipoleCorrection(PoissonSolver(), 2))

e = [molecule.get_potential_energy()]

cell = ads.get_cell()
cell[2][2] = $zlength

for atoms,calc in zip([substrate,ads],[scalc,acalc]):
	atoms.set_cell(cell)
	atoms.set_calculator(calc)
	e.append(atoms.get_potential_energy())

print 'Adsorption energy (zlength=$zlength AA):', np.round(e[2]-e[1]-e[0],4)
