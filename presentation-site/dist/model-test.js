import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const stage = document.querySelector('#model-stage');
const host = document.querySelector('#canvas-host');
const status = document.querySelector('#load-message');
const fieldset = document.querySelector('#viewer-controls');
const download = 'assets/models/rehearsal-nook.glb';

function fail(message) {
  stage.setAttribute('aria-busy', 'false');
  stage.dataset.state = 'error';
  status.hidden = false;
  status.replaceChildren(document.createTextNode(message + ' '));
  const link = document.createElement('a');
  link.href = download;
  link.download = 'rehearsal-nook.glb';
  link.textContent = 'Download the model instead.';
  status.append(link);
  fieldset.disabled = true;
}

try {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.tabIndex = 0;
  renderer.domElement.setAttribute('aria-label', 'Interactive rehearsal nook. Drag to rotate, scroll to zoom, or use the viewpoint buttons. Arrow keys pan.');
  host.append(renderer.domElement);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e5dfd1');
  const camera = new THREE.PerspectiveCamera(36, 1, .05, 100);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = .08;
  controls.minDistance = 3;
  controls.maxDistance = 24;
  controls.maxPolarAngle = Math.PI * .49;
  controls.autoRotateSpeed = .45;
  controls.listenToKeyEvents(renderer.domElement);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, .04);
  scene.environment = environment.texture;
  scene.environmentIntensity = .5;
  room.dispose();
  pmrem.dispose();
  const ambient = new THREE.HemisphereLight(0xdce8ff, 0x70573d, 1.2);
  scene.add(ambient);
  const key = new THREE.DirectionalLight(0xffddb0, 3);
  key.position.set(-3, 8, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -5, right: 5, top: 6, bottom: -5, near: .1, far: 24 });
  key.shadow.normalBias = .035;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xc8dcff, 1.2);
  fill.position.set(5, 4, 2);
  scene.add(fill);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ color: 0x514334, opacity: .16 }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -.26;
  ground.receiveShadow = true;
  scene.add(ground);
  let model, center = new THREE.Vector3(0, 1.65, 0), wireframe = false;
  const views = { corner: new THREE.Vector3(9, 7, 11), front: new THREE.Vector3(0, 4.5, 14), above: new THREE.Vector3(6.5, 12, 8) };
  let selectedView = 'corner';
  function setView(name) {
    selectedView = name;
    // Increase camera distance on narrow screens so the full floor fits.
    const scale = Math.max(1, .95 / camera.aspect);
    controls.target.copy(center);
    camera.position.copy(center).addScaledVector(views[name], scale);
    controls.maxDistance = Math.max(24, camera.position.distanceTo(center) * 1.5);
    controls.update();
    document.querySelectorAll('[data-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === name)));
  }
  function resize() {
    const { width, height } = host.getBoundingClientRect();
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }
  const observer = new ResizeObserver(() => { resize(); if (model) setView(selectedView); });
  observer.observe(host);
  resize();
  setView('corner');
  const presets = {
    warm: [0xffddb0, 0xc8dcff, 3, 1.2, 1.1],
    neutral: [0xffffff, 0xffffff, 2.6, 1.4, 1],
    cool: [0xd3e6ff, 0xb8ceff, 2.6, 1.5, 1.05]
  };
  document.querySelector('#lighting').addEventListener('change', event => {
    const [a, b, c, d, e] = presets[event.target.value];
    key.color.setHex(a); fill.color.setHex(b); key.intensity = c; fill.intensity = d; renderer.toneMappingExposure = e;
  });
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
  document.querySelector('#reset-view').addEventListener('click', () => setView('corner'));
  document.querySelector('#wireframe').addEventListener('click', event => {
    wireframe = !wireframe;
    model.traverse(object => { if (object.isMesh) for (const material of (Array.isArray(object.material) ? object.material : [object.material])) material.wireframe = wireframe; });
    event.currentTarget.setAttribute('aria-pressed', String(wireframe));
    event.currentTarget.querySelector('span').textContent = wireframe ? '●' : '○';
  });
  document.querySelector('#rotation').addEventListener('click', event => {
    controls.autoRotate = !controls.autoRotate;
    event.currentTarget.setAttribute('aria-pressed', String(controls.autoRotate));
    event.currentTarget.querySelector('span').textContent = controls.autoRotate ? '●' : '○';
  });
  renderer.domElement.addEventListener('webglcontextlost', event => {
    event.preventDefault(); renderer.setAnimationLoop(null); fail('The 3D view was interrupted. Reload this page to try again.');
  });
  new GLTFLoader().load(download, gltf => {
    model = gltf.scene;
    model.traverse(object => { if (object.isMesh) { object.castShadow = true; object.receiveShadow = true; } });
    scene.add(model);
    new THREE.Box3().setFromObject(model).getCenter(center);
    setView('corner');
    status.hidden = true;
    document.querySelector('#model-poster').hidden = true;
    stage.setAttribute('aria-busy', 'false');
    stage.dataset.state = 'loaded';
    fieldset.disabled = false;
  }, progress => {
    if (progress.total) document.querySelector('#load-percent').textContent = Math.round(progress.loaded / progress.total * 100) + '%';
  }, error => { console.error('Model could not load', error); fail('The 3D model could not load. Please reload to try again.'); });
  let visible = true;
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; }).observe(stage);
  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const delta = Math.min(clock.getDelta(), .05);
    if (document.hidden || !visible) return;
    controls.update(delta);
    renderer.render(scene, camera);
  });
} catch (error) {
  console.error('Viewer initialization failed', error);
  fail('Interactive 3D is unavailable in this browser.');
}
