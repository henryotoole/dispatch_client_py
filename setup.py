# dispatch/dispatch_client_py/setup.py
# Josh Reed 2020


from setuptools import setup, find_packages
import os
import glob

# Changelog:
# 0.1.0
#	First system wide release of the python client
# 0.1.1
#	Change to reflect change in __polling__ method
# 0.1.2
#	Add permanent data to backend sends
# 0.2.0
#	Modernize setup.py

# Lessons from https://blog.ionelmc.ro/2014/05/25/python-packaging/

setup(
	# This is NOT the module name e.g. 'import dispatch_client_py'. This is the library name as
	# it would appear in pip etc.
	name='dispatch_client_py',
	version='0.2.0',
	license='GNUv3',
	description='A python-based client with methods used to communicate with a dispatch server instance over HTTP.',
	author='Josh Reed (henryotoole)',
	#author_email='email@the_root.tech',
	url='https://github.com/henryotoole/dispatch_client_py',
	packages=find_packages('src'),
	package_dir={'': 'src'},
	py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob.glob('src/*.py')],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"requests"
	],
	classifiers=[
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 3',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
	]
)