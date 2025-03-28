# AmpersandCFD
A user-friendly OpenFOAM case generation tool

![Ampersand Interface](https://github.com/thawtar/ampersandCFD/blob/main/images/ampersand_ss.jpg)

## Overview
Ampersand streamlines the OpenFOAM case file generation process through an intuitive interface. It handles both external and internal incompressible flows with minimal user input, automatically managing mesh parameters, boundary conditions, and numerical schemes.

## Installation

### Prerequisites
- OpenFOAM (ESI version)
- Python 3.x
- Git

### Quick Install
```bash
pip install git+https://github.com/thawtar/ampersandCFD#egg=ampersandCFD
```

### Development Setup
```bash
git clone https://github.com/thawtar/ampersandCFD.git
cd ampersandCFD
pip install -r requirements.txt
```

### Compatibility
- Supports OpenFOAM ESI versions (v2206, v2212, and newer)
- Should work with v1912, v2006 (untested)

## Usage

### Create New Case
```bash
cd ampersandCFD/src
ampersandcfd --create
```

### Modify Existing Case
```bash
cd ampersandCFD/src
ampersandcfd --open
```

## Key Features

### Automated Workflow
- Simple question-based interface
- Automatic mesh sizing and y+ calculation
- Optimized boundary conditions
- Pre-configured numerical schemes

### Supported Applications
- External aerodynamics
- Internal flow machinery
- Multi-region simulations

## Example Applications

### Internal Flow: Multi-region Tank Mesh
![Tank Mesh](https://github.com/thawtar/ampersandCFD/blob/main/images/ampersand_mixer_total.png)

### External Flow: DrivAer Simulation
![DrivAer](https://github.com/thawtar/ampersandCFD/blob/main/images/drivAer_steady_state_defects.png)

### External Flow: Formula One
![F1 Car](https://github.com/thawtar/ampersandCFD/blob/main/images/1729773467507.jpg)

## Resources
- [Video Tutorial](https://www.youtube.com/watch?v=KoiBxDwSiP0&t=248s)
- [Support Contact](mailto:mr.thaw.tar1990@gmail.com)
- [Submit Issues](https://github.com/thawtar/ampersandCFD/issues)

## Contributing
Contributions are welcome! Please check our contribution guidelines before submitting pull requests.
