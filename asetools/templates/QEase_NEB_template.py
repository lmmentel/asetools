from ase.neb import NEB
from ase.io import write,read,PickleTrajectory
import numpy as np
from ase.optimize import BFGS,FIRE
from ase.visualize import view
from asetools import set_init_magmoms
from espresso.multiespresso import multiespresso

nimage = $nimage

initial = read('$initial')
final = read('$final')
write('initial.traj',initial)
write('final.traj',final)

calcs = multiespresso(ncalc=nimage,outdirprefix='neb',pw=$pw,dw=$dw,
    xc=$xc,kpts=$kpts,spinpol=$spinpol)

images = [initial]
for i in range(nimage):
    image = read('NEB/neb%d.traj' % (i+1))
    set_init_magmoms(image,[$magmom])
    images.append(image)

images.append(final)

neb = NEB(images,k=$hook,climb=$climb)
calcs.set_neb(neb)

#view(images)
qn = BFGS(neb, logfile='qn.log')

for j in range(1,nimage+1):
  traj = PickleTrajectory('neb%d.traj' % j, 'w', images[j])
  qn.attach(traj)

qn.run(fmax=$fmax)
