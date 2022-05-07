import os

from setuptools import setup

requirements_dir = os.getcwd() + "/requirements.txt"
with open(requirements_dir, "r") as f:
    file = f.readlines()
    requirements = [line.rstrip() for line in file]

setup(
    name='api_gateway',
    version='0.1.0',
    license='None',
    author='Aasood',
    author_email='meisam2236@gmail.com',
    load_description=open('README.md').read(),
    packages=["source"],
    install_requires=requirements,
    zip_safe=False
)
