from setuptools import setup, find_packages

setup(
    name='gnss',
    description='GNSS Utilities',
    author='Swift Navigation',
    author_email='dev@swiftnav.com',
    url='https://github.com/swift-nav/python-gnss',
    packages=find_packages(),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=['numpy'],
    extras_require={
        'test': [
            'pytest',
            'hypothesis',
        ],
    },
    license='mit',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
