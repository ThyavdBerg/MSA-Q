import numpy
import math


def SqlSqrt(real_number):
    """Used to import the python sqrt function to sqlite.

    :param real_number: The number of which the square root will be calculated.
    :type real_number: float"""
    return math.sqrt(real_number)


def SqlCardinalDir(x, y):
    """ Takes a spatial point and determines its cardinal direction from 0,0 using normalized vectors. Can be
    imported into SQlite.

     :param x: x-coordinate or longitude
     :type x: float

     :param y: y-coordinate or latitude
     :type y: float

     :returns: One of eight cardinal directions (N, NE, E, SE, S, SW, W, NW)
     :rtype: str"""
    # Create normalized vectors for cardinal directions
    vecN = numpy.array([1, 0])
    vecNE = numpy.array([1, 1])
    norm_vecNE = vecNE / numpy.linalg.norm(vecNE)
    vecE = numpy.array([0, 1])
    vecSE = numpy.array([-1, 1])
    norm_vecSE = vecSE / numpy.linalg.norm(vecSE)
    vecS = numpy.array([-1, 0])
    vecSW = numpy.array([-1, -1])
    norm_vecSW = vecSW / numpy.linalg.norm(vecSW)
    vecW = numpy.array([0, -1])
    vecNW = numpy.array([1, -1])
    norm_vecNW = vecSE / numpy.linalg.norm(vecNW)

    vecPoint = numpy.array([x, y])
    # Calculate euclidean distances to all normalized vectors of cardinal directions
    dist_N = numpy.linalg.norm(vecN - vecPoint)
    dist_NE = numpy.linalg.norm(norm_vecNE - vecPoint)
    dist_E = numpy.linalg.norm(vecE - vecPoint)
    dist_SE = numpy.linalg.norm(norm_vecSE - vecPoint)
    dist_S = numpy.linalg.norm(vecS - vecPoint)
    dist_SW = numpy.linalg.norm(norm_vecSW - vecPoint)
    dist_W = numpy.linalg.norm(vecW - vecPoint)
    dist_NW = numpy.linalg.norm(norm_vecNW - vecPoint)
    list_dist = [dist_N, dist_NE, dist_E, dist_SE, dist_S, dist_SW, dist_W, dist_NW]
    if min(list_dist) == list_dist[0]:
        return 'N'
    elif min(list_dist) == list_dist[1]:
        return 'NE'
    elif min(list_dist) == list_dist[2]:
        return 'E'
    elif min(list_dist) == list_dist[3]:
        return 'SE'
    elif min(list_dist) == list_dist[4]:
        return 'S'
    elif min(list_dist) == list_dist[5]:
        return 'SW'
    elif min(list_dist) == list_dist[6]:
        return 'W'
    elif min(list_dist) == list_dist[7]:
        return 'NW'
    else:
        return 'Error'
