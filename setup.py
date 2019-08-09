from setuptools import setup

setup(name='x_flu',
      version='0.1',
      description='X-ray fluorescence map visualizer',
      url='https://github.com/ldorofeeva/x_flu.git,
      author='Elisa',
      author_email='dorofeeva.l@gmail.com',
      license='MIT',
      packages=['x_flu'],
      install_requires=[
        'numpy',
        'h5py',
        'matplotlib',
        'tkinter'
    ])
