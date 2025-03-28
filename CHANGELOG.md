# Change Log

## Version 2.0

### Settings Adjustments
* Added Pydantic types for settings
* Removed InletValues since it was mostly unused with exception of U which is the same as boundary_conditions.velocityInlet.u_value
* Merged patches and bcPatches

### Meshing
* Removed dead code and made `calc_mesh_settings` into composable functions
* Created `BoundingBox` and `Domain` classes to faciliatate redundant calculations
* Fixed `StlAnalysis.calc_nx_ny_nz` to return even amount, meant mod (%) instead of (//)

### Code Quality Improvements
* Use pathlib instead of os.path
* Split functionality instead services and utils
* Removed `AmpersandProject` self variables and made interface more functional
* Restructured project strcuture 
```
src/
├── cli/
├── generators/
├── gui/
├── models/
├── services/
├── thirdparty/
├── utils/
├── __init__.py
└── project.py
```
* Removed unused __main__ code and other unused functions
* Created input Pydantic model for Python API that CLI generates, rather than `AmpersandProject` setters
* Made `AmpersandIO` into `IOUtils` and made print go to logger. Outputs for non-GUI are silenced unless IOUtils.verbose = True, on by default for CLI

### Miscellaneous
* Rewrote dense complex functions
* Structured into Pip package