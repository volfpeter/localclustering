from codecs import open
from os import path
from setuptools import setup, find_packages

# Get the long description from the README file
with open(path.join(path.abspath(path.dirname(__file__)), 'pypi_readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="localclustering",
    version="0.13.0",
    description="Python 3 implementation and documentation of the Hermina-Janos local "
                "graph clustering algorithm.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/volfpeter/localclustering",
    author="Peter Volf",
    author_email="do.volfp@gmail.com",
    license="AGPLv3+",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    keywords="graph network analysis cluster clustering ranking local hierarchical algorithm",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["graphscraper>=0.5"],
    python_requires=">=3.5"
)
