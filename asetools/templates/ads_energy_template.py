#Template input for calculation of an adsorption energy
from ase.io import write,read
from gpaw import GPAW
import numpy as np
from sys import path
path.insert(0,'/nfs/slac/g/suncatfs/brogaard/bin/mypython')

substrate = read('$spath')
molecule = read('$mpath')
ads = read('$apath')

scalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='substrate_h%s.txt' % $h)
mcalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='molecule_h%s.txt' % $h)
acalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='ads_h%s.txt' % $h)

e = []

for atoms,calc in zip([substrate,ads,molecule],[scalc,acalc,mcalc]):
	atoms.set_calculator(calc)
	e.append(atoms.get_potential_energy())

print 'Adsorption energy (h=$h):', np.round(e[2]-e[1]-e[0],4)