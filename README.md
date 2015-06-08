# ASETools

ASETools is a set of convenience methods and scripts for running quantum chemicals
calcualtions with the [Atomistic Simualtion Environment](https://wiki.fysik.dtu.dk/ase/).

## Installation

Basis installation requires running

```bash
$ python setup.py install --user
```

or system wide installation, that is discouraged
```bash
$ python setup.py install
```

## Usage

### Command line scripts

After installation all the command line (CLI) scripts should be available on
your `PATH`. If you made a local installtion using the `--user` option make
sure that the user's local bin in on the `PATH`. On linux the local bin is
usually under `$HOME/.local/bin`.

### access template files

To see the available template files you can use the `list_templates` method:

```python
>>> from asetools import list_templates
>>> tlist = list_templates()
>>> sorted(tlist)
['BEEFzeoliteonly_template.py',
 'BEEFzeoliteonly_template.pyc',
 'GPAW_DPE_template.py',
 'QE_DPE_template.py',
 'QEinitcalc_template.py',
 'QEmolopt_template.py',
 'QEopt_template.py',
 'QEsingle_template.py',
 'ZSM22_BEEFporemouthads_template.py',
 'ZSM22_BEEFporemouthads_template.pyc',
 'ZSM22_BEEFrerunneb_template.py',
 'ZSM22_BEEFrerunsingle_template.py',
 'ZSM22_BEEFsingle_template.py',
 'ZSM22_BEEFsingle_template.pyc',
 'ZSM22_addmolecule_template.py',
 'ads_energy_Ge_template.py',
 'ads_energy_smartcell_pw_template.py',
 'ads_energy_smartcell_template.py',
 'ads_energy_template.py',
 'ads_energy_template2.py',
 'clusterScreenDPE_template.py',
 'clusterScreenDPE_template.pyc',
 'clusterScreenNH3ads_template.py',
 'clusterScreenNH3ads_template.pyc',
 'dos_template_espresso.py',
 'dos_template_gpaw.py',
 'gencube_template.py',
 'molecule_template.py',
 'ph_template.py',
 'pp_template.py',
 'preparefreq_hydrocarbon_template.py',
 'preparefreq_hydrocarbon_template.pyc',
 'relax_gpaw.py',
 'relax_gpaw_extended.py',
 'relax_gpaw_metalscreen.py',
 'single_energy_only.py',
 'single_energy_only2.py',
 'vac_conv_template.py',
 'vibrationHarmonicXDfree_template.py',
 'vibrationHarmonicXDfree_template_gpaw.py',
 'vibrationIdealGas_template.py',
 'vibrationIdealGas_template_gpaw.py',
 'vibration_template.py',
 'vibration_template_gpaw.py']
```

To get the contents fo the file there is the `get_template` method

```python
>>> from asetools import get_template
>>> contents = get_template('ads_energy_template.py')
>>> print contents

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
```
