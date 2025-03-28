from setuptools import setup, find_packages

# Function to read the requirements.txt file
def parse_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read the requirements from requirements.txt
requirements = parse_requirements('requirements.txt')

setup(
    name='ampersandCFD',
    version='2.0.0',
    description='Computational Fluid Dynamics Tools',
    author='Thaw Tar',
    author_email='mr.thaw.tar1990@gmail.com',
    license='GPL-3.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'ampersandcfd = ampersandCFD.cli.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)