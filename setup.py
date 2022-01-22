from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='api_gateway',
    version='0.1.0',
    license='None',
    author='Mohamad Ahmadi',
    author_email='mohammadahmadidezhnet@gmail.com',
    load_description=open('README.md').read(),
    packages=find_packages(exclude=['api_gateway/source/', 'tests*']),
    install_requires=required,
    zip_safe=False
)
