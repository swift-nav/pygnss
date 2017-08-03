from setuptools import setup, find_packages

setup(
    name="snavutils",
    version="0.1.0",
    install_requires=['numpy'],
    extras_require={
        'test': ['pytest'],
    },
    packages=find_packages()
)
