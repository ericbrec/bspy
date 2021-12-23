import numpy as np
import quaternion as quat
import tkinter as tk
from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
from pyopengltk import OpenGLFrame
from bspy.spline import Spline

class SplineOpenGLFrame(OpenGLFrame):

    computeBasisCode = """
        void ComputeBasis(in int offset, in int order, in int n, in int m, in float u, 
            out float uBasis[{maxBasis}], out float duBasis[{maxBasis}], out float du2Basis[{maxBasis}])
        {{
            int degree = 1;

            uBasis = float[{maxBasis}](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
            duBasis = float[{maxBasis}](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
            du2Basis = float[{maxBasis}](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
            uBasis[order-1] = 1.0;

            while (degree < order - 2)
            {{
                int b = order - degree - 1;
                for (int i = m - degree; i < m + 1; i++)
                {{
                    float gap0 = texelFetch(uSplineData, offset + i + degree).x - texelFetch(uSplineData, offset + i).x; // knots[i+degree] - knots[i]
                    float gap1 = texelFetch(uSplineData, offset + i + degree + 1).x - texelFetch(uSplineData, offset + i + 1).x; // knots[i+degree+1] - knots[i+1]
                    gap0 = gap0 < 1.0e-8 ? 0.0 : 1.0 / gap0;
                    gap1 = gap1 < 1.0e-8 ? 0.0 : 1.0 / gap1;

                    float val0 = (u - texelFetch(uSplineData, offset + i).x) * gap0; // (u - knots[i]) * gap0;
                    float val1 = (texelFetch(uSplineData, offset + i + degree + 1).x - u) * gap1; // (knots[i+degree+1] - u) * gap1;
                    uBasis[b] = uBasis[b] * val0 + uBasis[b+1] * val1;
                    b++;
                }}
                degree++;
            }}
            while (degree < order - 1)
            {{
                int b = order - degree - 1;
                for (int i = m - degree; i < m + 1; i++)
                {{
                    float gap0 = texelFetch(uSplineData, offset + i + degree).x - texelFetch(uSplineData, offset + i).x; // knots[i+degree] - knots[i]
                    float gap1 = texelFetch(uSplineData, offset + i + degree + 1).x - texelFetch(uSplineData, offset + i + 1).x; // knots[i+degree+1] - knots[i+1]
                    gap0 = gap0 < 1.0e-8 ? 0.0 : 1.0 / gap0;
                    gap1 = gap1 < 1.0e-8 ? 0.0 : 1.0 / gap1;

                    float d0 = degree * gap0;
                    float d1 = -degree * gap1;
                    du2Basis[b] = uBasis[b] * d0 + uBasis[b+1] * d1;
                    float val0 = (u - texelFetch(uSplineData, offset + i).x) * gap0; // (u - knots[i]) * gap0;
                    float val1 = (texelFetch(uSplineData, offset + i + degree + 1).x - u) * gap1; // (knots[i+degree+1] - u) * gap1;
                    uBasis[b] = uBasis[b] * val0 + uBasis[b+1] * val1;
                    b++;
                }}
                degree++;
            }}
            while (degree < order)
            {{
                int b = order - degree - 1;
                for (int i = m - degree; i < m + 1; i++)
                {{
                    float gap0 = texelFetch(uSplineData, offset + i + degree).x - texelFetch(uSplineData, offset + i).x; // knots[i+degree] - knots[i]
                    float gap1 = texelFetch(uSplineData, offset + i + degree + 1).x - texelFetch(uSplineData, offset + i + 1).x; // knots[i+degree+1] - knots[i+1]
                    gap0 = gap0 < 1.0e-8 ? 0.0 : 1.0 / gap0;
                    gap1 = gap1 < 1.0e-8 ? 0.0 : 1.0 / gap1;

                    float d0 = degree * gap0;
                    float d1 = -degree * gap1;
                    duBasis[b] = uBasis[b] * d0 + uBasis[b+1] * d1;
                    du2Basis[b] = du2Basis[b] * d0 + du2Basis[b+1] * d1;
                    float val0 = (u - texelFetch(uSplineData, offset + i).x) * gap0; // (u - knots[i]) * gap0;
                    float val1 = (texelFetch(uSplineData, offset + i + degree + 1).x - u) * gap1; // (knots[i+degree+1] - u) * gap1;
                    uBasis[b] = uBasis[b] * val0 + uBasis[b+1] * val1;
                    b++;
                }}
                degree++;
            }}
        }}
    """

    computeDeltaCode = """
        void ComputeDelta(in vec4 point, in vec3 dPoint, in vec3 d2Point, inout float delta)
        {
            float zScale = 1.0 / (uScreenScale.z - point.z);
            float zScale2 = zScale * zScale;
            float zScale3 = zScale2 * zScale;
            vec2 projection = uScreenScale.z > 1.0 ? 
                vec2(uScreenScale.x * (d2Point.x * zScale - 2.0 * dPoint.x * dPoint.z * zScale2 +
                    point.x * (2.0 * dPoint.z * dPoint.z * zScale3 - d2Point.z * zScale2)),
                    uScreenScale.y * (d2Point.y * zScale - 2.0 * dPoint.y * dPoint.z * zScale2 +
                    point.y * (2.0 * dPoint.z * dPoint.z * zScale3 - d2Point.z * zScale2)))
                : vec2(uScreenScale.x * d2Point.x, uScreenScale.y * d2Point.y);
            float projectionLength = length(projection);
            delta = projectionLength < 1.0e-8 ? delta : 1.0 / sqrt(projectionLength);
        }
    """

    curveVertexShaderCode = """
        #version 410 core
     
        const int header = 2;

        attribute vec4 aParameters;

        uniform samplerBuffer uSplineData;

        out SplineInfo
        {
            int uOrder;
            int uN;
            int uM;
            float firstU;
            float lastU;
        } outData;

        void main()
        {
            outData.uOrder = int(texelFetch(uSplineData, 0).x);
            outData.uN = int(texelFetch(uSplineData, 1).x);
            outData.uM = min(gl_InstanceID + outData.uOrder - 1, outData.uN - 1);
            outData.firstU = texelFetch(uSplineData, header + outData.uM).x; // knots[uM]
            outData.lastU = texelFetch(uSplineData, header + outData.uM + 1).x; // knots[uM+1]
            gl_Position = aParameters;
        }
    """

    curveTCShaderCode = """
        #version 410 core

        layout (vertices = 1) out;

        const int header = 2;

        in SplineInfo
        {{
            int uOrder;
            int uN;
            int uM;
            float firstU;
            float lastU;
        }} inData[];

        uniform mat4 uProjectionMatrix;
        uniform vec3 uScreenScale;
        uniform samplerBuffer uSplineData;

        patch out SplineInfo
        {{
            int uOrder;
            int uN;
            int uM;
            float firstU;
            float lastU;
        }} outData;

        void main()
        {{
            outData.uOrder = inData[0].uOrder;
            outData.uN = inData[0].uN;
            outData.uM = inData[0].uM;
            outData.firstU = inData[0].firstU;
            outData.lastU = inData[0].lastU;

            gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;

            // Calculate the tessellation levels
            gl_TessLevelOuter[0] = 5.0;
            gl_TessLevelOuter[1] = 3.0;
        }}
    """.format()

    curveTEShaderCode = """
        #version 410 core

        layout (isolines, point_mode) in;

        const int header = 2;

        patch in SplineInfo
        {{
            int uOrder;
            int uN;
            int uM;
            float firstU;
            float lastU;
        }} inData;

        uniform mat4 uProjectionMatrix;
        uniform vec3 uScreenScale;
        uniform vec3 uSplineColor;
        uniform samplerBuffer uSplineData;

        out SplineInfo
        {{
            int uOrder;
            int uN;
            int uM;
            float firstU;
            float lastU;
        }} outData;
        out vec3 splineColor;

        void main()
        {{
            outData.uOrder = inData.uOrder;
            outData.uN = inData.uN;
            outData.uM = inData.uM;
            outData.firstU = inData.firstU;
            outData.lastU = inData.lastU;

            splineColor = uSplineColor;
            gl_Position = uProjectionMatrix * vec4(gl_TessCoord.x, gl_TessCoord.y, 0.0, 1.0);
        }}
    """.format()

    curveGeometryShaderCode = """
        #version 410 core

        layout( points ) in;
        layout( line_strip, max_vertices = {maxVertices} ) out;

        const int header = 2;

        in SplineInfo
        {{
            int uOrder;
            int uN;
            int uM;
            float firstU;
            float lastU;
        }} inData[];

        uniform mat4 uProjectionMatrix;
        uniform vec3 uScreenScale;
        uniform vec3 uSplineColor;
        uniform samplerBuffer uSplineData;

        out vec3 splineColor;

        {computeBasisCode}

        {computeDeltaCode}

        void DrawCurvePoints(in int order, in int n, in int m, in float u, inout float deltaU)
        {{
            float uBasis[{maxBasis}];
            float duBasis[{maxBasis}];
            float du2Basis[{maxBasis}];

            ComputeBasis(header, order, n, m, u, uBasis, duBasis, du2Basis);
            
            vec4 point = vec4(0.0, 0.0, 0.0, 0.0);
            vec3 dPoint = vec3(0.0, 0.0, 0.0);
            vec3 d2Point = vec3(0.0, 0.0, 0.0);
            int i = header + order + n + 4 * (m + 1 - order);
            for (int b = 0; b < order; b++) // loop from coefficient[m+1-order] to coefficient[m+1]
            {{
                point.x += uBasis[b] * texelFetch(uSplineData, i).x;
                point.y += uBasis[b] * texelFetch(uSplineData, i+1).x;
                point.z += uBasis[b] * texelFetch(uSplineData, i+2).x;
                point.w += uBasis[b] * texelFetch(uSplineData, i+3).x;
                dPoint.x += duBasis[b] * texelFetch(uSplineData, i).x;
                dPoint.y += duBasis[b] * texelFetch(uSplineData, i+1).x;
                dPoint.z += duBasis[b] * texelFetch(uSplineData, i+2).x;
                d2Point.x += du2Basis[b] * texelFetch(uSplineData, i).x;
                d2Point.y += du2Basis[b] * texelFetch(uSplineData, i+1).x;
                d2Point.z += du2Basis[b] * texelFetch(uSplineData, i+2).x;
                i += 4;
            }}

            gl_Position = uProjectionMatrix * point;
            EmitVertex();
            gl_Position = uProjectionMatrix * vec4(point.x - 0.01*dPoint.y, point.y + 0.01*dPoint.x, point.z, point.w);
            EmitVertex();
            gl_Position = uProjectionMatrix * point;
            EmitVertex();
            
            ComputeDelta(point, dPoint, d2Point, deltaU);
        }}

        void main()
        {{
            int order = inData[0].uOrder;
            int n = inData[0].uN;
            int m = inData[0].uM;
            float u = inData[0].firstU;
            float lastU = inData[0].lastU;
            float deltaU = 0.5 * (lastU - u);
            int vertices = 0;

            splineColor = uSplineColor;
            while (u < lastU && vertices <= {maxVertices} - 6) // Save room for the vertices at u and lastU
            {{
                DrawCurvePoints(order, n, m, u, deltaU);
                u += deltaU;
                vertices += 3;
            }}
            DrawCurvePoints(order, n, m, lastU, deltaU);
            vertices += 3;
            EndPrimitive();
        }}
    """

    surfaceVertexShaderCode = """
        #version 410 core

        const int header = 4;
     
        attribute vec4 aParameters;

        uniform samplerBuffer uSplineData;

        out SplineInfo
        {
            int uOrder;
            int vOrder;
            int uN;
            int vN;
            int uM;
            int vM;
            float firstU;
            float firstV;
            float lastU;
            float lastV;
        } outData;

        void main()
        {
            outData.uOrder = int(texelFetch(uSplineData, 0).x);
            outData.vOrder = int(texelFetch(uSplineData, 1).x);
            outData.uN = int(texelFetch(uSplineData, 2).x);
            outData.vN = int(texelFetch(uSplineData, 3).x);
            int stride = outData.vN - outData.vOrder + 1;

            outData.uM = min(int(gl_InstanceID / stride) + outData.uOrder - 1, outData.uN - 1);
            outData.vM = min(int(mod(gl_InstanceID, stride)) + outData.vOrder - 1, outData.vN - 1);
            outData.firstU = texelFetch(uSplineData, header + outData.uM).x; // uKnots[uM]
            outData.firstV = texelFetch(uSplineData, header + outData.uOrder + outData.uN + outData.vM).x; // vKnots[vM]
            outData.lastU = texelFetch(uSplineData, header + outData.uM + 1).x; // uKnots[uM+1]
            outData.lastV = texelFetch(uSplineData, header + outData.uOrder + outData.uN + outData.vM + 1).x; // vKnots[vM+1]
            gl_Position = aParameters;
        }
    """

    surfaceTCShaderCode = """
        #version 410 core

        layout (vertices = 1) out;

        const int header = 4;

        in SplineInfo
        {{
            int uOrder;
            int vOrder;
            int uN;
            int vN;
            int uM;
            int vM;
            float firstU;
            float firstV;
            float lastU;
            float lastV;
        }} inData[];

        uniform mat4 uProjectionMatrix;
        uniform vec3 uScreenScale;
        uniform samplerBuffer uSplineData;

        patch out PatchData
        {{
            int uM;
            int vM;
        }} patchData;

        void main()
        {{
            gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;

            // Set the control points of the output patch
            for (int i = 0 ; i < 3 ; i++)
            {{
                oPatch.Normal[i] = Normal_CS_in[i];
                oPatch.TexCoord[i] = TexCoord_CS_in[i];
            }}

            // Calculate the tessellation levels
            gl_TessLevelOuter[0] = gTessellationLevel;
            gl_TessLevelOuter[1] = gTessellationLevel;
            gl_TessLevelOuter[2] = gTessellationLevel;
            gl_TessLevelInner[0] = gTessellationLevel;
        }}
    """

    surfaceGeometryShaderCode = """
        #version 410 core

        layout( points ) in;
        layout( triangle_strip, max_vertices = {maxVertices} ) out;

        const int header = 4;

        in SplineInfo
        {{
            int uOrder;
            int vOrder;
            int uN;
            int vN;
            int uM;
            int vM;
            float firstU;
            float firstV;
            float lastU;
            float lastV;
        }} inData[];

        uniform mat4 uProjectionMatrix;
        uniform vec3 uScreenScale;
        uniform vec3 uSplineColor;
        uniform vec3 uLightDirection;
        uniform samplerBuffer uSplineData;

        out vec3 splineColor;

        {computeBasisCode}

        {computeDeltaCode}

        void DrawSurfacePoints(in int uOrder, in int uN, in int uM,
            in float uBasis[{maxBasis}], in float duBasis[{maxBasis}],
            in float uBasisNext[{maxBasis}], in float duBasisNext[{maxBasis}],
            in int vOrder, in int vN, in int vM, in float v, inout float deltaV)
        {{
            float vBasis[{maxBasis}];
            float dvBasis[{maxBasis}];
            float dv2Basis[{maxBasis}];

            ComputeBasis(header + uOrder + uN, vOrder, vN, vM, v, vBasis, dvBasis, dv2Basis);
            
            vec4 point = vec4(0.0, 0.0, 0.0, 0.0);
            vec3 duPoint = vec3(0.0, 0.0, 0.0);
            vec3 dvPoint = vec3(0.0, 0.0, 0.0);
            vec3 dv2Point = vec3(0.0, 0.0, 0.0);
            int j = header + uOrder + uN + vOrder + vN + (vM + 1 - vOrder) * 4;
            for (int vB = 0; vB < vOrder; vB++)
            {{
                int i = j + (uM + 1 - uOrder) * vN * 4;
                for (int uB = 0; uB < uOrder; uB++)
                {{
                    point.x += uBasis[uB] * vBasis[vB] * texelFetch(uSplineData, i).x;
                    point.y += uBasis[uB] * vBasis[vB] * texelFetch(uSplineData, i+1).x;
                    point.z += uBasis[uB] * vBasis[vB] * texelFetch(uSplineData, i+2).x;
                    point.w += uBasis[uB] * vBasis[vB] * texelFetch(uSplineData, i+3).x;
                    duPoint.x += duBasis[uB] * vBasis[vB] * texelFetch(uSplineData, i).x;
                    duPoint.y += duBasis[uB] * vBasis[vB] * texelFetch(uSplineData, i+1).x;
                    duPoint.z += duBasis[uB] * vBasis[vB] * texelFetch(uSplineData, i+2).x;
                    dvPoint.x += uBasis[uB] * dvBasis[vB] * texelFetch(uSplineData, i).x;
                    dvPoint.y += uBasis[uB] * dvBasis[vB] * texelFetch(uSplineData, i+1).x;
                    dvPoint.z += uBasis[uB] * dvBasis[vB] * texelFetch(uSplineData, i+2).x;
                    dv2Point.x += uBasis[uB] * dv2Basis[vB] * texelFetch(uSplineData, i).x;
                    dv2Point.y += uBasis[uB] * dv2Basis[vB] * texelFetch(uSplineData, i+1).x;
                    dv2Point.z += uBasis[uB] * dv2Basis[vB] * texelFetch(uSplineData, i+2).x;
                    i += vN * 4;
                }}
                j += 4;
            }}

            vec3 normal = normalize(cross(duPoint, dvPoint));
            float intensity = dot(normal, uLightDirection);
            splineColor = (0.3 + 0.7 * abs(intensity)) * uSplineColor;
            gl_Position = uProjectionMatrix * point;
            EmitVertex();
            
            ComputeDelta(point, dvPoint, dv2Point, deltaV);
            
            point = vec4(0.0, 0.0, 0.0, 0.0);
            duPoint = vec3(0.0, 0.0, 0.0);
            dvPoint = vec3(0.0, 0.0, 0.0);
            dv2Point = vec3(0.0, 0.0, 0.0);
            j = header + uOrder + uN + vOrder + vN + (vM + 1 - vOrder) * 4;
            for (int vB = 0; vB < vOrder; vB++)
            {{
                int i = j + (uM + 1 - uOrder) * vN * 4;
                for (int uB = 0; uB < uOrder; uB++)
                {{
                    point.x += uBasisNext[uB] * vBasis[vB] * texelFetch(uSplineData, i).x;
                    point.y += uBasisNext[uB] * vBasis[vB] * texelFetch(uSplineData, i+1).x;
                    point.z += uBasisNext[uB] * vBasis[vB] * texelFetch(uSplineData, i+2).x;
                    point.w += uBasisNext[uB] * vBasis[vB] * texelFetch(uSplineData, i+3).x;
                    duPoint.x += duBasisNext[uB] * vBasis[vB] * texelFetch(uSplineData, i).x;
                    duPoint.y += duBasisNext[uB] * vBasis[vB] * texelFetch(uSplineData, i+1).x;
                    duPoint.z += duBasisNext[uB] * vBasis[vB] * texelFetch(uSplineData, i+2).x;
                    dvPoint.x += uBasisNext[uB] * dvBasis[vB] * texelFetch(uSplineData, i).x;
                    dvPoint.y += uBasisNext[uB] * dvBasis[vB] * texelFetch(uSplineData, i+1).x;
                    dvPoint.z += uBasisNext[uB] * dvBasis[vB] * texelFetch(uSplineData, i+2).x;
                    dv2Point.x += uBasisNext[uB] * dv2Basis[vB] * texelFetch(uSplineData, i).x;
                    dv2Point.y += uBasisNext[uB] * dv2Basis[vB] * texelFetch(uSplineData, i+1).x;
                    dv2Point.z += uBasisNext[uB] * dv2Basis[vB] * texelFetch(uSplineData, i+2).x;
                    i += vN * 4;
                }}
                j += 4;
            }}

            normal = normalize(cross(duPoint, dvPoint));
            intensity = dot(normal, uLightDirection);
            splineColor = (0.3 + 0.7 * abs(intensity)) * uSplineColor;
            gl_Position = uProjectionMatrix * point;
            EmitVertex();
            
            float newDeltaV = deltaV;
            ComputeDelta(point, dvPoint, dv2Point, newDeltaV);
            deltaV = min(newDeltaV, deltaV);
        }}

        void main()
        {{
            int uOrder = inData[0].uOrder;
            int vOrder = inData[0].vOrder;
            int uN = inData[0].uN;
            int vN = inData[0].vN;
            int uM = inData[0].uM;
            int vM = inData[0].vM;
            float firstU = inData[0].firstU;
            float lastU = inData[0].lastU;
            float u = firstU;
            int vertices = 0;
            int verticesPerU = 0;
            float uBasis[{maxBasis}];
            float duBasis[{maxBasis}];
            float du2Basis[{maxBasis}];

            splineColor = uSplineColor;
            ComputeBasis(header, uOrder, uN, uM, u, uBasis, duBasis, du2Basis);
            while (u < lastU && vertices < {maxVertices})
            {{
                // Calculate deltaU (min deltaU value over the comvex hull of v values)
                float deltaU = 0.5 * (lastU - firstU);
                int j = header + uOrder + uN + vOrder + vN + (vM + 1 - vOrder) * 4;
                for (int vB = 0; vB < vOrder; vB++)
                {{
                    vec4 point = vec4(0.0, 0.0, 0.0, 0.0);
                    vec3 duPoint = vec3(0.0, 0.0, 0.0);
                    vec3 du2Point = vec3(0.0, 0.0, 0.0);
                    int i = j + (uM + 1 - uOrder) * vN * 4;
                    for (int uB = 0; uB < uOrder; uB++)
                    {{
                        point.x += uBasis[uB] * texelFetch(uSplineData, i).x;
                        point.y += uBasis[uB] * texelFetch(uSplineData, i+1).x;
                        point.z += uBasis[uB] * texelFetch(uSplineData, i+2).x;
                        point.w += uBasis[uB] * texelFetch(uSplineData, i+3).x;
                        duPoint.x += duBasis[uB] * texelFetch(uSplineData, i).x;
                        duPoint.y += duBasis[uB] * texelFetch(uSplineData, i+1).x;
                        duPoint.z += duBasis[uB] * texelFetch(uSplineData, i+2).x;
                        du2Point.x += du2Basis[uB] * texelFetch(uSplineData, i).x;
                        du2Point.y += du2Basis[uB] * texelFetch(uSplineData, i+1).x;
                        du2Point.z += du2Basis[uB] * texelFetch(uSplineData, i+2).x;
                        i += vN * 4;
                    }}
                    float newDeltaU = deltaU;
                    ComputeDelta(point, duPoint, du2Point, newDeltaU);
                    deltaU = min(newDeltaU, deltaU);
                    j += 4;
                }}

                // If there's less than 8 vertices for the last row, force this to be the last row.
                verticesPerU = verticesPerU > 0 ? verticesPerU : 2 * int((lastU - u) / deltaU);
                //deltaU = vertices + verticesPerU + 8 <= {maxVertices} ? deltaU : 2.0 * (lastU - u);

                u = min(u + deltaU, lastU);
                float uBasisNext[{maxBasis}];
                float duBasisNext[{maxBasis}];
                float du2BasisNext[{maxBasis}];
                ComputeBasis(header, uOrder, uN, uM, u, uBasisNext, duBasisNext, du2BasisNext);

                float v = inData[0].firstV;
                float lastV = inData[0].lastV;
                float deltaV = 0.5 * (lastV - v);
                verticesPerU = 0;
                while (v < lastV && vertices <= {maxVertices} - 4) // Save room for the vertices at v and lastV
                {{
                    DrawSurfacePoints(uOrder, uN, uM, uBasis, duBasis, uBasisNext, duBasisNext,
                        vOrder, vN, vM, v, deltaV);
                    v = min(v + deltaV, lastV);
                    vertices += 2;
                    verticesPerU += 2;
                }}
                DrawSurfacePoints(uOrder, uN, uM, uBasis, duBasis, uBasisNext, duBasisNext,
                    vOrder, vN, vM, v, deltaV); //lastV, deltaV);
                vertices += 2;
                verticesPerU += 2;
                EndPrimitive();
                uBasis = uBasisNext;
                duBasis = duBasisNext;
                du2Basis = du2BasisNext;
            }}
        }}
    """

    fragmentShaderCode = """
        #version 410 core
     
        in vec3 splineColor;
        out vec3 color;
     
        void main()
        {
            color = splineColor;
        }
    """
 
    def __init__(self, *args, **kw):
        OpenGLFrame.__init__(self, *args, **kw)
        self.animate = 0 # Set to number of milliseconds before showing next frame (0 means no animation)
        self.splineDrawList = []
        self.currentQ = quat.one
        self.lastQ = quat.one
        self.origin = None
        self.bind("<ButtonPress-3>", self.Home)
        self.bind("<ButtonPress-1>", self.RotateStartHandler)
        self.bind("<ButtonRelease-1>", self.RotateEndHandler)
        self.bind("<B1-Motion>", self.RotateDragHandler)
        self.glInitialized = False

    def initgl(self):
        if not self.glInitialized:
            self.maxVertices = glGetIntegerv(GL_MAX_GEOMETRY_OUTPUT_VERTICES)
            #print("GL_VERSION: ", glGetString(GL_VERSION))
            #print("GL_SHADING_LANGUAGE_VERSION: ", glGetString(GL_SHADING_LANGUAGE_VERSION))
            #print("GL_MAX_GEOMETRY_OUTPUT_VERTICES: ", glGetIntegerv(GL_MAX_GEOMETRY_OUTPUT_VERTICES))
            #print("GL_MAX_GEOMETRY_TOTAL_OUTPUT_COMPONENTS: ", glGetIntegerv(GL_MAX_GEOMETRY_TOTAL_OUTPUT_COMPONENTS))
            #print("GL_MAX_TESS_GEN_LEVEL: ", glGetIntegerv(GL_MAX_TESS_GEN_LEVEL))

            try:
                self.computeBasisCode = self.computeBasisCode.format(maxBasis=Spline.maxOrder+1)

                self.curveGeometryShaderCode = self.curveGeometryShaderCode.format(maxVertices=self.maxVertices,
                    computeBasisCode=self.computeBasisCode,
                    computeDeltaCode=self.computeDeltaCode,
                    maxBasis=Spline.maxOrder+1)
                self.curveProgram = shaders.compileProgram(
                    shaders.compileShader(self.curveVertexShaderCode, GL_VERTEX_SHADER), 
                    shaders.compileShader(self.curveTCShaderCode, GL_TESS_CONTROL_SHADER), 
                    shaders.compileShader(self.curveTEShaderCode, GL_TESS_EVALUATION_SHADER), 
                    #shaders.compileShader(self.curveGeometryShaderCode, GL_GEOMETRY_SHADER), 
                    shaders.compileShader(self.fragmentShaderCode, GL_FRAGMENT_SHADER))
                
                self.surfaceGeometryShaderCode = self.surfaceGeometryShaderCode.format(maxVertices=self.maxVertices,
                    computeBasisCode=self.computeBasisCode,
                    computeDeltaCode=self.computeDeltaCode,
                    maxBasis=Spline.maxOrder+1)
                self.surfaceProgram = shaders.compileProgram(
                    shaders.compileShader(self.surfaceVertexShaderCode, GL_VERTEX_SHADER), 
                    shaders.compileShader(self.surfaceGeometryShaderCode, GL_GEOMETRY_SHADER), 
                    shaders.compileShader(self.fragmentShaderCode, GL_FRAGMENT_SHADER))
            except shaders.ShaderCompilationError as exception:
                error = exception.args[0]
                lineNumber = error.split(":")[3]
                source = exception.args[1][0]
                badLine = source.split(b"\n")[int(lineNumber)-1]
                shaderType = exception.args[2]
                print(shaderType, error)
                print(badLine)
                quit()

            self.splineDataBuffer = glGenBuffers(1)
            self.splineTextureBuffer = glGenTextures(1)
            glBindBuffer(GL_TEXTURE_BUFFER, self.splineDataBuffer)
            glBindTexture(GL_TEXTURE_BUFFER, self.splineTextureBuffer)
            glTexBuffer(GL_TEXTURE_BUFFER, GL_R32F, self.splineDataBuffer)
            maxFloats = 4 + 2 * Spline.maxKnots + 4 * Spline.maxCoefficients * Spline.maxCoefficients
            glBufferData(GL_TEXTURE_BUFFER, 4 * maxFloats, None, GL_STATIC_READ)

            self.parameterBuffer = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.parameterBuffer)
            glBufferData(GL_ARRAY_BUFFER, 4 * 4, np.array([0,0,0,0], np.float32), GL_STATIC_DRAW)

            glUseProgram(self.curveProgram)
            self.aCurveParameters = glGetAttribLocation(self.curveProgram, "aParameters")
            glBindBuffer(GL_ARRAY_BUFFER, self.parameterBuffer)
            glVertexAttribPointer(self.aCurveParameters, 4, GL_FLOAT, GL_FALSE, 0, None)
            self.uCurveProjectionMatrix = glGetUniformLocation(self.curveProgram, 'uProjectionMatrix')
            self.uCurveScreenScale = glGetUniformLocation(self.curveProgram, 'uScreenScale')
            self.uCurveSplineColor = glGetUniformLocation(self.curveProgram, 'uSplineColor')
            self.uCurveSplineData = glGetUniformLocation(self.curveProgram, 'uSplineData')
            glUniform1i(self.uCurveSplineData, 0) # 0 is the active texture (default is 0)

            glUseProgram(self.surfaceProgram)
            self.aSurfaceParameters = glGetAttribLocation(self.surfaceProgram, "aParameters")
            glBindBuffer(GL_ARRAY_BUFFER, self.parameterBuffer)
            glVertexAttribPointer(self.aSurfaceParameters, 4, GL_FLOAT, GL_FALSE, 0, None)
            self.uSurfaceProjectionMatrix = glGetUniformLocation(self.surfaceProgram, 'uProjectionMatrix')
            self.uSurfaceScreenScale = glGetUniformLocation(self.surfaceProgram, 'uScreenScale')
            self.uSurfaceSplineColor = glGetUniformLocation(self.surfaceProgram, 'uSplineColor')
            self.uSurfaceLightDirection = glGetUniformLocation(self.surfaceProgram, 'uLightDirection')
            self.lightDirection = np.array((0.6, 0.3, 1), np.float32)
            self.lightDirection = self.lightDirection / np.linalg.norm(self.lightDirection)
            glUniform3fv(self.uSurfaceLightDirection, 1, self.lightDirection)
            self.uSurfaceSplineData = glGetUniformLocation(self.surfaceProgram, 'uSplineData')
            glUniform1i(self.uSurfaceSplineData, 0) # 0 is the active texture (default is 0)

            glUseProgram(0)

            #glEnable( GL_DEPTH_TEST )
            #glClearColor(1.0, 1.0, 1.0, 0.0)
            glClearColor(0.0, 0.0, 0.0, 0.0)

            self.glInitialized = True

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        xExtent = self.width / self.height
        clipDistance = np.sqrt(3.0)
        zDropoff = 3.0
        near = zDropoff - clipDistance
        far = zDropoff + clipDistance
        top = clipDistance * near / zDropoff # Choose frustum that displays [-clipDistance,clipDistance] in y for z = -zDropoff
        glFrustum(-top*xExtent, top*xExtent, -top, top, near, far)
        glTranslate(0.0, 0.0, -zDropoff)
        #glOrtho(-xExtent, xExtent, -1.0, 1.0, -1.0, 1.0)

        self.projection = glGetFloatv(GL_PROJECTION_MATRIX)
        self.screenScale = np.array((0.5 * self.height * self.projection[0,0], 0.5 * self.height * self.projection[1,1], self.projection[3,3]), np.float32)
        glUseProgram(self.curveProgram)
        glUniformMatrix4fv(self.uCurveProjectionMatrix, 1, GL_FALSE, self.projection)
        glUniform3fv(self.uCurveScreenScale, 1, self.screenScale)
        glUseProgram(self.surfaceProgram)
        glUniformMatrix4fv(self.uSurfaceProjectionMatrix, 1, GL_FALSE, self.projection)
        glUniform3fv(self.uSurfaceScreenScale, 1, self.screenScale)
        glUseProgram(0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def redraw(self):

        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
        glLoadIdentity()
        rotation33 = quat.as_rotation_matrix(self.currentQ * self.lastQ)
        rotation44 = np.identity(4, np.float32)
        rotation44[0:3,0:3] = rotation33.T # Transpose to match OpenGL format in numpy
        transform = rotation44

        for spline in self.splineDrawList:
            spline.Draw(self, transform)

        glFlush()

    def Home(self, event):
        self.lastQ = quat.one
        self.currentQ = quat.one
        self.tkExpose(None)

    def ProjectToSphere(self, point):
        length = np.linalg.norm(point)
        if length <= 0.7071: # 1/sqrt(2)
            projection = np.array((point[0], point[1], np.sqrt(1.0 - length * length)), np.float32)
        else:
            projection = np.array((point[0], point[1], 0.5 / length), np.float32)
            projection = projection / np.linalg.norm(projection)
        return projection

    def RotateStartHandler(self, event):
        self.origin = np.array(((2.0 * event.x - self.width)/self.height, (self.height - 2.0 * event.y)/self.height), np.float32)

    def RotateDragHandler(self, event):
        if self.origin is not None:
            point = np.array(((2.0 * event.x - self.width)/self.height, (self.height - 2.0 * event.y)/self.height), np.float32)
            a = self.ProjectToSphere(self.origin)
            b = self.ProjectToSphere(point)
            dot = np.dot(a, b)
            halfCosine = np.sqrt(0.5 * (1.0 + dot))
            halfSine = np.sqrt(0.5 * (1.0 - dot))
            n = np.cross(a,b)
            if halfSine > 1.0e-8:
                n = (halfSine / np.linalg.norm(n)) * n
            self.currentQ = quat.from_float_array((halfCosine, n[0], n[1], n[2]))
            self.tkExpose(None)

    def RotateEndHandler(self, event):
        if self.origin is not None:
            self.lastQ = self.currentQ * self.lastQ
            self.currentQ = quat.one
            self.origin = None