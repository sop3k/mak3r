"""
OBJ file reader.
OBJ are wavefront object files. These are quite common and can be exported
from a lot of 3D tools.
Only vertex information is read from the OBJ file,
information about textures and normals is ignored.

http://en.wikipedia.org/wiki/Wavefront_.obj_file
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

from omni3dapp.util import printableObject
from omni3dapp.logger import log


def loadScene(filename, callback=None):
    log.debug("entered loadScene in obj loader")
    obj = printableObject.printableObject(filename)
    m = obj._addMesh()

    vertexList = []
    faceList = []

    if callback:
        callback(0.01)
    f = open(filename, "r")
    for line in f:
        parts = line.split()
        if len(parts) < 1:
            continue
        if parts[0] == 'v':
            vertexList.append([float(parts[1]), float(parts[2]),
                               float(parts[3])])
        if parts[0] == 'f':
            parts = map(lambda p: p.split('/')[0], parts)
            for idx in xrange(1, len(parts)-2):
                faceList.append([int(parts[1]), int(parts[idx+1]),
                                 int(parts[idx+2])])
    f.close()

    flen = len(faceList)
    m._prepareFaceCount(flen)
    if callback:
        callback(0.02)
    for no, f in enumerate(faceList):
        i = f[0] - 1
        j = f[1] - 1
        k = f[2] - 1
        if i < 0 or i >= len(vertexList):
            i = 0
        if j < 0 or j >= len(vertexList):
            j = 0
        if k < 0 or k >= len(vertexList):
            k = 0
        m._addFace(vertexList[i][0], vertexList[i][1], vertexList[i][2],
                   vertexList[j][0], vertexList[j][1], vertexList[j][2],
                   vertexList[k][0], vertexList[k][1], vertexList[k][2])

        if callback and no % 100 == 0:
            callback((no+1)*0.97/flen)

    obj._postProcessAfterLoad()
    return [obj]
