// Apply a captured object-editor layout to a GLB while preserving its mesh and texture bytes.
import { readFileSync, writeFileSync } from 'node:fs';
import { Euler, Quaternion, MathUtils } from '../dist/assets/vendor/three/build/three.core.js';
const asset = new URL('../dist/assets/models/rehearsal-nook.glb', import.meta.url);
const layout = JSON.parse(readFileSync(new URL('../dist/assets/models/rehearsal-nook-layout.json', import.meta.url)));
const bytes = readFileSync(asset);
if (bytes.readUInt32LE(0) !== 0x46546c67 || bytes.readUInt32LE(4) !== 2) throw new Error('Expected GLB 2.0');
const chunks = [];
for (let offset = 12; offset < bytes.length;) {
  const length = bytes.readUInt32LE(offset), type = bytes.readUInt32LE(offset + 4);
  chunks.push({ type, data: bytes.subarray(offset + 8, offset + 8 + length) });
  offset += 8 + length;
}
const jsonChunk = chunks.find(chunk => chunk.type === 0x4e4f534a);
const gltf = JSON.parse(jsonChunk.data.toString());
const names = new Set();
for (const value of layout.objects) {
  const node = gltf.nodes.find(node => node.name === value.name);
  if (!node || names.has(value.name)) throw new Error(`Missing or duplicate object: ${value.name}`);
  for (const vector of [value.position, value.rotationDegrees, value.scale]) if (vector.length !== 3 || !vector.every(Number.isFinite)) throw new Error('Invalid transform');
  if (value.scale.some(n => n <= 0)) throw new Error('Scale must be positive');
  names.add(value.name);
  node.translation = value.position;
  node.rotation = new Quaternion().setFromEuler(new Euler(...value.rotationDegrees.map(MathUtils.degToRad), 'XYZ')).toArray();
  node.scale = value.scale;
  node.extras = { ...node.extras, vrhsTransformSpace: value.space };
  delete node.matrix;
}
const json = Buffer.from(JSON.stringify(gltf));
jsonChunk.data = Buffer.concat([json, Buffer.alloc((4 - json.length % 4) % 4, 0x20)]);
const header = Buffer.alloc(12); header.writeUInt32LE(0x46546c67); header.writeUInt32LE(2, 4);
header.writeUInt32LE(12 + chunks.reduce((sum, chunk) => sum + chunk.data.length + 8, 0), 8);
writeFileSync(asset, Buffer.concat([header, ...chunks.flatMap(chunk => { const h = Buffer.alloc(8); h.writeUInt32LE(chunk.data.length); h.writeUInt32LE(chunk.type, 4); return [h, chunk.data]; })]));
console.log(`Saved ${names.size} approved object transforms; mesh and texture binary data preserved.`);
