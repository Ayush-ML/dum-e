# A Simple Script to View the URDF Mesh
import time
from dum_e.hal.sim_backend import SimBackend


try:
    backend = SimBackend(use_gui=True)
    backend.connect()

    while backend.is_connected():
        time.sleep(1)
except Exception:
    import traceback
    traceback.print_exc()
    input("Press Enter to close...") 
