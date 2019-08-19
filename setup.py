from setuptools import setup

setup(name='x_flu',
      version='0.1',
      description='X-ray fluorescence map visualizer',
      url='https://github.com/ldorofeeva/x_flu.git',
      author='Elisa',
      author_email='dorofeeva.l@gmail.com',
      license='MIT',
      packages=['x_flu'],
      include_package_data=True,
      install_requires=[
        'numpy>=1.16',
		'scipy>=1.3',
        'h5py>=2.9',
        'matplotlib>=3',
        'tk'],
      long_description=open('README.md').read(),
      scripts=['bin/x_flu']
      )
