import * as THREE from 'three';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const stage = document.querySelector('#model-stage');
const host = document.querySelector('#canvas-host');
const status = document.querySelector('#load-message');
const fieldset = document.querySelector('#viewer-controls');
const download = 'assets/models/rehearsal-nook.glb?v=approved-layout-1';

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
  document.querySelector('#object-select').disabled = true;
  document.querySelector('#object-controls').disabled = true;
  document.querySelectorAll('.history-buttons button').forEach(button => { button.disabled = true; });
}

try {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.tabIndex = 0;
  renderer.domElement.setAttribute('aria-label', 'Interactive rehearsal nook. Click an object to select it. Use W to move, E to rotate, R to scale, Q for global or local axes. Drag empty space to orbit, scroll to zoom. Arrow keys pan.');
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

  // Operate on the model's named asset roots, never on faces, lights or helpers.
  const transform = new TransformControls(camera, renderer.domElement);
  transform.setSize(.85);
  scene.add(transform.getHelper());
  const objectSelect = document.querySelector('#object-select');
  const objectFields = document.querySelector('#object-controls');
  const spaceSelect = document.querySelector('#transform-space');
  const numericFields = [...document.querySelectorAll('[data-transform]')];
  const objects = [], original = new Map(), spaces = new Map();
  let selected = null, selectionBox = null, beforeDrag = null;
  const undoStack = [], redoStack = [];
  const snapshot = () => objects.map(object => ({ object, position: object.position.clone(), quaternion: object.quaternion.clone(), scale: object.scale.clone() }));
  function historyButtons() {
    document.querySelector('#undo-transform').disabled = !undoStack.length;
    document.querySelector('#redo-transform').disabled = !redoStack.length;
  }
  function remember(before) {
    const changed = before.some(({ object, position, quaternion, scale }) => !object.position.equals(position) || !object.quaternion.equals(quaternion) || !object.scale.equals(scale));
    if (!changed) return;
    undoStack.push(before);
    if (undoStack.length > 100) undoStack.shift();
    redoStack.length = 0;
    historyButtons();
  }
  function syncFields() {
    if (!selected) return;
    const rotation = new THREE.Euler().setFromQuaternion(selected.quaternion, 'XYZ');
    for (const input of numericFields) {
      const vector = input.dataset.transform === 'rotation' ? rotation : selected[input.dataset.transform];
      const value = input.dataset.transform === 'rotation' ? THREE.MathUtils.radToDeg(vector[input.dataset.axis]) : vector[input.dataset.axis];
      input.value = String(Number(value.toFixed(3)));
    }
    selected.updateMatrixWorld(true);
    selectionBox?.update();
  }
  function stopRotation() {
    controls.autoRotate = false;
    const button = document.querySelector('#rotation');
    button.setAttribute('aria-pressed', 'false');
    button.querySelector('span').textContent = '○';
  }
  function selectObject(object) {
    if (transform.dragging) return;
    if (selectionBox) { scene.remove(selectionBox); selectionBox.geometry.dispose(); selectionBox.material.dispose(); selectionBox = null; }
    selected = object;
    objectFields.disabled = !object;
    objectSelect.value = object ? String(objects.indexOf(object)) : '';
    if (!object) {
      transform.detach();
      document.querySelector('#selection-status').textContent = 'Click the model or choose an object above.';
      return;
    }
    stopRotation();
    transform.attach(object);
    transform.setSpace(spaces.get(object) || 'world');
    spaceSelect.value = transform.space;
    selectionBox = new THREE.BoxHelper(object, 0xad7023);
    selectionBox.material.depthTest = false;
    selectionBox.renderOrder = 999;
    scene.add(selectionBox);
    document.querySelector('#selection-status').textContent = objectSelect.selectedOptions[0].textContent;
    syncFields();
  }
  function setTool(mode) {
    transform.setMode(mode);
    document.querySelectorAll('[data-tool]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.tool === mode)));
  }
  function setSpace(space) {
    if (!selected) return;
    spaces.set(selected, space);
    spaceSelect.value = space;
    transform.setSpace(space);
  }
  function restore(state) {
    for (const { object, position, quaternion, scale } of state) { object.position.copy(position); object.quaternion.copy(quaternion); object.scale.copy(scale); object.updateMatrixWorld(true); }
    syncFields(); historyButtons();
  }
  function undo() { if (transform.dragging || !undoStack.length) return; redoStack.push(snapshot()); restore(undoStack.pop()); }
  function redo() { if (transform.dragging || !redoStack.length) return; undoStack.push(snapshot()); restore(redoStack.pop()); }
  transform.addEventListener('dragging-changed', event => { controls.enabled = !event.value; });
  transform.addEventListener('mouseDown', () => { beforeDrag = snapshot(); stopRotation(); });
  transform.addEventListener('mouseUp', () => { if (beforeDrag) remember(beforeDrag); beforeDrag = null; syncFields(); });
  transform.addEventListener('objectChange', () => {
    if (selected && transform.mode === 'scale') for (const axis of ['x', 'y', 'z']) selected.scale[axis] = Math.max(.01, selected.scale[axis]);
    syncFields();
  });
  objectSelect.addEventListener('change', () => selectObject(objectSelect.value === '' ? null : objects[Number(objectSelect.value)]));
  document.querySelectorAll('[data-tool]').forEach(button => button.addEventListener('click', () => setTool(button.dataset.tool)));
  spaceSelect.addEventListener('change', () => setSpace(spaceSelect.value));
  document.querySelector('#transform-snap').addEventListener('change', event => {
    transform.setTranslationSnap(event.target.checked ? .1 : null);
    transform.setRotationSnap(event.target.checked ? Math.PI / 12 : null);
    transform.setScaleSnap(event.target.checked ? .1 : null);
  });
  for (const input of numericFields) {
    let beforeEdit = null, dirty = false;
    const applyValue = () => {
      if (!selected || input.value.trim() === '') return;
      const value = input.valueAsNumber, axis = input.dataset.axis;
      if (!Number.isFinite(value) || (input.dataset.transform === 'scale' && (value < .01 || value > 100))) return;
      if (!beforeEdit) beforeEdit = snapshot();
      if (input.dataset.transform === 'rotation') {
        const euler = new THREE.Euler().setFromQuaternion(selected.quaternion, 'XYZ');
        euler[axis] = THREE.MathUtils.degToRad(value); selected.quaternion.setFromEuler(euler);
      } else selected[input.dataset.transform][axis] = value;
      selected.updateMatrixWorld(true); selectionBox?.update();
    };
    const finishEdit = () => { if (dirty) { applyValue(); if (beforeEdit) remember(beforeEdit); } beforeEdit = null; dirty = false; syncFields(); };
    input.addEventListener('focus', () => { beforeEdit = snapshot(); dirty = false; });
    input.addEventListener('input', () => { dirty = true; applyValue(); });
    input.addEventListener('change', () => { dirty = true; finishEdit(); });
    input.addEventListener('blur', finishEdit);
  }
  document.querySelector('#reset-object').addEventListener('click', () => {
    if (!selected) return;
    const before = snapshot(); restore([original.get(selected)]); remember(before);
  });
  document.querySelector('#reset-layout').addEventListener('click', () => { const before = snapshot(); restore([...original.values()]); remember(before); });
  document.querySelector('#undo-transform').addEventListener('click', undo);
  document.querySelector('#redo-transform').addEventListener('click', redo);
  const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
  let pointerStart = null;
  renderer.domElement.addEventListener('pointerdown', event => {
    if (event.button !== 0 || !event.isPrimary) { pointerStart = null; return; }
    pointerStart = { x: event.clientX, y: event.clientY, id: event.pointerId, gizmo: transform.dragging || Boolean(transform.axis) };
  });
  renderer.domElement.addEventListener('pointercancel', () => { pointerStart = null; });
  renderer.domElement.addEventListener('pointerup', event => {
    const start = pointerStart; pointerStart = null;
    if (!start || start.id !== event.pointerId || start.gizmo || transform.dragging || Math.hypot(event.clientX - start.x, event.clientY - start.y) > 5) return;
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.set((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(objects, true)[0];
    let object = hit?.object;
    while (object && !objects.includes(object)) object = object.parent;
    selectObject(object || null);
  });
  document.querySelector('.model-workspace').addEventListener('keydown', event => {
    if (event.target.matches('input, select, textarea') || event.target.isContentEditable) return;
    const key = event.key.toLowerCase();
    if ((event.ctrlKey || event.metaKey) && key === 'z') { event.preventDefault(); event.shiftKey ? redo() : undo(); return; }
    if (key === 'escape') { if (transform.dragging) transform.reset(); else selectObject(null); return; }
    if (!selected || event.ctrlKey || event.metaKey || event.altKey || transform.dragging) return;
    const modes = { w: 'translate', e: 'rotate', r: 'scale' };
    if (modes[key]) { event.preventDefault(); setTool(modes[key]); }
    if (key === 'q') { event.preventDefault(); setSpace(transform.space === 'world' ? 'local' : 'world'); }
  });

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
    for (const object of model.children) {
      if (!object.isMesh && !object.getObjectByProperty('isMesh', true)) continue;
      objects.push(object);
    }
    objects.sort((a, b) => a.name.localeCompare(b.name));
    for (const [index, object] of objects.entries()) {
      const option = document.createElement('option'); option.value = String(index);
      option.textContent = object.name.replace(/^\d+_/, '').replaceAll('_', ' ');
      objectSelect.append(option);
      original.set(object, { object, position: object.position.clone(), quaternion: object.quaternion.clone(), scale: object.scale.clone() });
      spaces.set(object, object.userData.vrhsTransformSpace === 'local' ? 'local' : 'world');
    }
    objectSelect.disabled = false;
    document.querySelector('#reset-layout').disabled = false;
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
