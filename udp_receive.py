import socket
import sys
from matplotlib import pyplot as plt
from mapping import GEMapper
import gain_pattern_plotting as gpp

UDP_IP = "127.0.0.1"  # "171.64.161.62"  # this is this machine's IP address
UDP_PORT = 21234

FIG_ROTATION = 1
FIG_RSSI = 2

MAX_DISPLAY = 100  # the maximum number of current RSSI values to display

# doing this poorly with globals for now
# but these are globals containing the info for the plotting
rot_rssi_val = []  # the rssi values during a rotation
rot_headings = []  # the heading during a rotation

all_rssi_val = []  # a chunk of the most recent rssi values
all_meas_index = []  # the index for the chunk of rssi values
ind = 0

# class to handle the mapping
mapper = GEMapper()


def parse_bearing(data):
    global mapper

    # these are now comma separated values
    values = data.split(",")

    # extract the data
    bearing_cc = float(values[0])
    bearing_max = float(values[1])
    bearing_max3 = float(values[2])
    lat = float(values[3])
    lon = float(values[4])
    alt = float(values[5])

    # for now just print it out to the screen
    print "Bearings Calculated:\n\tcc:\t{}\n\tmax:\t{}\n\tmax3:\t{}\n".format(
        bearing_cc, bearing_max, bearing_max3)

    # plot with the bearings
    gpp.plot_gain_pattern(rot_headings, rot_rssi_val, FIG_ROTATION,
                          bearing_cc, bearing_max, bearing_max3)

    # update the map with this new point
    mapper.update_path(lon, lat, alt)


def parse_rssi(data):
    global rot_rssi_val
    global rot_headings
    global all_rssi_val
    global all_meas_index
    global ind

    # these are now comma separated values
    values = data.split(",")

    # extract the values
    rotating = float(values[0])
    directional = float(values[1])
    omni = float(values[2])
    heading = float(values[3])
    lat = float(values[4])
    lon = float(values[5])
    alt = float(values[6])

    # for now just print it out to the screen
    print "RSSI measurement:\nrot\t{}\n\tdir:\t{}\n\tomni:\t{}\n\thead:\t{}\n".format(
        rotating, directional, omni, heading)

    # add to the necessary plot
    if rotating == 1:
        rot_rssi_val.append(directional)
        rot_headings.append(heading)

        print "appending rssi {} with heading {}".format(directional, heading)

        # plot the gain pattern
        gpp.plot_gain_pattern(rot_headings, rot_rssi_val, FIG_ROTATION)

    else:
        # reset the rotational measurements
        rot_rssi_val = []
        rot_headings = []

        ind += 1
        if directional == sys.maxint:
            directional = float('nan')

        all_rssi_val.append(directional)
        all_meas_index.append(ind)
        if len(all_rssi_val) > MAX_DISPLAY:
            all_rssi_val.pop(0)
            all_meas_index.pop(0)

        plt.figure(FIG_RSSI)
        plt.plot(all_meas_index, all_rssi_val,
                 marker="x", linestyle="-", linewidth=2, color="r")
        plt.axis([min(all_meas_index), max(all_meas_index), -80, -30])
        plt.pause(0.001)

    # update the map with this new point
    mapper.update_path(lon, lat, alt)


def parse_message(msg):
    # first split string by ":" to determine the message type
    splt = msg.split(":")
    msg_type = splt[0]

    # handle the message differently based on type
    if msg_type == "BEAR":
        # received a bearing message
        parse_bearing(splt[1])

    elif msg_type == "RSSI":
        # received an rssi message
        parse_rssi(splt[1])

    else:
        print("unknown message type\n")

    return 1


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    # set up the plotting
    plt.ion()
    plt.figure(1)
    plt.show()
    plt.figure(2)
    plt.show()

    while True:
        msg, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        parse_message(msg)


if __name__ == "__main__":
    main()
