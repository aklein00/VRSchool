# VRHS presentation website: art direction first

Revised October 29, 2026. This is a working game pitch with dedicated Art Style Guide, Prototypes, Design, and Product pages. The production case study is a supporting part of the Pitch. The Goblin Bard is male, he/him. His 3D model is one example of the broader art direction, not the organizing idea of the presentation.

Planned expansion, October 29: see [the voice, workflow and Campus Passport content plan](presentation-content-expansion-plan.md). It proposes a Character Voices page, a dedicated Production Workflow destination under Art, and teacher welcome stations on Design based on slides 17–20 of the current faculty deck. These additions are planned, not implemented; the dedicated workflow page expands the earlier Pitch-only treatment below.

## Website structure

| Page | Purpose | Initial content |
| --- | --- | --- |
| Pitch | Sell the game and its distinctive visual world | Premise, teen player fantasy, original visual identity, faculty/world exploration, experience loop, production approach, next milestone; direct links to guide and prototypes |
| Art Style Guide | Show Art's direction across the whole game | Shared foundations and eight art disciplines, each with intent, rules, examples, review criteria, and a planned proof |
| Prototypes | Let the visitor inspect and try selected experiments | Goblin model in Sketchfab when ready, environment corner, voice audition, small music interaction, and eventual integrated web slice; accurate status for each |
| Design | Explain how players experience the direction | Core loop, teaching interaction, player expression, interaction hierarchy, accessibility, music activity and scope |
| Product | Make the existing research useful and concise | Audience hypothesis, six relevant comparisons distilled from the 20-game study, implications for VRHS, evidence limits, commercial questions, validation plan, sources |

The Pitch should be understandable without reading the other pages. The Art Style Guide is a first-class destination and the most substantial body of art-direction evidence. Each supporting page should connect its decisions back to the game's visual identity.

## Eight art disciplines

Reference inspected: slide 3 of NFL Clash Art Style Guide lists seven named pillars: Characters, Environments, Animation, UI/Emotes, Cards, Loot Boxes, VFX. Later slides cover app icon, logo, advertising and social/event graphics. For VRHS, use those seven categories with context-appropriate names, plus Brand & Key Art as the eighth. This makes the additional discipline explicit rather than attributing an eight-item list to that slide.

1. **Characters:** silhouette, anatomy, proportions, costume, facial language and teaching props. Goblin model is one proof; existing faculty drawings establish the ensemble.
2. **Environments:** architecture, staging, prop language, materials, lighting and department identities. A beautiful music workshop corner tests those rules together.
3. **Animation:** pose, gesture, idle/listen/teach behavior, timing and emotional range. Start with direction boards or a short movement study; a full rig is optional this weekend.
4. **UI & Emotes:** typography, icons, prompts, feedback states, expressive symbols and accessibility. A consistent readable hierarchy must work alongside the world.
5. **Cards & Illustrated Content:** faculty portraits, learning prompts and illustrated activity summaries. These are proposed presentation/learning formats; no card-game mechanic is implied.
6. **Rewards & Reveals:** how achievement, completion and student work are staged. Adapt the original loot-box discipline into visible earned accomplishment; do not imply randomized paid rewards.
7. **VFX:** visual language for interaction, magical teaching, focus, success and failure. Effects communicate state and preserve character readability.
8. **Brand & Key Art:** title treatment, emblem, hero compositions, presentation imagery and promotional consistency. Reuse the same designed world across pitch and playable.

Shared foundations sit above these disciplines: intended teen tone, shape language, proportion, color/value, material behavior, lighting, detail density, camera/readability and cross-device constraints. AI production, file conventions and asset review are supporting workflows across all eight. ElevenLabs voice supports performance and interaction without replacing visual direction.

For each discipline, the guide needs: one clear intention, practical do/avoid rules, a visual target or explicitly marked placeholder, acceptance criteria, and its next production task. Provisional directions must not be presented as approved style rules. Not every discipline needs a finished asset by Sunday.

## Pitch beats

