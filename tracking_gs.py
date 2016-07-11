"""
Tkinter based ground station for the tracking data coming down from JAGER.
"""
import Tkinter
import time
import threading
import random
import Queue
import socket
import sys
import numpy as np
import tracking_msg_parser as tmp

# matplot lib handling for use with Tkinter
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

# constants for the UDP connection
UDP_IP = "192.168.1.33" # "127.0.0.1"  # "171.64.161.62"  # this is this machine's IP address
UDP_PORT = 21234


def add_to_array(arr, val):
    """
    simple function to append to the end of an array
    and maintain its size
    """
    a = np.delete(arr, 0)
    a = np.append(a, val)
    return a


class GuiPart:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        # Set up the GUI
        console = Tkinter.Button(master, text='Done', command=endCommand)
        console.pack()

        # make some plots
        f = Figure()
        self.axis = f.add_subplot(121)
        self.x_data = np.zeros(50)
        self.y_data = np.zeros(50)
        self.line1, = self.axis.plot(self.x_data, self.y_data)
        self.axis.set_ylim([-70, 0])
        self.start = time.time()

        self.axis_rot = f.add_subplot(122, polar=True)
        self.headings = np.zeros(50)
        self.gains = np.zeros(50)
        self.axis_rot.set_ylim(-70, -10)
        self.axis_rot.set_yticks(np.arange(-70, -10, 6))
        self.axis_rot.set_xticks(np.arange(0, 2 * np.pi, np.pi / 6))
        self.axis_rot.grid(True)
        self.gain_line, = self.axis_rot.plot(self.headings, self.gains, marker="x", linestyle="-", linewidth=2)

        self.headings = np.zeros(50)
        self.gains = np.zeros(50)
        
        # add a canvas
        self.canvas = FigureCanvasTkAgg(f, master=master)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)  # not sure what this line does
        #self.canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)  # not sure what this line does

        # Add more GUI stuff here

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                
                # parse the rssi messages
                if msg['type'] == 2:  # rssi message

                    self.x_data = add_to_array(self.x_data, time.time() - self.start)
                    self.y_data = add_to_array(self.y_data, msg['directional'])
                    self.line1.set_ydata(self.y_data)
                    self.line1.set_xdata(self.x_data)
                    self.axis.set_xlim([np.amin(self.x_data), np.amax(self.x_data)])
                    
                    if msg['directional'] != sys.maxint:
                        self.headings = add_to_array(self.headings, msg['heading'] * np.pi/180)
                        self.gains = add_to_array(self.gains, float(msg['directional']))
                        self.gain_line.set_xdata(self.headings)
                        self.gain_line.set_ydata(self.gains)

                    # update the figures
                    self.canvas.show()

                # TODO: handle the bearing messages

            except Queue.Empty:
                pass

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master

        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
    	self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            sys.exit(1)
        self.master.after(10, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """

        # set up the socket for communication with JAGER
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        while self.running:
            start = time.time()
            
            msg, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            parsed = tmp.parse_message(msg)
            self.queue.put(parsed)

            # TODO: want to make sure we can get bearing messages
            # TODO: build the map from this thread - for google earth use

            end = time.time()
            remain = start + 0.2 - end
            if remain > 0:
                time.sleep(remain)

    def endApplication(self):
        self.running = 0

rand = random.Random()
root = Tkinter.Tk()

client = ThreadedClient(root)
root.mainloop()