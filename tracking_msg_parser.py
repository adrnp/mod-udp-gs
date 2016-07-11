"""
These are a collection of functions for parsing the tracking messages
"""

def parse_bearing(data):
    """
    parses a bearing message
    contains the position and calculated bearings after a rotation
    """

    # these are now comma separated values
    values = data.split(",")

    # extract the data
    msg = {}
    msg['bearing_cc'] = float(values[0])
    msg['bearing_max'] = float(values[1])
    msg['bearing_max3'] = float(values[2])
    msg['lat'] = float(values[3])
    msg['lon'] = float(values[4])
    msg['alt'] = float(values[5])

    # for now just print it out to the screen
    #print "Bearings Calculated:\n\tcc:\t{}\n\tmax:\t{}\n\tmax3:\t{}\n".format(
    #    msg['bearing_cc'], msg['bearing_max'], msg['bearing_max3'])

    # need to return a dictionary probably of the data
    return msg


def parse_rssi(data):
    """
    parses an rssi message
    """

    # these are now comma separated values
    values = data.split(",")

    # extract the values
    msg = {}
    msg['rotating'] = float(values[0])
    msg['directional'] = float(values[1])
    msg['omni'] = float(values[2])
    msg['heading'] = float(values[3])
    msg['lat'] = float(values[4])
    msg['lon'] = float(values[5])
    msg['alt'] = float(values[6])

    # for now just print it out to the screen
    #print "RSSI measurement:\nrot\t{}\n\tdir:\t{}\n\tomni:\t{}\n\thead:\t{}\n".format(
    #    msg['rotating'], msg['directional'], msg['omni'], msg['heading'])

    # return a dictionary with the data
    return msg

def parse_message(msg):
    """
    main parsing function
    splits the incoming data and calls the appropriate parser
    """

    # first split string by ":" to determine the message type
    splt = msg.split(":")
    msg_type = splt[0]

    # default to an empty dictionary (for an unknown message type)
    msg = {}

    # handle the message differently based on type
    if msg_type == "BEAR":
        # received a bearing message
        msg = parse_bearing(splt[1])
        msg['type'] = 1

    elif msg_type == "RSSI":
        # received an rssi message
        msg = parse_rssi(splt[1])
        msg['type'] = 2

    else:
        print("unknown message type\n")
        msg['type'] = 0

    return msg
