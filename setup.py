from setuptools import setup, find_packages

setup(
    name='ampersandCFD',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # Add your project dependencies here
        # e.g., 'numpy', 'scipy', 'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            # Add command line scripts here
            # e.g., 'ampersandCFD=ampersandCFD.cli:main'
        ],
    },
)