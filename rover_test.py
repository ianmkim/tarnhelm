import numpy as np

from network import Network, Reality
from rover import Rover

rand = np.random.rand(800, 600)

net = Network(rand.shape)
net.start()

reality = Reality(rand)
reality.start()

rover = Rover(0)
print("PROSPECTED ",rover.prospect(0,0))





