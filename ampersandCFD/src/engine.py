from logger import logger
# a lof of logic is implemented here

# this class will contain the mesh settings
EXTERNAL = 0
INTERNAL = 1
class Domain:
    def __init__(self):
        self.domain_type = None
        self. xLength = None
        self. yLength = None
        self. zLength = None
        self.nX = None
        self.nY = None
        self.nZ = None
        # cell size in each direction
        # this code will think from cell size perspective
        self.dx = None
        self.dy = None
        self.dz = None

    
    def set_domain_type(self, domain_type):
        self.domain_type = domain_type
    
    def set_domain_size(self, xLength, yLength, zLength):
        self.xLength = xLength
        self.yLength = yLength
        self.zLength = zLength

    def calc_domain_size(self, bounding_box):
        self.xLength = bounding_box[1][0] - bounding_box[0][0]
        self.yLength = bounding_box[1][1] - bounding_box[0][1]
        self.zLength = bounding_box[1][2] - bounding_box[0][2]
    


# this class will contain the methods to handle the logic and program flow
class Engine:
    def __init__(self, config):
        self.U = config["U"]

    # calculate nx, ny, nz from domain size and cell size
    def calc_nxnynz_with_directions(self, domain,cell_size)->tuple:
        nx = int(domain[0]/cell_size[0])
        ny = int(domain[1]/cell_size[1])
        nz = int(domain[2]/cell_size[2])
        return nx,ny,nz
        
    # calculate dx, dy, dz from domain size and target cell size
    def calc_nxnynz_refineLevels(self, domain,target_cell_size=0.1,refinementLevel=2)->tuple:
        cell_size = target_cell_size*(2**refinementLevel)
        dx = domain[0]/cell_size
        dy = domain[1]/cell_size
        dz = domain[2]/cell_size
        return dx,dy,dz
    
    
    