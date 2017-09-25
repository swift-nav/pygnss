from setuptools import setup, find_packages

setup(
    name="gnss",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=['numpy'],
    extras_require={
        'test': [
            'pytest',
            'hypothesis',
        ],
    },
    packages=find_packages()
)
