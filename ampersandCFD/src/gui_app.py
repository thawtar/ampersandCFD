# this is the starting point of the application
from ampersandCFD.src.gui_core import ampersand

def main(server=None, **kwargs):
    app = ampersand(server)
    app.server.start(**kwargs)

if __name__ == "__main__":
    main()