1. The fantasy: a school worth inhabiting, taught by memorable monster mentors.
2. The visual promise: Art's original drawings and selected direction, with concrete rules that make the cast and world belong together.
3. The experience: arrive, meet, try, receive feedback, create/perform, and share an accomplishment.
4. The art system: eight disciplines working together; selected examples, then a direct link to the guide.
5. Proof through prototypes: model inspection, environment, voice and interactive experiment, assembled into a small slice as they become ready.
6. Production approach: a compact optional case-study subsection showing intention, AI output, directed correction and final use. The tools support the visual decisions.
7. Product opportunity and next step: concise audience rationale, actual observations and the next test. Link to Design and Product for detail.

## Design page

Keep the explanation compact: core loop, teacher/student relationship, expression, short session flow, music-class example, success/feedback states, input/audio/accessibility choices. The four-beat music activity is a proposed prototype, not the scope of the entire game. Show how art helps players recognize who to approach, what can be touched and what changed.

## Product page

Reuse docs/research/teen-game-market-review.md, game-designer-notes.md, art-direction-notes.md and citations.md. Show a six-comparison digest: Royale High (place/belonging), Brawl Stars (readability/objectives), Adopt Me! (warmth/attachment), Dress To Impress (expression/showcase), Minecraft (making/modularity), Genshin Impact (composition/discovery). Each comparison gets one observation, one VRHS implication and a specific visual/design choice. Link a short selected-source list; raw repo research is not deployed.

Call the underlying study a 20-game research set, not a verified popularity ranking of US teens. Royale High is an additional thematic reference outside that set. Keep youth surveys, all-age engagement, downloads and commercial signals distinct. Do not add numerical demand or learning claims. Describe who might choose/pay, the value hypothesis and what still needs testing.

## ComfyUI and ElevenLabs

The current local starter supports preview, speech, motion video and talking video. It does not create a textured 3D mesh or rig. Preserve Art's working hosted edits; update current Goblin identity to male. Assign the existing Goblin voice ID and generate a short audition, followed by welcome, instruction, hint and completion lines. Use prerecorded media with text, replay and mute. Generate one contrasting character only if it helps demonstrate controlled identity/style consistency.

Keep the node graph and production receipts out of the deployed site. Publish selected screenshots, recordings and final outputs only. No live paid generation is needed for visitors. A talking clip does not establish a working rig, and a voice ID is not a trained voice model.

## Publishing boundary

The standalone placeholder is presentation-site/dist/. Only that directory is served as website content. Use copied, selected image derivatives; never serve the VRHS repository root, data, docs, production, private configuration, .git, or original art masters. The hosting manifest sits outside dist and configures the deployment; it is not a public download.

The Utility Infielder project remains a hub. The proposed eventual destination is vrhs.utilityinfielder.com, linked from the hub and personal presentation. The initial owner-private preview is published at https://vrhs-art-direction-pitch.aklein00.chatgpt.site after Art explicitly approved that exact destination and selected content. Publication succeeded. Domain integration at vrhs.utilityinfielder.com is later work. Keep the site source separate from the main portfolio code and deploy only its built output.

## What is next

1. Review the five-page placeholder and the eight-discipline guide structure.
2. Confirm the selected visual treatment and common foundations before expanding asset production.
3. Run a Goblin voice/media audition and verify the separate 3D generation/export route.
4. Review the Goblin model in Sketchfab before environment production, as requested. The website and guide can advance while the model is pending.
5. Build the workshop corner and refine the small activity, showing UI, gesture, feedback, materials, light and reward as a coherent direction.
6. Replace each relevant placeholder with actual evidence; finish the research digest, test, package and rehearse.

## Placeholder delivered locally

Five pages and a working four-beat interaction are implemented in presentation-site/dist. The art guide covers all eight disciplines; unfinished 3D, environment and voice studies are labeled. Only selected compressed images and static HTML/CSS/JS enter the website ZIP. Art explicitly approved the exact temporary destination and selected content; the owner-private preview was published successfully. The preview requires ChatGPT sign-in. The main Utility Infielder domain remains unchanged.
