import os
import plynth
import plynth.js as js


document, window, console = js.document, js.window, js.console
three = js.THREE

class CalcApp:
    def __init__(self):
        console.info(three)
        scene = three.Scene();

        renderer = three.WebGLRenderer( { "antialias": True } );
        renderer.setPixelRatio( window.devicePixelRatio );
        renderer.setSize( window.innerWidth, window.innerHeight );
        document.body.appendChild( renderer.domElement );


        # camera
        camera = three.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 1000 );
        camera.position.set( 15, 20, 30 );
        scene.add( camera );

        # controls
        controls = js.OrbitControls( camera, renderer.domElement );
        controls.minDistance = 20;
        controls.maxDistance = 50;
        controls.maxPolarAngle = js.Math.PI / 2;

        scene.add( three.AmbientLight( 0x222222 ) );

        console.info(controls)
