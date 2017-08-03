from setuptools import setup, find_packages

setup(
    name="snavutils",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=['numpy'],
    extras_require={
        'test': ['pytest'],
    },
    packages=find_packages()
)
