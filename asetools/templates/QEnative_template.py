#Template input for a single point energy calculation with Quantum Espresso
from ase.io import write,read
from espresso import espresso
from mypython import set_init_magmoms

calc = espresso(pw=$pw,dw=$dw,
                xc='$xc',
                kpts = $kpts,
		london = $grimme,
                sigma = $sigma, #Fermi smearing
		isolated='$screening', #assuming the system to be isolated (a molecule or a cluster in a 3D supercell)
                convergence={'energy':1e-6}, #default
		onlycreatepwinp = 'pw.inp',
		spinpol=$spinpol,
		mode='$nativemode',
		fmax=$fmax
                )

atoms = read('$input')
set_init_magmoms(atoms,[$magmoms])
$extralines
calc.initialize(atoms)
