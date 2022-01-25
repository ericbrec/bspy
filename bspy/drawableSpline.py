import numpy as np
from OpenGL.GL import *
from os import path
from bspy import Spline

class DrawableSpline(Spline):

    maxOrder = 9
    maxCoefficients = 120
    maxKnots = maxCoefficients + maxOrder
    maxFloats = 4 + 2 * maxKnots + 4 * maxCoefficients * maxCoefficients

    HULL = (1 << 0)
    SHADED = (1 << 1)
    BOUNDARY = (1 << 2)
    ISOPARMS = (1 << 3)

    def __init__(self, order, knots, coefficients, name=None):
        floatCount = 0
        coefficientCount = 1
        dimension = len(order)
        for i in range(dimension):
            assert order[i] <= self.maxOrder
            assert len(knots[i]) == order[i] + coefficients.shape[dimension - 1 - i]
            floatCount += 2 + order[i] + coefficients.shape[dimension - 1 - i]
            coefficientCount *= coefficients.shape[dimension - 1 - i]
        assert coefficients.shape[dimension] == 4 # Coefficients are all 4-vectors (homogeneous coordinates)
        assert floatCount + 4 * coefficientCount <= self.maxFloats
        for knotArray in knots:
            assert knotArray.dtype == np.float32
        assert coefficients.dtype == np.float32

        coefs = coefficients.T
        Spline.__init__(self, dimension, 4, order, coefs.shape[1:], knots, coefs)

        self.fillColor = np.array((0.0, 1.0, 0.0, 1.0), np.float32)
        self.lineColor = np.array((0.0, 0.0, 0.0, 1.0), np.float32)
        self.options = self.SHADED | self.BOUNDARY
        if name is None:
            self.name = "[{0}, {1}]".format(self.coefs[0], self.coefs[1])
        else:
            self.name = name

    def __str__(self):
        return self.name
    
    def DrawCurve(self, frame, drawCoefficients):
        if self.options & self.HULL:
            glColor3f(0.0, 0.0, 1.0)
            glBegin(GL_LINE_STRIP)
            for point in drawCoefficients:
                glVertex3f(point[0], point[1], point[2])
            glEnd()

        glUseProgram(frame.curveProgram)
        glUniform4fv(frame.uCurveLineColor, 1, self.lineColor)
        glBindBuffer(GL_TEXTURE_BUFFER, frame.splineDataBuffer)
        offset = 0
        size = 4 * 2
        glBufferSubData(GL_TEXTURE_BUFFER, offset, size, np.array((self.order[0], drawCoefficients.shape[0]), np.float32))
        offset += size
        size = 4 * len(self.knots[0])
        glBufferSubData(GL_TEXTURE_BUFFER, offset, size, self.knots[0])
        offset += size
        size = 4 * 4 * len(drawCoefficients)
        glBufferSubData(GL_TEXTURE_BUFFER, offset, size, drawCoefficients)
        glEnableVertexAttribArray(frame.aCurveParameters)
        glPatchParameteri(GL_PATCH_VERTICES, 1)
        glDrawArraysInstanced(GL_PATCHES, 0, 1, drawCoefficients.shape[0] - self.order[0] + 1)
        glDisableVertexAttribArray(frame.aCurveParameters)
        glUseProgram(0)

    def DrawSurface(self, frame, drawCoefficients):
        if self.options & self.HULL:
            glColor3f(0.0, 0.0, 1.0)
            for pointList in drawCoefficients:
                glBegin(GL_LINE_STRIP)
                for point in pointList:
                    glVertex3f(point[0], point[1], point[2])
                glEnd()

        glUseProgram(frame.surfaceProgram)
        glUniform4fv(frame.uSurfaceFillColor, 1, self.fillColor)
        glUniform4fv(frame.uSurfaceLineColor, 1, self.lineColor)
        glUniform1i(frame.uSurfaceOptions, self.options)
        glBindBuffer(GL_TEXTURE_BUFFER, frame.splineDataBuffer)
        offset = 0
        size = 4 * 4
        glBufferSubData(GL_TEXTURE_BUFFER, offset, size, np.array((self.order[0], self.order[1], drawCoefficients.shape[1], drawCoefficients.shape[0]), np.float32))
        offset += size
        size = 4 * len(self.knots[0])
        glBufferSubData(GL_TEXTURE_BUFFER, offset, size, self.knots[0])
        offset += size
        size = 4 * len(self.knots[1])
        glBufferSubData(GL_TEXTURE_BUFFER, offset, size, self.knots[1])
        offset += size
        size = 4 * 4 * drawCoefficients.shape[1] * drawCoefficients.shape[0]
        glBufferSubData(GL_TEXTURE_BUFFER, offset, size, drawCoefficients)
        glEnableVertexAttribArray(frame.aSurfaceParameters)
        glPatchParameteri(GL_PATCH_VERTICES, 1)
        glDrawArraysInstanced(GL_PATCHES, 0, 1, (drawCoefficients.shape[1] - self.order[0] + 1) * (drawCoefficients.shape[0] - self.order[1] + 1))
        glDisableVertexAttribArray(frame.aSurfaceParameters)
        glUseProgram(0)

    def Draw(self, frame, transform):
        drawCoefficients = self.coefs.T @ transform
        if len(self.order) == 1:
            self.DrawCurve(frame, drawCoefficients)
        elif len(self.order) == 2:
            self.DrawSurface(frame, drawCoefficients)

    def Save(self, fileName):
        kw = {}
        kw["order"] = order=np.array(self.order, np.int32)
        for i in range(len(self.knots)):
            kw["knots{count}".format(count=i)] = self.knots[i]
        kw["coefficients"] = self.coefs
        np.savez(fileName, **kw )
    
    @staticmethod
    def Load(fileName):
        kw = np.load(fileName)
        order = kw["order"]
        knots = []
        for i in range(len(order)):
            knots.append(kw["knots{count}".format(count=i)])
        coefficients = kw["coefficients"]
        spline = DrawableSpline(order, knots, coefficients, path.splitext(path.split(fileName)[1])[0])
        return spline