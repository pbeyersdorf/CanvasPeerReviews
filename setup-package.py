from setuptools import setup, find_packages
setup(name='cpr',
      version='0.2',
      description='A plugin to mange peer review grading on canvas',
      url='https://www.sjsu.edu/faculty/beyersdorf/',
      author='Peter Beyersdorf',
      author_email='peter.beyersdorf@sjsu.edu',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      keywords=['python', 'canvas', 'peer reviews'],
      classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
      ]
      )