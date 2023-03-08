from queue import Queue
from unittest import TestCase
from unittest.mock import Mock, patch
from logical_clock import LogicalClock
from machine import Machine

class LogicalClockTests(TestCase):

    # mock the objects that we use to send messages between client/server
    client = Mock()
    conn = Mock()

    this_machine = Machine(0, 3000)


    def test_listen_through_socket(self):
        '''
        Description:
        - This function tests the functionality of the listen_through_socket method of a 
        machine object. It sets up a mock message queue and a mock socket object and simulates 
        receiving a message through the socket. It then asserts that the message was added 
        to the message queue.

        Parameters:
        - self: the instance of the test class

        Return:
        - None
        '''

        # mock the message queue for this specific function as we are mocking its inputs later
        self.this_machine.message_queue = Mock()

        # patch the socket module to return the mock socket object
        with patch('socket.socket', return_value=self.client):

            # create a mock message to simulate receiving a message through the socket
            mock_message = 'test message'.encode(self.this_machine.FORMAT)

            # set the return value of recv to the mock message
            self.client.recv.return_value = mock_message

            # call the listen_through_socket method
            x = self.this_machine.listen_through_socket(self.client)

            # assert that put was called on the message_queue with the message
            self.this_machine.message_queue.put.assert_called_once_with(mock_message.decode(self.this_machine.FORMAT))


    def test_run_tasks(self):
        '''
        Description:
        - This function tests the functionality of the run_tasks method of a machine object. 
        It sets up a mock socket object and simulates sending messages through the socket 
        using different task types. It then asserts that the correct number of calls to the 
        send method were made and that the logical clock was updated correctly.

        Parameters:
        - self: the instance of the test class
        
        Return:
        - None
        '''

        self.this_machine.logical_clock = LogicalClock()

        # patch the socket module to return the mock socket object
        with patch('socket.socket.send'):

            # test for task = 1 (send through client)
            task = 1

            # create a mock message to simulate sending a message through the socket
            mock_message = "[machine 0, task 1] the time is 0".encode()

            # call the run_tasks method again
            self.this_machine.run_tasks(task, self.client, self.conn, write_data=False)

            # assert that the send function was called in the client socket, and that
            # the logical clock was updated correctly
            self.client.send.assert_called_once_with(mock_message)
            self.assertEqual(self.this_machine.logical_clock.get_time(), 1)

            # test for task = 2 (send through server)
            task = 2

            # create a mock message to simulate sending a message through the socket
            mock_message = "[machine 0, task 2] the time is 1".encode()

            # call the run_tasks method again
            self.this_machine.run_tasks(task, self.client, self.conn, write_data=False)

            # assert that the send function was called in the server socket, and that
            # the logical clock was updated correctly
            self.conn.send.assert_called_once_with(mock_message)
            self.assertEqual(self.this_machine.logical_clock.get_time(), 2)

            # test for task = 3 (send through client and server)
            task = 3
            # create a mock message to simulate sending a message through the socket
            mock_message = "[machine 0, task 3] the time is 2".encode()

            # call the run_tasks method again
            self.this_machine.run_tasks(task, self.client, self.conn, write_data=False)
            
            # assert that the send function was called in the client and server socket, 
            # and that the logical clock was updated correctly
            self.assertEqual(self.client.send.call_count, 2)
            self.assertEqual(self.conn.send.call_count, 2)
            self.assertEqual(self.this_machine.logical_clock.get_time(), 3)

            # test for task = 4 (Internal Event)
            task = 4

            # call the run_tasks method again
            self.this_machine.run_tasks(task, self.client, self.conn, write_data=False)

            # assert that the send function was not called in the client and server socket, 
            # and that the logical clock was updated correctly
            self.assertEqual(self.client.send.call_count, 2)
            self.assertEqual(self.conn.send.call_count, 2)
            self.assertEqual(self.this_machine.logical_clock.get_time(), 4)

    def test_pop_message(self):
        '''
        Description:
        - This function tests the functionality of the pop_message method of a machine 
        object when messages exist to be read. It sets up a message queue and a logical 
        clock and simulates popping messages from the queue. It then asserts that the 
        queue size and logical clock were updated correctly.

        Parameters:
        - self: the instance of the test class

        Return:
        - None
        '''

        self.this_machine.message_queue = Queue()
        self.this_machine.logical_clock = LogicalClock()

        # queue up a message
        self.this_machine.message_queue.put("[machine 1, task 3] the time is 0")

        # pop the message and assert that the queue is empty and the logical clock was updated
        self.this_machine.pop_message(write_data=False)
        self.assertTrue(self.this_machine.message_queue.empty())
        self.assertEqual(self.this_machine.logical_clock.get_time(), 1)

        # queue up 2 messages
        self.this_machine.message_queue.put("[machine 1, task 3] the time is 1")
        self.this_machine.message_queue.put("[machine 2, task 3] the time is 6")

        # pop a message and assert that one message is still left, and that the logical clock
        # was updated
        self.this_machine.pop_message(write_data=False)
        self.assertEqual(self.this_machine.message_queue.qsize(), 1)
        self.assertEqual(self.this_machine.logical_clock.get_time(), 2)

        # pop the last message that should result in a logical clock jump, and assert that the
        # queue is now empty and the logical clock is updated correctly
        self.this_machine.pop_message(write_data=False)
        self.assertTrue(self.this_machine.message_queue.empty())
        self.assertEqual(self.this_machine.logical_clock.get_time(), 7)


    def test_logical_clock_methods(self):
        '''
        Description:
        - This function tests the functionality of the LogicalClock class methods. It 
        creates an instance of the class and tests the tick and update methods. It then 
        asserts that the time was updated correctly.

        Parameters:
        - self: the instance of the test class

        Return:
        - None
        '''
        logical_clock = LogicalClock()

        # test that the logical clock is initially set to 0
        self.assertEqual(logical_clock.get_time(), 0)

        # tick the clock and assert that the time updated correctly
        logical_clock.tick()
        self.assertEqual(logical_clock.get_time(), 1)

        # update the clock with too early of a time and assert that it still incremented the time by
        # only 1
        logical_clock.update(0)
        self.assertEqual(logical_clock.get_time(), 2)

        # update the clock with a later time and assert that there was a time jump
        logical_clock.update(5)
        self.assertEqual(logical_clock.get_time(), 6)