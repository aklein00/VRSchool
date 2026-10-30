# VRHS: ElevenLabs voices + fal video in ComfyUI

Open **workflows/VRHS-All-Characters-Grouped.json** in a ComfyUI installation that supports your own custom nodes. It has **18 independently switchable character sections: 12 subject teachers, the headmaster and five students**. Each section includes its reference drawing, character description, sample dialogue and prefilled action. Only the Yeti starts ON, in free preview mode. The headmaster is section 13.

**Speech now uses your existing ElevenLabs voices through your ElevenLabs account. Video uses fal.** You do not need to recreate, clone or transfer your voices to another provider. Voice IDs have deliberately been left blank because your actual assignments have not been supplied. Missing IDs give a clear setup error before any speech request.

## Access from your Intel Mac

Comfy Desktop for macOS requires Apple Silicon; it is not the right installer for an Intel Mac. Use a browser connection to a hosted ComfyUI machine that allows you to upload and install private custom nodes. [RunComfy documents support for uploaded files and node installation](https://comfyui-guides.runcomfy.com/ultimate-comfyui-how-tos-a-runcomfy-guide/is-runcomfy-machine-private). Its generation computer runs remotely; your Mac displays the browser interface.

1. Launch a hosted ComfyUI instance with file access and custom-node installation.
2. Upload and extract **VRHS-ComfyUI-Starter.zip** using the host's file browser.
3. Put the complete **ComfyUI-VRHS** folder in that instance's **ComfyUI/custom_nodes/** directory. Keep its `characters.json`, `nodes` and `references` folders together.
4. Install `ComfyUI-VRHS/requirements.txt` using that instance's ComfyUI Python environment, then restart the ComfyUI process.
5. Open **workflows/VRHS-All-Characters-Grouped.json** in the ComfyUI canvas.
6. Run the Yeti preview first. It needs no API keys and makes no generation calls.

This package uses API calls rather than local model checkpoints, so it does not need a powerful GPU for its own generation steps. Hosted providers may still charge for instance time in addition to ElevenLabs and fal usage. Avoid leaving rented instances running between sessions.

[Comfy Cloud currently does not let users directly install their own custom nodes](https://support.comfy.org/articles/6791455062-custom-nodes-on-cloud), so the included private VRHS nodes cannot simply be uploaded there. A self-managed ComfyUI server on another Windows or Linux computer is another browser-access option. Hosting services and actual browser import have not been live-tested for this delivery.

The JSON opens in **ComfyUI**, not directly in fal's model playground. ComfyUI calls the APIs. Deploying the entire workflow on fal would require a separate server deployment; that is not part of this package.

## Connect your existing ElevenLabs voices

1. In ElevenLabs, open **My Voices**, choose a voice's three-dot menu and select **Copy voice ID**. [Official instructions](https://elevenlabs.io/docs/help-center/technical/how-do-i-find-the-voice-id-of-my-voices-via-the-website-and-api).
2. Paste that ID into **elevenlabs_voice_id** in the matching character's left-hand node. A voice ID is an identifier, not your API key.
3. For the two-headed Ettin, put head A's ID in **elevenlabs_voice_id** and head B's ID in **elevenlabs_head_b_voice_id**. The **ettin_head** control chooses the speaker. Head B never silently borrows head A's voice.
4. Leave **elevenlabs_model_id** blank to use the character registry model (default `eleven_multilingual_v2`), or enter another TTS model available to your voice, such as `eleven_v3`.
5. In the installed **ComfyUI-VRHS** folder, duplicate **config.ini.example** and name the copy **config.ini**. Enter your keys after the equals signs. The node reads this file when it runs; no startup-command changes are needed. Environment variables are also supported and take precedence. Keep keys out of the workflow and character JSON.
6. Turn that character section ON and choose **audio** mode on its right-hand output node. Run to generate the existing sample text in your voice.
7. For **talking_video**, also enter **FAL_KEY** in the same settings file. The extension generates the speech with ElevenLabs, uploads the saved MP3 and character reference to fal, and requests the video.

Audio mode needs only the ElevenLabs key. Silent motion video needs only the fal key. Talking video validates both keys and the voice ID before making paid calls. Preview needs none. Keys are read from the private settings file or server environment and are not written into saved graphs or receipts. Keep config.ini private; Cloud Save may include files in your hosted environment, so do not share a saved environment containing your keys. The local bundle builder excludes config.ini from exported ZIPs.

For a locally managed server, set the environment before launching it:

```sh
export ELEVENLABS_API_KEY='your-elevenlabs-key'
export FAL_KEY='your-fal-key'
# Launch ComfyUI from this same environment using its usual command.
```

Your ElevenLabs account/key must have access to the chosen voice and text-to-speech API. The extension does not publish your voices or move them between accounts. Voice descriptions remain creative direction notes; the existing voice ID selects the actual speaker.

## Character controls

| Control | Purpose |
| --- | --- |
| enabled | ON runs this section; OFF saves nothing and makes no ElevenLabs or fal calls |
| action | idle, listen, greet, teach, travel or speak |
| action_override | Explicit character-specific action, prefilled in the grouped graph; clear it to use the selected action preset |
| line | welcome, reassure or prompt |
| script_override | Prefilled character-sheet welcome; edit it, or clear it to use the line preset |
| ettin_head | A/B voice and dialogue selection; clear script_override to use that head's sample |
| elevenlabs_voice_id | Existing ElevenLabs voice for this character, or Ettin head A |
| elevenlabs_head_b_voice_id | Separate voice for Ettin head B; ignored for other characters |
| elevenlabs_model_id | Optional model override; blank uses the registry model, initially eleven_multilingual_v2 |
| mode | preview, audio, motion_video or talking_video |
| duration_seconds | Five or ten seconds for silent motion; talking-video duration follows the speech |
| generation_variant | Keep 0 to reuse cached speech/media; increase to request a fresh performance. It is a cache version, not a provider seed |

Each section starts assigned to its named character. Explicitly edited speech, actions and voice-ID overrides stay in place if you later change that selection; clear them if assigning the node to someone else. All enabled sections run when you click Run.

Faculty sample dialogue comes from the character-register source records. The headmaster's welcome is “Welcome to VR High School. You belong here before you solve a single puzzle.” Student sample dialogue and voice direction are proposals because no student dialogue sheets were present. Current female dragon/Gnoll/headmaster identities and non-binary Oobleck/Mimic identities are retained.

## Save voice assignments for batches

You can simply save your edited grouped workflow in ComfyUI; its individual voice-ID fields will be retained. For the included batch helper, put the IDs in **vrhs-characters.json** under each character's `voice.elevenlabs.voice_id`.

```json
"elevenlabs": {
  "voice_id": "YOUR_EXISTING_VOICE_ID",
  "model_id": "eleven_multilingual_v2"
}
```

For Ettin, use `voice.heads.A.elevenlabs.voice_id` and `voice.heads.B.elevenlabs.voice_id`. These example placeholders must be replaced with your real IDs. Never add an API key to this JSON.

To rebuild all canvas files and the ZIP, edit **ComfyUI-VRHS/characters.json** and run `python build_bundle.py`. It refreshes the standalone JSON too. Embedded character data travels with the canvas workflows; the extension folder still supplies code and reference images. Manual canvas edits are not automatically copied back into these source files; keep a saved workflow copy before rebuilding.

## Outputs and caching

| Mode | Output | Fresh generation requests |
| --- | --- | --- |
| preview | Current PNG plus selected prompt/script receipt | None |
| audio | ElevenLabs MP3 | One direct ElevenLabs request |
| motion_video | Silent five- or ten-second MP4 | One fal Kling image-to-video request |
| talking_video | ElevenLabs MP3 and talking-character MP4 | One ElevenLabs request plus one fal Kling Avatar request |

Outputs save to **ComfyUI/output/VRHS/<character-id>/** with JSON receipts containing scripts, prompts, IDs, model names, reference checksums and provider request IDs where returned. Audio/video displays in the output node on current ComfyUI frontends. STRING outputs carry the raw result JSON, local path and manifest; decoded native AUDIO/VIDEO sockets are not provided.

Speech is cached under `.elevenlabs_jobs` by voice, model, script and generation variant. The same voice and line can be reused for a talking video without paying ElevenLabs again. `.fal_jobs` journals fal request IDs so a retry with the same request can resume. Completed local media is reused. Increase generation_variant to request another performance.

There are no automatic retries of ElevenLabs speech POSTs: a timed-out request could already have generated billable speech. Check ElevenLabs history before retrying after an ambiguous failure. A local interruption does not promise cancellation of an already-submitted remote job. If a fal submission fails before its ID is recorded, check fal's dashboard before retrying. Use one ComfyUI process with this output folder; caches do not coordinate simultaneous server processes.

## Suggested production order

1. Assign your existing teacher voices, including the headmaster and two Ettin heads. Make one short audio check per speaker.
2. Make one welcome, instruction, hint and reassuring response for the Yeti puzzle or Oobleck workshop already proposed in the project.
3. Test talking clips with the Goblin, Yeti and headmaster before expanding to the whole cast.
4. Generate small idle/listen/greet/teach libraries for repeated use. For the spider, slime, chest and two-headed Ettin, start with silent movement plus voice-over and inspect anatomy carefully.

Stylized avatar support does not guarantee reliable lip sync or anatomy for these specific nonhuman drawings. Keep the camera fixed and request one small movement. Five-second clips are loop candidates until you inspect their endpoints. Exact scripts are retained, but timed subtitles, curriculum review, engine rigs and classroom-scene generation are not implemented here.

## Batch helper

`workflows/` contains canvas files; `api-workflows/` contains local ComfyUI `/prompt` graphs. The helper prints jobs without submitting unless you add `--submit`.

```sh
# List three free previews.
python queue_batch.py --characters 02-math-yeti 09-art-oobleck 13-headmaster-lich

# List faculty audio jobs after entering voice IDs in vrhs-characters.json.
python queue_batch.py --characters faculty --mode audio --max-jobs 13

# Queue a single audio job to an already running local ComfyUI server.
python queue_batch.py --characters 13-headmaster-lich --mode audio --submit
```

Run the helper on the server hosting ComfyUI; it connects only to localhost by design. For browser-hosted use, the canvas is usually simpler. `--ettin-head B` chooses the second head. The default three-job cap can be raised explicitly; it is not a dollar budget. Changing only the action in audio mode reuses the same speech.

## Verification

Ten offline tests cover all reference checksums, real free-preview saves, current identities, dialogue, head-specific voice IDs, UI/API graph agreement, disabled sections, request caching, ElevenLabs HTTP request construction and credential handling, audio without a fal key, and validation before talking-video charges. Paid responses are simulated. Five canvas files are checked against ComfyUI's official v0.4 workflow schema.

**No authenticated ElevenLabs/fal generation or live ComfyUI canvas import has been run for this update.** Your voice IDs and API keys still need configuring. No generation credits were spent. The older Qwen embedding graphs were moved to `archive/pre-elevenlabs/` in the project and are excluded from the new ZIP.

Implementation references checked 29 October 2026: [ElevenLabs create speech](https://elevenlabs.io/docs/api-reference/text-to-speech/convert), [ComfyUI workflow schema](https://github.com/Comfy-Org/docs/blob/main/specs/workflow_json_0.4.mdx), [fal Python client](https://github.com/fal-ai/fal/tree/main/projects/fal_client), [Kling image-to-video](https://fal.ai/models/fal-ai/kling-video/v2.1/standard/image-to-video/api), [Kling Avatar](https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/standard/api), and [Comfy Desktop Mac requirements](https://docs.comfy.org/installation/desktop/macos). Check current provider pricing before a large batch.
