from setuptools import setup
import jasinja, sys

requires = ['Jinja2']
if sys.version_info < (2, 6):
    requirements += ['simplejson']

setup(
    name='jasinja',
    version=jasinja.__version__,
    url='http://bitbucket.org/djc/jasinja',
    license='BSD',
    author='Dirkjan Ochtman',
    author_email='dirkjan@ochtman.nl',
    description='A JavaScript code generator for Jinja templates',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['jasinja', 'jasinja.tests'],
    package_data={
        'jasinja': ['*.js']
    },
    install_requires=requires,
    test_suite='jasinja.tests.run.suite',
    entry_points={
    	'console_scripts': ['jasinja-compile = jasinja.compile:main'],
    },
)
