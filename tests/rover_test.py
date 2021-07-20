import numpy as np

import sys
sys.path.append("..")

from network import Network, Reality
from rover import Rover

def test():
    rand = np.random.rand(800, 600)

    net = Network(rand.shape)
    net.start()

    reality = Reality(rand)
    reality.start()

    rover = Rover(0)
    print("PROSPECTED ", rover.prospect(0,0))


if __name__ == "__main__":
    test()




