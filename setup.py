import setuptools


setuptools.setup(
    name='Pedal',
    version='0.1.5dev',
    author='acbart,lukesg08',
    author_email='acbart9@gmail.com',
    description='Tools for analyzing student code.',
    packages= ['pedal', 'pedal.report', 'pedal.plugins', 'pedal.resolvers',
               'pedal.source', 'pedal.tifa', 
               'pedal.cait', 'pedal.mistakes', 'pedal.toolkit',
               'pedal.rerun', 'pedal.sandbox'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.rst').read(),
    url='https://github.com/acbart/pedal',
    classifiers=(
        "Programming Language :: Python :: 3",
        
    )
)