#
# Copyright (c) 2008 Daniel Truemper truemped@googlemail.com
#
# test_mgmt.py 10-Jan-2011
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# under the License.
#
#

import unittest

import time

import zmq
from zmq.eventloop.ioloop import IOLoop

from spyder.core.mgmt import ZmqMgmt
from spyder.core.constants import *


class ManagementTest(unittest.TestCase):


    def callMe(self, msg):
        self.assertEqual( [ self._topic, 'test' ], msg )
        self._master_pub.send_multipart(ZMQ_SPYDER_MGMT_WORKER_QUIT)


    def onEnd(self, msg):
        self.assertEqual(ZMQ_SPYDER_MGMT_WORKER_QUIT, msg)
        self._ioloop.stop()


    def test_simple_mgmg_session(self):
        
        context = zmq.Context(1)

        self._master_pub = context.socket(zmq.PUB)
        self._master_pub.bind( 'inproc://master/worker/coordination' )

        worker_sub = context.socket(zmq.SUB)
        worker_sub.connect( 'inproc://master/worker/coordination' )

        worker_pub = context.socket(zmq.PUB)
        worker_pub.bind( 'inproc://worker/master/coordination' )

        master_sub = context.socket(zmq.SUB)
        master_sub.connect( 'inproc://worker/master/coordination' )

        self._ioloop = IOLoop.instance()

        self._topic = ZMQ_SPYDER_MGMT_WORKER + 'testtopic'

        mgmt = ZmqMgmt( worker_sub, worker_pub, ioloop=self._ioloop)
        mgmt.addCallback(self._topic, self.callMe)
        mgmt.addCallback(ZMQ_SPYDER_MGMT_WORKER, self.onEnd)

        self._master_pub.send_multipart( [ self._topic, 'test'.encode() ] )

        self._ioloop.start()

        master_sub.setsockopt(zmq.SUBSCRIBE, "")
        self.assertEqual(ZMQ_SPYDER_MGMT_WORKER_QUIT_ACK, master_sub.recv_multipart())

if __name__ == '__main__':
    unittest.main()