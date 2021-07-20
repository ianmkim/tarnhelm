import unittest

import rover
from network import Network, Reality

from utils import byte_utils
from utils import utils
from utils import func_utils

import pika
import numpy as np
import constants

import time

def alert(str):
    print("[!]", str)

class TestRover(unittest.TestCase):
    def test_instantiation(self):
        alert("Testing Initiation")
        rov = rover.Rover(10)
        del rov

    def test_prospecting(self):
        alert("Testing Prospection")
        rov = rover.Rover(1, x=0, y=0)
        rand = np.random.rand(800, 600)

        reality = Reality(rand)
        reality.start()

        time.sleep(0.2)
        self.assertEqual(rand[0][0], rov.prospect())
        reality.stop()

        del reality
        del rov

    def test_reporting(self):
        alert("Testing Reporting Prospection Results")
        rov = rover.Rover(1, x=0, y=0)
        rand = np.random.rand(800, 600)

        reality = Reality(rand)
        reality.start()

        net = Network(rand.shape)
        net.start()

        time.sleep(0.2)
        amount = rov.prospect()
        self.assertEqual(rand[0][0], amount)
        self.assertNotEqual(net.resource_map[0][0], rand[0][0])
        rov.report(amount)
        self.assertEqual(net.resource_map[0][0], rand[0][0])

        reality.stop()
        net.stop()
        del reality
        del net

    def test_mining(self):
        alert("Testing Mining")

        rand = np.random.rand(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        rand[0][0] = 1.0

        reality = Reality(rand)
        reality.start()

        net = Network(rand.shape)
        net.start()
        time.sleep(0.2)

        rov =rover.Rover(1, x=0, y=0)

        prev_inventory = rov.inventory
        rov.mine()

        self.assertAlmostEqual(prev_inventory +rov.mine_rate, rov.inventory)

        reality.stop()
        net.stop()
        del reality
        del net

    def test_communication(self):
        alert("Testing Rover x Rover Comms")

class TestNetwork(unittest.TestCase):
    def test_instantiation(self):
        alert("Testing Network instantiation")
        n = Network(100, 100)
        n.start()
        n.stop()
        del n

    def test_communication(self):
        alert("Testing Network Communicatio")
        n = Network(100,100)
        n.start()

        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange=constants.ADD_RESOURCE_DISCOVERED, exchange_type='fanout')

        inp = np.array([0, 0, 100])
        message = byte_utils.encode_1d(inp)
        channel.basic_publish(exchange=constants.ADD_RESOURCE_DISCOVERED, routing_key='', body=message)
        connection.close()

        n.stop()
        del n

if __name__ == "__main__":
    unittest.main()

