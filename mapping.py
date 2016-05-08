import os
import simplekml


class GEMapper(object):

    def __init__(self):
        # style to be used
        self.styleGreen = simplekml.Style()
        self.styleGreen.linestyle.color = simplekml.Color.green
        self.styleGreen.polystyle.color = simplekml.Color.changealphaint(
            180, simplekml.Color.forestgreen)
        self.styleGreen.linestyle.width = 2

        # setup the ballon animation KML
        self.vehicleKml = simplekml.Kml()
        self.vehicleKml.document.name = "Vehicle"

        self.vehiclePt = self.vehicleKml.newpoint(name="Jager")
        self.vehiclePt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/paddle/grn-blank.png"
        self.vehiclePt.style.iconstyle.heading = 0.0
        self.vehiclePt.altitudemode = simplekml.AltitudeMode.relativetoground
        self.vehiclePt.extrude = 1

        self.vehicleTrace = self.vehicleKml.newlinestring(name="path")
        self.vehicleTrace.style = self.styleGreen
        self.vehicleTrace.altitudemode = simplekml.AltitudeMode.relativetoground
        self.vehicleTrace.extrude = 1

        self.prevLocs = []
        self.pathLength = 150  # how many points to save in the trace

        # create the network link
        self.create_network_link()

    def create_network_link(self):
        # create a network link file for for jager
        linkKml = simplekml.Kml()
        networklink = linkKml.newnetworklink(name="Refresh Link")
        networklink.link.href = os.getcwd() + "/jager_meas.kml"
        networklink.link.refreshmode = simplekml.RefreshMode.oninterval
        networklink.link.refreshinterval = 1.0
        linkKml.save("jager_meas_link.kml")

    def update_path(self, lon, lat, alt):

        if len(self.prevLocs) < self.pathLength:
            self.prevLocs.append((lon, lat, alt))
        else:
            self.prevLocs.pop(0)
            self.prevLocs.append((lon, lat, alt))

        # update the plane kml file
        self.vehiclePt.coords = [(lon, lat, alt)]
        self.vehicleTrace.coords = self.prevLocs

        # save the file
        self.vehicleKml.save("jager_meas.kml")
