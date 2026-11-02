import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const host = document.querySelector('#character-model-canvas');
const status = document.querySelector('#character-model-status');
const buttons = document.querySelector('#character-model-controls');
let started = false;

async function start() {
  if (started) return;
  started = true;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    renderer.toneMapping = THREE.NeutralToneMapping;
    renderer.toneMappingExposure = 1;
    const canvas = renderer.domElement;
    canvas.tabIndex = 0;
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', 'Interactive Goblin teacher model. Drag or use arrow keys to rotate; scroll or use plus and minus to zoom.');
    canvas.setAttribute('aria-describedby', 'character-model-help');
    host.prepend(canvas);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#e8e7e3');
    const camera = new THREE.PerspectiveCamera(35, 1, .001, 1000);
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.autoRotateSpeed = .7;
    const pmrem = new THREE.PMREMGenerator(renderer);
    const room = new RoomEnvironment();
    const environment = pmrem.fromScene(room, .04);
    scene.environment = environment.texture;
    scene.environmentIntensity = .35;
    room.dispose();
    pmrem.dispose();
    scene.add(new THREE.HemisphereLight(0xffffff, 0xaaaaaa, 1));
    const key = new THREE.DirectionalLight(0xffffff, 2);
    key.position.set(3, 5, 4);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xffffff, .7);
    fill.position.set(-3, 2, -2);
    scene.add(fill);
    let inView = true;
    let home = new THREE.Vector3();
    function resize() {
      const width = host.clientWidth, height = host.clientHeight;
      if (!width || !height) return;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    }
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);
    resize();
    const gltf = await new GLTFLoader().loadAsync('assets/models/goblin-teacher-test.glb', event => {
      status.textContent = event.total ? `Loading character · ${Math.round(event.loaded / event.total * 100)}%` : 'Loading character…';
    });
    const model = gltf.scene;
    const box = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3());
    model.position.sub(box.getCenter(new THREE.Vector3()));
    scene.add(model);
    const radius = size.length() / 2;
    const distance = radius / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.1;
    camera.near = Math.max(radius / 1000, .0001);
    camera.far = radius * 100;
    home.set(0, size.y * .04, distance);
    camera.position.copy(home);
    camera.updateProjectionMatrix();
    controls.minDistance = radius * .65;
    controls.maxDistance = distance * 2.5;
    controls.update();
    status.hidden = true;
    host.setAttribute('aria-busy', 'false');
    buttons.disabled = false;
    const rotate = document.querySelector('#character-model-rotate');
    rotate.addEventListener('click', () => {
      controls.autoRotate = !controls.autoRotate;
      rotate.setAttribute('aria-pressed', String(controls.autoRotate));
      rotate.textContent = controls.autoRotate ? 'Pause rotation' : 'Auto-rotate';
    });
    document.querySelector('#character-model-reset').addEventListener('click', () => {
      controls.autoRotate = false;
      rotate.setAttribute('aria-pressed', 'false');
      rotate.textContent = 'Auto-rotate';
      camera.position.copy(home);
      controls.target.set(0, 0, 0);
      controls.update();
    });
    canvas.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-'].includes(event.key)) return;
      event.preventDefault();
      const spherical = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
      if (event.key === 'ArrowLeft') spherical.theta -= .12;
      if (event.key === 'ArrowRight') spherical.theta += .12;
      if (event.key === 'ArrowUp') spherical.phi -= .12;
      if (event.key === 'ArrowDown') spherical.phi += .12;
      if (event.key === '+' || event.key === '=') spherical.radius *= .9;
      if (event.key === '-') spherical.radius *= 1.1;
      spherical.radius = THREE.MathUtils.clamp(spherical.radius, controls.minDistance, controls.maxDistance);
      spherical.makeSafe();
      camera.position.setFromSpherical(spherical).add(controls.target);
      controls.update();
    });
    new IntersectionObserver(entries => { inView = entries[0].isIntersecting; }).observe(host);
    renderer.setAnimationLoop(() => {
      if (!inView || document.hidden) return;
      controls.update();
      renderer.render(scene, camera);
    });
    canvas.addEventListener('webglcontextlost', event => {
      event.preventDefault();
      status.hidden = false;
      status.textContent = 'The 3D view was interrupted. Reload the page or download the model below.';
      buttons.disabled = true;
    });
  } catch (error) {
    renderer?.dispose();
    status.hidden = false;
    status.textContent = 'The 3D preview could not load. You can download the model below.';
    host.setAttribute('aria-busy', 'false');
    console.error('Character preview:', error);
  }
}

new IntersectionObserver((entries, observer) => {
  if (entries.some(entry => entry.isIntersecting)) {
    observer.disconnect();
    start();
  }
}, { rootMargin: '200px' }).observe(host);
