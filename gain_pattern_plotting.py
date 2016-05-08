import sys
import numpy
from matplotlib import pyplot


def plot_gain_pattern(angles, gains, figure_number=1,
                      bearing_cc=None, bearing_max=None, bearing_max3=None):

    # get the angles into an array and as radians
    a = numpy.array(angles)
    a *= numpy.pi / 180.0

    gains = numpy.array(gains)

    # get the gains in the right format (nan instead of max int)
    gainsnan = []
    for i in range(0, gains.size):
        if gains[i] == sys.maxint:
            gainsnan.append(float('nan'))
        else:
            gainsnan.append(float(gains[i]))
    g = numpy.array(gainsnan)

    gmin = numpy.nanmin(g)
    gmax = numpy.nanmax(g)

    # even out the upper limit to be a multiple of 3 db for prettiness of plot
    rem = (gmax - gmin) % 3
    if rem != 0:
        gmax += (3 - rem)

    # for plotting truncate array to skip all nan values
    g_trim = g[~numpy.isnan(g)]
    a_trim = a[~numpy.isnan(g)]

    # don't try to plot if no measurements have yet to have a real value
    if g_trim.size == 0:
        return

    # to make the pattern look closed, repeat the first value at the end
    g_trim = numpy.append(g_trim, g_trim[0])
    a_trim = numpy.append(a_trim, a_trim[0])

    # do the actual plotting
    pyplot.figure(figure_number)
    pyplot.clf()
    ax = pyplot.subplot(111, polar=True)
    ax.set_ylim(gmin, gmax)
    ax.set_yticks(numpy.arange(gmin, gmax, 3))
    ax.set_xticks(numpy.arange(0, 2 * numpy.pi, numpy.pi / 6))
    ax.plot(a_trim, g_trim, marker="x", linestyle="-", linewidth=2)
    ax.grid(True)

    # add the bearing lines if they have been set
    if bearing_cc is not None:
        head = bearing_max * numpy.pi / 180.0
        ax.plot([head, head], [gmin, gmax],
                linestyle='--', linewidth=2, color='g')

        head = bearing_max3 * numpy.pi / 180.0
        ax.plot([head, head], [gmin, gmax],
                linestyle='--', linewidth=2, color='c')

        head = bearing_cc * numpy.pi / 180.0
        ax.plot([head, head], [gmin, gmax],
                linestyle='--', linewidth=2, color='k')

    pyplot.draw()
    pyplot.pause(0.001)
