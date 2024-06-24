from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in lawyer/__init__.py
from lawyer import __version__ as version

setup(
	name="lawyer",
	version=version,
	description="Lawyer app",
	author="Alaa",
	author_email="Alaah1420@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
