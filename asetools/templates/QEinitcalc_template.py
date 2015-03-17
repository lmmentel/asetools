#Template input for a single point energy calculation with Quantum Espresso
from ase.io import write,read
from espresso import espresso
from mypython import set_init_magmoms

calc = espresso(pw=$pw,dw=$dw,
                xc='$xc',
                kpts = $kpts,
		vdw_corr = $vdw,
                sigma = $sigma, #Fermi smearing
                convergence={'energy':1e-6}, #default
		onlycreatepwinp = 'pw.inp',
		spinpol=$spinpol,
		mode='$mode',
		fmax=$fmax
                )

atoms = read('$readpath')
set_init_magmoms(atoms,[$idxs])
$extralines
calc.initialize(atoms)
