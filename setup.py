from setuptools import setup, find_packages

setup(
    name="swiftnav-gnss",
    description="GNSS Utilities",
    author="Swift Navigation",
    author_email="dev@swiftnav.com",
    url="https://github.com/swift-nav/pygnss",
    packages=find_packages(),
    package_data={
        "gnss": ["py.typed"],
    },
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["numpy>=1.21", "pandas>=1.0"],
    extras_require={
        "test": [
            "pytest",
            "hypothesis",
            "mypy",
            "pandas-stubs",
            "black",
        ],
    },
    license="mit",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
