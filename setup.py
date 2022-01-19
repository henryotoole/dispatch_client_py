# dispatch/dispatch_client_py/setup.py
# Josh Reed 2020
#
# This sets up the dispatch python client module system wide. To install it run
# >> python setup.py install
from glob import glob

import setuptools
from setuptools import setup
from setuptools import find_packages

# Changelog:
# 0.1.0
#	First system wide release of the python client
# 0.1.1
#	Change to reflect change in __polling__ method
# 0.1.2
#	Add permanent data to backend sends


# Kindly note:
# Given this setup.py, src is never ever mentioned by import or anything
# Import with 'import packagename'
# Cool right?
#
# ├─ src
# │  └─ packagename
# │     ├─ __init__.py
# │     └─ ...
# ├─ tests
# │  └─ ...
# └─ setup.py


# Master TODO for dispatch:
# USE THIS
# https://blog.ionelmc.ro/2014/05/25/python-packaging/

setup(
	# This is NOT the module name e.g. 'import dispatch_server'. This is the library name as
	# it would appear in pip etc.
	name='dispatch_client_py',
	version='0.1.2',
	license='GNUv3',
	description='A python-based client with methods used to communicate with a dispatch server instance over HTTP.',
	author='Josh Reed (henryotoole)',
	#author_email='email@the_root.tech',
	url='https://github.com/henryotoole/dispatch_client_py',
	packages=find_packages('src'),
	package_dir={'': 'src'},
	py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
	include_package_data=True,
	zip_safe=False,
	classifiers=[
		# TODO figure out these
		# complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
		#'Development Status :: 5 - Production/Stable',
		#'Intended Audience :: Developers',
		#'License :: OSI Approved :: BSD License',
		#'Operating System :: Unix',
		#'Operating System :: POSIX',
		#'Operating System :: Microsoft :: Windows',
		#'Programming Language :: Python',
		#'Programming Language :: Python :: 2.7',
		#'Programming Language :: Python :: 3',
		#'Programming Language :: Python :: 3.5',
		#'Programming Language :: Python :: 3.6',
		#'Programming Language :: Python :: 3.7',
		#'Programming Language :: Python :: 3.8',
		#'Programming Language :: Python :: 3.9',
		#'Programming Language :: Python :: Implementation :: CPython',
		#'Programming Language :: Python :: Implementation :: PyPy',
		# uncomment if you test on these interpreters:
		# 'Programming Language :: Python :: Implementation :: IronPython',
		# 'Programming Language :: Python :: Implementation :: Jython',
		# 'Programming Language :: Python :: Implementation :: Stackless',
		#'Topic :: Utilities',
	],
	keywords=[
		# eg: 'keyword1', 'keyword2', 'keyword3',
	],
	# We use python 3.6.3 lol
	python_requires='>=3.6.0',
	#TODO
	install_requires=[
		# eg: 'aspectlib==1.1.1', 'six>=1.7',
	],
	#TODO
	extras_require={
		# eg:
		#   'rst': ['docutils>=0.11'],
		#   ':python_version=="2.6"': ['argparse'],
	},
	#TODO
	setup_requires=[
		'pytest-runner',
	],
	entry_points={
		'console_scripts': [
			'nameless = nameless.cli:main',
		]
	},
)