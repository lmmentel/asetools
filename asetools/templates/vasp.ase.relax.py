
from ase import Atoms, Atom
import ase.io
from ase.calculators.vasp import Vasp
from ase.optimize import BFGS

atoms = ase.io.read('%initial')

calc = Vasp(
        prec='Accurate',
        gga='PE',
        lreal=False,
        ediff=1.0e-8,
        encut=600.0,
        nelmin=5,
        nsw=0,
        nelm=100,
        ediffg=-0.001,
        ismear=0,
        ibrion=-1,
        nfree=2,
        isym=0,
        lvdw=True,
        lcharg=False,
        lwave=False,
        istart=0,
        npar=2,
        ialgo=48,
        lplane=True,
        ispin=1,
    )

atoms.set_calculator(calc)

opt = BFGS(atoms, logfile='optimizer.log', trajectory='%relaxed')
opt.run(fmax=0.01)

