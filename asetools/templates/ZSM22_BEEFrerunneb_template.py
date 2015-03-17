#Template input for restarting previously run RPBE NEB calculations
from ase.neb import NEB
from ase.io import write,read,PickleTrajectory
import numpy as np
from ase.optimize import BFGS,FIRE
from ase.parallel import rank, size
from gpaw import GPAW,FermiDirac,Mixer

lc = $lc #optimized lattice constants from the unit cell
zrep = $zrep #repeating of cell in z direction (along big channel)

#create the primitive (super) cell from the unit cell parameters
cell = np.array([[lc[0]*0.5,lc[1]*0.5,0],[-lc[0]*0.5,lc[1]*0.5,0],[0,0,zrep*lc[2]]])

dir='/a/suncatfs1/u1/brogaard/zeolites/ZSM22/Primitive_1x1x2/'

initial = read(dir+'$initial'+'/dyn.traj')
write('initial.traj',initial)
final = read(dir+'$final'+'/dyn.traj')
write('final.traj',final)

nimage = $nimage
n = size // nimage # number of cpu's per image
j = 1 + rank // n  # my image number
assert nimage * n == size

images = [initial]

for i in range(nimage):

    ranks = np.arange(i * n, (i + 1) * n)
    image = read('../neb'+str(i+1)+'.traj')
    image.set_cell(cell,scale_atoms=True)

    if rank in ranks:
        calc = GPAW(xc='BEEF-vdW',h=0.2,
                    kpts=(1, 1, 1),
                    txt='neb%d.txt' % j,
                    communicator=ranks)
        image.set_calculator(calc)
    images.append(image)

images.append(final)

neb = NEB(images, parallel=True,k=0.3,climb=True)

qn = FIRE(neb, logfile='qn.log')

traj = PickleTrajectory('neb%d.traj' % j, 'w', images[j],
                        master=(rank % n == 0))

qn.attach(traj)
qn.run(fmax=0.05)

