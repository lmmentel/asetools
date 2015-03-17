#Template input for calculation of an adsorption energy
from ase.io import write,read
from gpaw import GPAW,FermiDirac,PoissonSolver

substrate = read('$spath')
molecule = read('$mpath')
ads = read('$apath')

scalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='substrate_h%s.txt' % $h,nbands=-4,occupations=FermiDirac(0.0),stencils=(4,3),poissonsolver=PoissonSolver(nn=4,relax='GS'),maxiter=240)
mcalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='molecule_h%s.txt' % $h,nbands=-4,occupations=FermiDirac(0.0),stencils=(4,3),poissonsolver=PoissonSolver(nn=4,relax='GS'),maxiter=240)
acalc = GPAW(xc='$xc',h=$h,kpts=$kpts,txt='ads_h%s.txt' % $h,nbands=-4,occupations=FermiDirac(0.0),stencils=(4,3),poissonsolver=PoissonSolver(nn=4,relax='GS'),maxiter=240)

e = []

for atoms,calc in zip([substrate,molecule,ads],[scalc,mcalc,acalc]):
	atoms.set_calculator(calc)
	e.append(atoms.get_potential_energy())

print 'Adsorption energy (h=$h):',np.round(e[2]-e[1]-e[0],4),'eV'
