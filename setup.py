import setuptools

setuptools.setup(
    name='Pedal',
    version='0.1.61',
    author='acbart,lukesg08',
    author_email='acbart9@gmail.com',
    description='Tools for analyzing student code.',
    packages=['pedal', 'pedal.report', 'pedal.plugins', 'pedal.resolvers',
              'pedal.source', 'pedal.tifa', 'pedal.questions',
              'pedal.cait', 'pedal.mistakes', 'pedal.toolkit',
              'pedal.assertions', 'pedal.sandbox', 'cs1014'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.rst').read(),
    url='https://github.com/pedal-edu/pedal/',
    classifiers=(
        "Programming Language :: Python :: 3",

    )
)
