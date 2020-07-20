from setuptools import setup, find_packages
setup(
    name = "LabTools3",
    version = "0.2.8",
    packages = find_packages(),
    # add additional files
    package_data = {'':['*.bat','*.command']},
    # meta data about package
    # metadata for upload to PyPI
    author = "Werner Boeglin",
    author_email = "boeglinw@fiu.edu",
    description = "Python 3 Package of modules for typical analysis tasks analyzing physics data",
    license = "GPL",
    keywords = "Data Analysis",
    url = "http://wanda.fiu.edu/boeglinw/LabTools3",   # project home page, if any    
)
