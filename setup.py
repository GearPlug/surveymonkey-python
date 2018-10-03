import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='surveymonkey-python',
      version='0.1.0',
      description='Python wrapper for SurveyMonkey API',
      long_description=read('README.md'),
      url='https://github.com/GearPlug/surveymonkey-python',
      author='Nerio Rincon',
      author_email='nrincon.mr@gmail.com',
      license='GPL',
      packages=['surveymonkey'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)