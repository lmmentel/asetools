#Template input for calculation of an adsorption energy
from ase.io import write,read
from gpaw import GPAW,PW
import numpy as np
from sys import path

substrate = read('$spath')
molecule = read('$mpath')
ads = read('$apath')

scalc = GPAW(nbands=560,mode=PW($pw),xc='$xc',kpts=$kpts,txt='substrate_%s.txt' % $pw)
mcalc = GPAW(nbands=560,mode=PW($pw),xc='$xc',kpts=$kpts,txt='molecule_%s.txt' % $pw)
acalc = GPAW(nbands=560,mode=PW($pw),xc='$xc',kpts=$kpts,txt='ads_%s.txt' % $pw)

#Generate cell with 5 AA distance to the wall in every direction
molecule.center(vacuum=5.0)

e = []

for atoms,calc in zip([substrate,ads,molecule],[scalc,acalc,mcalc]):
	atoms.set_calculator(calc)
	e.append(atoms.get_potential_energy())

print 'Adsorption energy (pw=$pw):', np.round(e[2]-e[1]-e[0],4)
