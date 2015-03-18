
''' ASE-Tools package with helpful scripts'''

from setuptools import setup

setup(
    author = "Lukasz Mentel",
    author_email = "lmmentel@gmail.com",
    packages = ['asetools'],
    include_package_data = True,
    scripts = [
        'scripts/analyze',
        'scripts/ase-build-py26',
        'scripts/ase-db-py26',
        'scripts/ase-gui-py26',
        'scripts/ase-info-py26',
        'scripts/ase-run-py26',
        'scripts/checkpointNEB',
        'scripts/checkpointQE',
        'scripts/cubecutperiodic',
        'scripts/dirpid',
        'scripts/displayDOS',
        'scripts/displayDOS_gpaw',
        'scripts/dynmatsimple',
        'scripts/espresso.pyc',
        'scripts/espresso_old.py',
        'scripts/esub-gen',
        'scripts/esub-suncat',
        'scripts/genCHG',
        'scripts/genopt_nohydrocarbon_gpaw',
        'scripts/genopt_zeoliteonly',
        'scripts/genopt_zeoliteonly_gpaw',
        'scripts/getAtomindices',
        'scripts/getCell',
        'scripts/getDPE',
        'scripts/getEpot',
        'scripts/getStructDiff',
        'scripts/getads',
        'scripts/getads_screen',
        'scripts/getadsgrid',
        'scripts/getmagmom',
        'scripts/getmaxforce',
        'scripts/gkill',
        'scripts/gsub-gen',
        'scripts/gsub-lcls',
        'scripts/gsub-oak',
        'scripts/gsub-pinto',
        'scripts/gsub-suncat',
        'scripts/insertadsZSM22',
        'scripts/insertadsZSM22poremouth',
        'scripts/interpolate',
        'scripts/jmol_template',
        'scripts/jobDir',
        'scripts/jobInfo',
        'scripts/makejmolscript',
        'scripts/massCommand',
        'scripts/mkm-bsub',
        'scripts/mysbatch',
        'scripts/parseErr',
        'scripts/piddir',
        'scripts/preparefreq_hydrocarbon',
        'scripts/preparefreq_hydrocarbon_gpaw',
        'scripts/printIRspec',
        'scripts/printNEBxyzs',
        'scripts/printPics',
        'scripts/printZSM22',
        'scripts/printZSM22jmol',
        'scripts/printbcharges',
        'scripts/pwlog2traj',
        'scripts/pwlog2trajectory',
        'scripts/rerunBEEF',
        'scripts/rerunBEEF_molecule',
        'scripts/rerunBEEF_neb',
        'scripts/rerunBEEF_newunit',
        'scripts/rerunBEEF_single',
        'scripts/rerunQE_single',
        'scripts/rerunQEopt',
        'scripts/rerunQEopt_ZSM22',
        'scripts/rerunQEopt_ZSM5',
        'scripts/rerunQEopt_mol',
        'scripts/restartNEB',
        'scripts/restartcalc',
        'scripts/resub',
        'scripts/resuball',
        'scripts/runBEEFopt',
        'scripts/runDOS',
        'scripts/runDOS_gpaw',
        'scripts/runDPE_QE',
        'scripts/runDPE_gpaw',
        'scripts/runNCIplot',
        'scripts/runPBED',
        'scripts/runPBED_2',
        'scripts/runQE',
        'scripts/runQE_DFTd_single',
        'scripts/runRPBE',
        'scripts/runRPBE_gpaw',
        'scripts/runRPBE_gpaw.bak',
        'scripts/runRPBEoptzeolite',
        'scripts/run_frequencies',
        'scripts/run_gencube',
        'scripts/run_molecule',
        'scripts/running',
        'scripts/sub_runRPBE',
        'scripts/sub_zeoliteonly',
        'scripts/submitQE',
        'scripts/usage',
        'scripts/writecif',
        'scripts/writeqespec',
    ],
    description = "convenience scripts for ASE",
    install_requires = [
        #"ase",
        "numpy",
    ],
    license = open("LICENSE.txt", "r").read(),
    long_description = open("README.md", "r").read(),
    name = "asetools",
    url = "www.bitbucket.org/lukaszmentel/asetools",
    version = "0.1.0",
)
