from typing import Annotated, Any
from views import rasterize, view_types, ray_trace, camera
from mesh.mesh import Meshes
from enum import Enum
import numpy as np
import vedo


class Camera:
    pass


class Viewer:
    class Rendering(Enum):
        RAY_TRACE = 1
        RASTERIZE = 2

    class Perspective(Enum):
        ORTHOGRAPHIC = 1
        PERSPECTIVE = 2

    view_mode: Perspective = None
    render_mode: Rendering = Rendering.RASTERIZE

    cam: camera.Camera

    def change_view_mode(self,newView):
        print("in change view")
        if newView == 1:
            self.view_mode = self.Perspective.PERSPECTIVE
            print("changed to perspective")
        else:
            self.view_mode = self.Perspective.ORTHOGRAPHIC
            print("set to othro")

    def __init__(self, cam: camera.Camera | None = None):
        self.cam = camera.Camera()

        self.cam.set_position(np.array([0, 0, -10], dtype=np.float64))
        self.cam.set_focal_point(np.array([50, 40, 50], dtype=np.float64))

    def camera_transform(self,vertices,eye,gaze,up):
        gnorm = gaze/np.linalg.norm(gaze)
        w = -1*gnorm

        u = (np.cross(up,w))
        u = u/(np.linalg.norm(u))

        v = np.cross(w,u)

        M_cam = np.eye(4)
        M_cam [0:3,0:3] = [u,v,w]
        M_cam[0:3,3] = eye
        M_cam = np.linalg.inv(M_cam)
        print(M_cam)


        #transform = np.multiply(m1,m2)
        vertices = vertices.T
        new_vertices =np.ones([vertices.shape[0]+1, vertices.shape[1]])
        new_vertices[0:3,:] = vertices

        vertices_homo = np.matmul(M_cam,new_vertices)
        vertices_homo = vertices_homo.T
        return vertices_homo[:,:3]

    # Projection Transformation
    def project_vertices(self,vertices, projection_type, near=1, far=10):
    
        #assume r is 1 and l is -1
        r =1
        t =1
        l =-1
        b=-1
        M = np.array([
            [1/(r-l), 0,0, 0],
            [0,1/(t-b),0,0],
            [0,0,2/(near-far),-(near+far)/(far-near)],
            [0,0,0,1]
            ])

        if projection_type == "perspective":
            #performs a perspective projection type
            M = np.array([
            [near,0,0,0],
            [0,near,0,0],
            [0,0,near + far, -near*far],
            [0,0,1,0]
            ])
  
        vp_vertices = np.hstack((vertices,np.ones([len(vertices),1]))) #appending a 1 to the end of each point for proper sizing    
        res_pts = vp_vertices @M.T

        if projection_type == "perspective":
            res_pts[:,0] = res_pts[:,0]/res_pts[:,3]
            res_pts[:,1] = res_pts[:,1]/res_pts[:,3]
            res_pts[:,2] = res_pts[:,2]/res_pts[:,3]

        return res_pts[:,0:3]
    
    def viewport_transform(self,vertices, width, height):
        print(vertices)
        Mvp = np.array([
            [width/2,0,0,(width-1)/2],
            [0, height/2,0,(height-1)/2],
            [0,0,1,0],
            [0,0,0,1]
        ])

        vp_vertices = np.hstack((vertices,np.ones([len(vertices),1]))) #appending a 1 to the end of each point for proper sizing
        res_pts = Mvp @ vp_vertices.T #transposing the vertices so the matrix multiplication is correct

        res = res_pts[:2,:] #only getting points from the matrix
        print(res)
        return res.T

    def render(
        self,
        display: view_types.Display,
        meshes: Meshes,
    ) -> view_types.Raster:
        
        print(self.view_mode) #testing print

        if self.view_mode == self.Perspective.ORTHOGRAPHIC:
            print("in ortho")
            up = np.array([0,1,0])
            gaze = self.cam.get_focal_point()
            eye = self.cam.get_position()
            
            for key in meshes.meshes:
                curmesh = meshes.meshes[key]
                vertices = curmesh.vertices
                faces = curmesh.cells
                color = curmesh.color()

                #camera transform
                transformed_vertices = self.camera_transform(vertices,eye,gaze,up)

                #projection transformation 
                perspective_vertices = self.project_vertices(transformed_vertices,"orhtographic", near= 1, far=10)               

                #viewport transformation
                final_transform = self.viewport_transform(perspective_vertices, display.width,display.height)

                curmesh = vedo.Mesh([final_transform,faces], c=vedo.colors.get_color(color))
            return rasterize.render(display,meshes,self.cam)
        
        if self.view_mode == self.Perspective.PERSPECTIVE:
            print("in perspective")
            up = np.array([0,1,0])
            gaze = self.cam.get_focal_point()
            eye = self.cam.get_position()
            
            for key in meshes.meshes:
                curmesh = meshes.meshes[key]
                vertices = curmesh.vertices
                faces = curmesh.cells
                color = curmesh.color()

                #camera transform
                transformed_vertices = self.camera_transform(vertices,eye,gaze,up)

                #projection transformation 
                perspective_vertices = self.project_vertices(transformed_vertices,"perspective", near= 1, far=10)               

                #viewport transformation
                final_transform = self.viewport_transform(perspective_vertices, display.width,display.height)

                curmesh = vedo.Mesh([final_transform,faces], c=vedo.colors.get_color(color))

            return rasterize.render(display,meshes,self.cam)
        
        if self.render_mode == self.Rendering.RASTERIZE:
            print('rasterize')
            return rasterize.render(display, meshes, self.cam)
        if self.render_mode == self.Rendering.RAY_TRACE:
            return ray_trace.render(display, meshes, self.cam)
        return np.random.randint(0, 255, size=(display.width, display.height, 3), dtype=np.uint8)

    def rotate_cam(self, vert: np.float64, hori: np.float64) -> None:
        vert = np.deg2rad(vert)
        hori = np.degrees(hori)

        cam_coords = self.cam.get_position()
        if cam_coords is None:
            return
        focal_point = self.cam.get_focal_point()
        if focal_point is not None:
            cam_coords -= focal_point

        cv = np.cos(vert)
        sv = np.sin(vert)
        vert_rot = np.array(
            [
                [cv, 0, sv],
                [0, 1, 0],
                [-sv, 0, cv],
            ],
            dtype=np.float64,
        )

        cam_coords = np.dot(vert_rot, cam_coords)

        ch = np.cos(hori)
        sh = np.sin(hori)
        hori_rot = np.array(
            [
                [ch, sh, 0],
                [-sh, ch, 0],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

        cam_coords = np.dot(hori_rot, cam_coords)

        if focal_point is not None:
            cam_coords += focal_point
        self.cam.set_position(cam_coords)

    def zoom_cam(self, factor: np.float64) -> None:
        factor = 1 + factor / 100
        cam_coords = self.cam.get_position()
        if cam_coords is None:
            return
        focal_point = self.cam.get_focal_point()
        if focal_point is not None:
            cam_coords -= focal_point

        cam_coords *= factor

        if focal_point is not None:
            cam_coords += focal_point
        self.cam.set_position(cam_coords)
