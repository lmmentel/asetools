
''' ASE-Tools package with helpful scripts'''

from setuptools import setup

setup(
    author = "Lukasz Mentel",
    author_email = "lmmentel@gmail.com",
    scripts = [
        'scripts/mkm-bsub',
        'scripts/ase-db-py26',
        'scripts/sub_qe.py',
        'scripts/gsub-oak',
        'scripts/esub-gen',
        'scripts/rerunBEEF',
        'scripts/esub-suncat',
        'scripts/ase-build-py26',
        'scripts/runRPBE_gpaw.bak',
        'scripts/printbcharges',
        'scripts/usage',
        'scripts/jobInfo',
        'scripts/insertadsZSM22poremouth',
        'scripts/dynmatsimple',
        'scripts/gsub-pinto',
        'scripts/espresso.pyc',
        'scripts/mysbatch',
        'scripts/rerunQEopt',
        'scripts/displayDOS',
        'scripts/rerunBEEF_single',
        'scripts/rerunQEopt_ZSM22',
        'scripts/printPics',
        'scripts/SLURMtemplate.py',
        'scripts/runRPBEoptzeolite',
        'scripts/preparefreq_hydrocarbon_gpaw',
        'scripts/runDPE_gpaw',
        'scripts/pwlog2traj',
        'scripts/printNEBxyzs',
        'scripts/runBEEFopt',
        'scripts/interpolate',
        'scripts/genopt_zeoliteonly',
        'scripts/analyze',
        'scripts/espresso_old.py',
        'scripts/getDPE',
        'scripts/printZSM22jmol',
        'scripts/getmagmom',
        'scripts/runDPE_QE',
        'scripts/getAtomindices',
        'scripts/genopt_nohydrocarbon_gpaw',
        'scripts/ase-gui-py26',
        'scripts/genopt_zeoliteonly_gpaw',
        'scripts/checkpointNEB',
        'scripts/running',
        'scripts/resub',
        'scripts/runPBED_2',
        'scripts/getmaxforce',
        'scripts/parseErr',
        'scripts/gkill',
        'scripts/printZSM22',
        'scripts/writecif',
        'scripts/printIRspec',
        'scripts/preparefreq_hydrocarbon',
        'scripts/rerunQEopt_mol',
        'scripts/getads_screen',
        'scripts/makejmolscript',
        'scripts/piddir',
        'scripts/displayDOS_gpaw',
        'scripts/pwlog2trajectory',
        'scripts/ase-run-py26',
        'scripts/jobDir',
        'scripts/getEpot',
        'scripts/runDOS_gpaw',
        'scripts/sub_runRPBE',
        'scripts/submitQE',
        'scripts/run_gencube',
        'scripts/gsub-suncat',
        'scripts/restartcalc',
        'scripts/writeqespec',
        'scripts/getadsgrid',
        'scripts/rerunQE_single',
        'scripts/resuball',
        'scripts/rerunBEEF_newunit',
        'scripts/massCommand',
        'scripts/runQE_DFTd_single',
        'scripts/runPBED',
        'scripts/run_molecule',
        'scripts/restartNEB',
        'scripts/getads',
        'scripts/insertadsZSM22',
        'scripts/rerunBEEF_molecule',
        'scripts/getStructDiff',
        'scripts/cubecutperiodic',
        'scripts/gsub-gen',
        'scripts/runQE',
        'scripts/gsub-lcls',
        'scripts/sub_zeoliteonly',
        'scripts/runDOS',
        'scripts/getCell',
        'scripts/rerunQEopt_ZSM5',
        'scripts/jmol_template',
        'scripts/runRPBE',
        'scripts/runNCIplot',
        'scripts/ase-info-py26',
        'scripts/genCHG',
        'scripts/rerunBEEF_neb',
        'scripts/dirpid',
        'scripts/runRPBE_gpaw',
        'scripts/checkpointQE',
        'scripts/run_frequencies',     
    ],
    description = "convenience scripts for ASE",
    install_requires = [
        "numpy",
    ],
    license = open("LICENSE.txt", "r").read(),
    long_description = open("README.md", "r").read(),
    name = "asetools",
    url = "",
    version = "0.1.0",
)
