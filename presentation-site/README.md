# VRHS presentation website

This is a normal folder in aklein00/VRSchool, not a separate Git repository. Make website changes and commit them through the main VRSchool repository. Do not initialize a nested repository here.

## Vercel settings

- Repository: aklein00/VRSchool
- Root Directory: presentation-site
- Framework/Application Preset: Other
- Build Command: empty
- Output Directory: dist
- Install Command: empty
- Environment variables: none for this placeholder

Only dist is served as the website. It contains six HTML pages, shared CSS/JavaScript and selected compressed concept images, including portrait derivatives for the voice gallery. Keep original artwork, research, workflows, voice assignments, secrets and project documents outside dist. Do not change the output directory to the VRSchool root.

## Pages

Pitch; Art Style Guide (eight disciplines); Prototypes; Design; Product; First Lessons. Prototypes features Unit 1.1: Acoustical Awareness & The Anatomy of Sound, with Soundscape Mapping, the Timbre Experiment and expandable explanations for the understanding checks. First Lessons is a supporting page linked from Prototypes and Design, with descriptions for the other faculty. The earlier rhythm sequencer has been replaced. The production case study supports the pitch. Pending models, scenes and recordings are labeled.

## Temporary preview

An earlier owner-private Sites preview is available separately. Its published content remains unchanged. Vercel and aklein00/VRSchool are the intended ongoing deployment route; do not recreate a nested Git repository for that old preview.

## Audio

Prototypes includes 14 short faculty clips for 13 teachers, with separate Ettin Head A and Head B players. The selected MP3s are served from `dist/assets/audio/`; each has a transcript and download link. Playback works without an ElevenLabs account or runtime API calls. Starting a clip pauses the other gallery clips. Student voice studies remain planned.

The four instrument-comparison recordings for the Music lesson are separate from the character voices and remain to be added. Production scripts, voice assignments, archives and speech-review results stay in `production/audio/`, outside the website output.

## Candid illustrations · October 30, 2026

The pitch hero uses the original hatless Goblin Bard teaching flute and drum. The Art Style Guide opens with nonbinary Oobleck painting with two students; Design adds a Chuul science demonstration banner. Product uses an unlabeled three-style headmaster comparison. The repeated Goblin image in the pending 3D-model section is replaced by a model-study placeholder; the lesson and voice portraits remain for identification.

Full-resolution masters are in `../assets/concepts/2026-10-30/website/`. Served WebP copies are in `dist/assets/candid/`. Generation prompts and reference paths are recorded in `../docs/art/website-candid-image-prompts.json`. Images were generated with the built-in image tool and reviewed in desktop and mobile layouts. Prior concept masters are preserved. No live deployment was made as part of this local artwork update.

## 3D model test page

`dist/model-test.html` is linked from the music-workshop section of Prototypes. It displays the assembled rehearsal nook as a self-contained GLB with camera presets, orbit/pan/zoom, lighting choices, wireframe, reset and optional rotation. Keyboard users can tab to the canvas and use arrow keys to pan, or use the labeled viewpoint buttons. A poster, loading status, model download and explicit error state support slower connections or unavailable WebGL.

The served model is `dist/assets/models/rehearsal-nook.glb` (37 meshes, 82,772 triangles, approximately 18 MB), exported from the local Blender scene. All model textures are embedded. `dist/assets/vendor/three/` contains the required MIT-licensed Three.js 0.181.1 files from the official npm package, including its license. The viewer has no runtime CDN dependency and requires no build step. Serve `dist` over HTTP to preview; browser modules do not run from a file URL. The browser lighting is arranged separately from the Blender render.
