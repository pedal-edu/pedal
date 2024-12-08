import setuptools

setuptools.setup(
    name='pedal',
    version='2.7.0',
    python_requires='>=3.8',
    author='acbart,lukesg08',
    author_email='acbart@udel.edu',
    description='Tools to provide feedback on student code.',
    keywords='feedback education teaching program analysis tifa cait sandbox pedal grading grader grade',
    packages=['pedal', 'pedal.core', 'pedal.utilities', 'pedal.environments',
              'pedal.resolvers', 'pedal.command_line',
              'pedal.source', 'pedal.cait', 'pedal.tifa',
              'pedal.sandbox', 'pedal.sandbox.library', 'pedal.assertions',
              'pedal.questions', 'pedal.extensions', 'pedal.types', 'pedal.types.library'
              ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.rst').read(),
    install_requires=["tabulate"],
    entry_points={
          'console_scripts': [
              'pedal = pedal.command_line.command_line:main'
          ]
      },
    url='https://pedal-edu.github.io/pedal',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Education",
        "Topic :: Education",
    ]
)
