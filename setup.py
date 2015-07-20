
''' ASE-Tools package with helpful scripts'''

from setuptools import setup

setup(
    author = "Lukasz Mentel",
    author_email = "lmmentel@gmail.com",
    packages = ['asetools'],
    include_package_data = True,
    scripts = [
        'scripts/checkpointNEB',
        'scripts/checkpointQE',
        'scripts/cubecutperiodic',
        'scripts/displayDOS',
        'scripts/displayDOS_gpaw',
        'scripts/dynmatsimple',
        'scripts/genCHG',
        'scripts/genopt_zeoliteonly',
        'scripts/getAtomindices',
        'scripts/getCell',
        'scripts/getDPE',
        'scripts/getEpot',
        'scripts/getStructDiff',
        'scripts/getads',
        'scripts/getads_screen',
        'scripts/getadsgrid',
        'scripts/getmaxforce',
        'scripts/gkill',
        'scripts/insertadsZSM22',
        'scripts/insertadsZSM22poremouth',
        'scripts/interpolate',
        'scripts/makejmolscript',
        'scripts/massCommand',
        'scripts/parseErr',
        'scripts/piddir',
        'scripts/preparefreq_hydrocarbon',
        'scripts/printIRspec',
        'scripts/printNEBxyzs',
        'scripts/printPics',
        'scripts/printZSM22jmol',
        'scripts/printbcharges',
        'scripts/pwlog2traj',
        'scripts/pwlog2trajectory',
        'scripts/rerunBEEF',
        'scripts/rerunBEEF_neb',
        'scripts/rerunBEEF_newunit',
        'scripts/rerunBEEF_single',
        'scripts/restartNEB',
        'scripts/restartcalc',
        'scripts/runBEEFopt',
        'scripts/runDOS',
        'scripts/runDOS_gpaw',
        'scripts/runDPE_QE',
        'scripts/runNCIplot',
        'scripts/runQE',
        'scripts/run_frequencies',
        'scripts/run_gencube',
        'scripts/running',
        'scripts/sub_runRPBE',
        'scripts/sub_zeoliteonly',
        'scripts/submitQE',
        'scripts/translate_cell',
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
    version = "0.1.1",
)
