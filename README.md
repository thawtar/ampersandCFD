# ampersandCFD
A streamlined OpenFOAM generation tool 

![alt text](https://github.com/thawtar/ampersandCFD/blob/main/images/ampersand_ss.jpg)

### Overview
Ampersand is designed to provide users a simple and streamlined workflow for generating their OpenFOAM case files.

You can use Ampersand for external and internal incompressible flows. The case file generation procedure is very simple. You need to locate your STL file and answer a few YES/NO and multiple choice questions. Ampersand will take care of the rest including mesh size and y+, boundary conditions and numerical schemes.

### Installation
1. **Requirements**: OpenFOAM, Python 3.x, additional dependencies (list here).
2. **Installation**: Clone the repository and install dependencies.

```bash
   git clone https://github.com/thawtar/ampersandCFD.git
   cd ampersandCFD
   pip install -r requirements.txt
```

3. **Setup**: Configure paths as needed, then verify with a test case.


### Quick Start
1. **Case generation**: Go inside ampersandCFD/src directory and run:
```bash
   python main.py --create
```

2. **Modifying generated case**: Go inside ampersandCFD/src directory and run:
```bash
   python main.py --open
```

### Features
1. **Streamlined workflow for external and internal flows**
An easy to follow series of prompts and questions to create your OpenFOAM casefiles and meshes. You can choose whether external aerodynamics or internal flows inside various machinery and Ampersand will help you generate a suitable case directory for you.

2. **Boundary conditions and simulation settings**
Easily configure boundaries, geometry and physics. Stable and accurate discretization schemes and linear solvers are chosen for your simulations!

### User Guide
The user guide and related documentations are under construction. We will provide more detailed guides later.

### Contributing 
Contributions are welcome! Please see our contribution guide for details.

### Support
For questions or support, contact Thaw Tar (mr.thaw.tar1990@gmail.com) or open an issue.


### Demonstration 
You can see the demonstration of this code in this following YouTube video:
https://www.youtube.com/watch?v=KoiBxDwSiP0&t=248s


## Gallery 
The OpenFOAM case files for the following meshes and CFD simulations are created using Ampersand.

![alt text](https://github.com/thawtar/ampersandCFD/blob/main/images/drivAer_steady_state_defects.png)

Multi-region mesh of a tank (Internal flow problem)

![alt text]
DrivAer simulation (External flow)

![alt text](https://github.com/thawtar/ampersandCFD/blob/main/images/1729773467507.jpg)
Formula One car (External flow)


