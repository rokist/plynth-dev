import os
import math
import plynth
import plynth.js as js


document, window, console = js.document, js.window, js.console
three = js.THREE

#if not 'esmod' in globals():
esmod = js.esmod

esmodImportPromise = js.esImport( {
    "jsm/controls/OrbitControls.js": ["OrbitControls"],
    "jsm/geometries/ConvexGeometry.js": ["ConvexBufferGeometry"]
});


async def main():
    await esmodImportPromise
    CalcApp()


class CalcApp:
    def __init__(self):
        self.setup()
        self.animate()

    def setup(self):
        # https://github.com/mrdoob/three.js/blob/master/examples/webgl_geometry_convex.html

        self.scene = three.Scene();

        self.renderer = three.WebGLRenderer( { "antialias": True } );
        self.renderer.setPixelRatio( window.devicePixelRatio );
        self.renderer.setSize( window.innerWidth, window.innerHeight );
        document.body.appendChild( self.renderer.domElement );

        # camera
        self.camera = three.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 1000 );
        self.camera.position.set( 15, 20, 30 );
        self.scene.add( self.camera );

        # controls
        controls = esmod.OrbitControls( self.camera, self.renderer.domElement );
        controls.minDistance = 20;
        controls.maxDistance = 50;
        controls.maxPolarAngle = math.pi / 2;

        self.scene.add( three.AmbientLight( 0x222222 ) );

        # light
        light = three.PointLight( 0xffffff, 0.6 );
        self.camera.add( light );

        #helper
        self.scene.add( three.AxesHelper( 20 ) );

        #textures
        loader = three.TextureLoader();
        texture = loader.load( 'textures/sprites/disc.png' );

        self.group = three.Group();
        self.scene.add( self.group );


        #points
        vertices = three.DodecahedronGeometry( 10 ).vertices;
        #for ( var i = 0; i < vertices.length; i ++ ) {
        #        //vertices[ i ].add( randomPoint().multiplyScalar( 2 ) ); // wiggle the points
        #}

        pointsMaterial = three.PointsMaterial( {
            "color": 0x0080ff,
            "map": texture,
            "size": 1,
            "alphaTest": 0.5
        });

        pointsGeometry = three.BufferGeometry().setFromPoints(vertices);

        points = three.Points(pointsGeometry, pointsMaterial);
        self.group.add(points);

        #convex hull
        meshMaterial = three.MeshLambertMaterial({
            "color": 0xffffff,
            "opacity": 0.4,
            "transparent": True
        });


        meshGeometry = esmod.ConvexBufferGeometry( vertices );

        mesh = three.Mesh(meshGeometry, meshMaterial );
        mesh.material.side = three.BackSide; # // back faces
        mesh.renderOrder = 0;
        self.group.add(mesh);

        mesh = three.Mesh(meshGeometry, meshMaterial.clone());
        mesh.material.side = three.FrontSide; # // front faces
        mesh.renderOrder = 1;

        self.group.add(mesh);


    def animate(self):

        js.requestAnimationFrame( self.animate );

        self.group.rotation.y += 0.005;

        self.render();


    def render(self):
        self.renderer.render( self.scene, self.camera );

