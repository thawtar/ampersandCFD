# ampersandCFD
A streamlined OpenFOAM generation tool 

![alt text](https://github.com/thawtar/ampersandCFD/blob/dev/ampersandCFD/images/ampersand_ss.jpg)

### Overview
Ampersand is designed to provide users a simple and streamlined workflow for generating their OpenFOAM case files.

You can use Ampersand for external and internal incompressible flows. The case file generation procedure is very simple. You need to locate your STL file and answer a few YES/NO and multiple choice questions. Ampersand will take care of the rest including mesh size and y+, boundary conditions and numerical schemes.

### Installation
1. **Requirements**: OpenFOAM, Python 3.x, additional dependencies (list here).
2. **Installation**: Clone the repository and install dependencies.

```bash
   git clone <repo-url>
   cd Ampersand
   pip install -r requirements.txt
```

3. **Setup**: Configure paths as needed, then verify with a test case.


### Quick Start
1. **Case generation**: Go inside AmpersandCFD/src directory and run:
```bash
   python main.py --create
```

2. **Modifying generated case**: Go inside AmpersandCFD/src directory and run:
```bash
   python main.py --open
```


You can see the demonstration of this code in this following YouTube video:
https://www.youtube.com/watch?v=KoiBxDwSiP0&t=248s

#Some of the cases that are generated using Ampersand

![alt text](https://github.com/thawtar/ampersandCFD/blob/dev/ampersandCFD/images/ampersand_mixer_total.png)
Multi-region mesh of a tank (Internal flow problem)

![alt text](https://github.com/thawtar/ampersandCFD/blob/dev/ampersandCFD/images/drivAer_steady_state_defects.png)
DrivAer simulation (External flow)

![alt text](https://github.com/thawtar/ampersandCFD/blob/dev/ampersandCFD/images/1729773467507.jpg)
Formula One car (External flow)


