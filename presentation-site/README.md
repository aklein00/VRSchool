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

The pitch hero uses the new Goblin-and-Yeti classroom key art beside “The Monsters are the Teachers.” The original hatless Goblin Bard teaching flute and drum is preserved among the candid assets. The Art Style Guide opens with nonbinary Oobleck painting with two students; Design adds a Chuul science demonstration banner. Product uses an unlabeled three-style headmaster comparison. The repeated Goblin image in the pending 3D-model section is replaced by a model-study placeholder; the lesson and voice portraits remain for identification.

Full-resolution masters are in `../assets/concepts/2026-10-30/website/`. Served WebP copies are in `dist/assets/candid/`. Generation prompts and reference paths are recorded in `../docs/art/website-candid-image-prompts.json`. Images were generated with the built-in image tool and reviewed in desktop and mobile layouts. Prior concept masters are preserved. No live deployment was made as part of this local artwork update.

## 3D model test page

`dist/model-test.html` is linked from the music-workshop section of Prototypes. It displays the assembled rehearsal nook as a self-contained GLB with camera presets, orbit/pan/zoom, lighting choices, wireframe, reset and optional rotation. Keyboard users can tab to the canvas and use arrow keys to pan, or use the labeled viewpoint buttons. A poster, loading status, model download and explicit error state support slower connections or unavailable WebGL.

The served model is `dist/assets/models/rehearsal-nook.glb` (37 meshes, 82,772 triangles, approximately 18 MB), exported from the local Blender scene. All model textures are embedded. `dist/assets/vendor/three/` contains the required MIT-licensed Three.js 0.181.1 files from the official npm package, including its license. The viewer has no runtime CDN dependency and requires no build step. Serve `dist` over HTTP to preview; browser modules do not run from a file URL. The browser lighting is arranged separately from the Blender render.

The test page also supports object-level transforms through the vendored `TransformControls` addon. Click geometry or choose one of the 37 assets from the list. W/E/R select translation/rotation/scale; Q toggles global/local gizmo axes, remembered independently for each object during the session. Scale follows the object's axes, matching standard transform-gizmo behavior. Numeric position and XYZ Euler orientation are absolute in the model's world-aligned parent space; rotation is shown in degrees and Y is up. Optional snapping uses 0.1 meters, 15 degrees, and 0.1 scale increments. Camera orbit is disabled while dragging a gizmo, and object selection pauses auto-rotation. Undo/redo (including Ctrl/Cmd-Z and Shift-Z), selected-object reset, and full-layout reset support experimentation. The editor changes the current browser scene only; reloading or downloading the original GLB does not retain edits.

The default GLB now contains the user's approved object arrangement captured from the live editor on 1 November 2026. `dist/assets/models/rehearsal-nook-layout.json` preserves the displayed position, XYZ rotation in degrees, scale and per-object gizmo-space values for all 37 named assets. `node presentation-site/scripts/apply-model-layout.mjs` reapplies that snapshot to the served GLB without changing its geometry or texture binary data. The viewer captures these loaded transforms as its reset baseline, so selected-object and full-layout resets restore the approved arrangement. The downloadable GLB has the same layout. The Art Style Guide's environment section includes an actual tool screenshot and a link to the interactive preview.

## Environment concept gallery

The Environments discipline in the Art Style Guide has a large editor screenshot directly beneath its heading, with an explicit “Open 3D viewer” button. Three existing exterior concepts follow: Meadow Cloister, Lakeside Abbey and High Pass School. The guide does not embed or preload the 18 MB 3D scene; the separate editor provides room for its object controls. Interior concept studies are no longer displayed in this section. The three served images are direct crops of the top row of the original six-study Alpine monastery sheet from 30 October 2026, without repainting or upscaling. The master is preserved at `assets/concepts/2026-10-30/environments/05-alpine-monastery-exterior-six-concepts.png`, with crop provenance in `exterior-web-selection.json`. The full-size concept viewer retains previous/next buttons, arrow keys, Escape and focus restoration.

## Animation study

The Animation discipline in the Art Style Guide includes the supplied Goblin Bard victory-emote test: a five-second portrait MP4, served unchanged from `dist/assets/animation/`, with a still from the clip as its poster. Native playback controls, inline mobile playback and a download link require no added JavaScript. The clip does not autoplay. `animation-study.css` is loaded only on the Art Style Guide. The accompanying copy explains early appeal testing, stakeholder buy-in, audience anticipation and establishing art direction, plus using video generation to explore and plan character animation, VFX and cinematics.

## VFX studies

The VFX discipline presents the supplied four-treatment Goblin Bard concept sheet, followed by two five-second motion studies: in-world musical effects and a reward-stars overlay. The sheet is served as a full-resolution WebP with a full-size link; its original PNG is preserved in `assets/concepts/2026-11-01/vfx/`. Both MP4s are served unchanged in `dist/assets/vfx/`, with posters extracted from the clips, native playback controls and individual download links. Videos do not autoplay or preload; the sheet loads lazily. `vfx-studies.css` keeps the paired videos in two columns on desktop and stacks them on mobile. This is a local update awaiting publishing approval.

## Character study placement

The Yeti, Mimic and student-party studies from “Direction across the cast” now sit inside the Characters discipline, below its direction and review criteria. The standalone pre-navigation cast section has been removed.

## Art guide expansion · November 2, 2026

Four disciplines now contain concept artwork for local review: UI button studies mocked onto the music lesson, three character emotes, three unlocked achievement cards, volumetric loot-box and reward-UI studies, four logo directions, Meta Quest hero/icon merchandising and two Facebook banners. Original generated PNGs and provenance are in `assets/concepts/2026-11-02/art-guide/`; the page serves WebPs from `dist/assets/art-guide/`. Prompts and reference roles are recorded in `docs/art/art-guide-expansion-2026-11-02-prompts.json`. The built-in image generator was used. These are exploratory concepts, not approved production assets. The Quest listing is an HTML mockup, with [Meta’s asset guidelines](https://developers.meta.com/vr/resources/asset-guidelines/) as its platform reference.

The large VFX concept sheet sits directly beneath the VFX heading, beside its direction copy; both motion studies remain below it. The Animation and existing exterior artwork are preserved.

The Characters section embeds the user-supplied `goblin_teacher_model_test.glb` as `dist/assets/models/goblin-teacher-test.glb`, unchanged (SHA-256 `4821b7b95eaff4fa466e06a34cf27f1cc09eba8ce4b776ced4d6f13ad83ce058`, approximately 35 MB). Its viewer appears on the right, beside the explanation of early engine testing. `character-study.js` uses the already vendored Three.js and GLTFLoader, starts loading only near the viewport, pauses rendering when offscreen, and supports pointer orbit/zoom, keyboard rotation/zoom, reset and optional auto-rotation. It is a supplied technical test, not a new generated model or an approved art-direction reference. Local review only; the user will approve and commit.

The character lineup spans the full content width, with larger paired teacher studies and a full-width student comparison. Media-led Environment, Animation and VFX sections use separate title and media rows so their descriptive text starts at the top of the image or video. They stack in reading order on mobile. Layout stylesheet URLs are versioned to prevent stale cached rules. The character viewer uses neutral white lights, a neutral environment and background, and Neutral tone mapping; its model, materials and textures are unchanged, with no per-part color correction.
