"""Rebuild importable UI/API graphs and the portable archive from characters.json."""
import json
import shutil
import zipfile
import copy
from pathlib import Path

BASE = Path(__file__).resolve().parent
PACK = BASE / "ComfyUI-VRHS"


def build():
    registry = json.loads((PACK / "characters.json").read_text(encoding="utf-8"))
    registry_text = json.dumps(registry, ensure_ascii=False)
    shutil.copyfile(PACK / "characters.json", BASE / "vrhs-characters.json")
    for filename, mode, character, title in [
        ("00-preview", "preview", "02-math-yeti", "START HERE • Free character and prompt preview"),
        ("01-audio", "audio", "02-math-yeti", "Speech with your existing ElevenLabs voice"),
        ("02-motion-video", "motion_video", "09-art-oobleck", "Animate the reference drawing • Silent 5/10 second clip"),
        ("03-talking-video", "talking_video", "10-music-goblin", "Talking character pilot • Speech plus avatar video"),
    ]:
        nodes = [
            {"id": 1, "type": "VRHSCharacter", "title": "1 • Choose character, action and spoken line",
             "pos": [60, 230], "size": [540, 800], "flags": {}, "order": 0, "mode": 0,
             "inputs": [], "outputs": [{"name": "character_job_json", "type": "STRING", "links": [1], "slot_index": 0}],
             "properties": {"Node name for S&R": "VRHSCharacter"},
             "widgets_values": [character, "speak" if mode == "talking_video" else "greet", "", "welcome", "", "A", "", "", "", registry_text]},
            {"id": 2, "type": "VRHSFalProduction", "title": "2 • Choose output and Run",
             "pos": [700, 230], "size": [550, 800], "flags": {}, "order": 1, "mode": 0,
             "inputs": [{"name": "character_job_json", "type": "STRING", "link": 1}],
             "outputs": [{"name": name, "type": "STRING", "links": None, "slot_index": i}
                         for i, name in enumerate(["result_json", "local_media_path", "manifest_json"])],
             "properties": {"Node name for S&R": "VRHSFalProduction"},
             "widgets_values": [True, mode, "5", 0]},
            {"id": 3, "type": "Note", "title": title, "pos": [60, 20], "size": [1190, 170],
             "flags": {}, "order": 2, "mode": 0, "inputs": [], "outputs": [], "properties": {},
             "widgets_values": [
                 "ONE-TIME SETUP: Copy the complete ComfyUI-VRHS folder into ComfyUI/custom_nodes, install requirements.txt with ComfyUI's Python, then restart. "
                 "Preview is free. Audio uses ELEVENLABS_API_KEY; video uses FAL_KEY; talking video needs both. Enter API keys in ComfyUI-VRHS/config.ini or the server environment, never the graph. "
                 "Select any of the 18 characters on the left. Empty script_override uses the chosen sample line. Ettin head A/B chooses one speaker. "
                 "Change mode on the right: preview / audio / motion_video / talking_video. "
                 "duration_seconds applies only to silent motion. Talking video follows the speech audio. "
                 "Outputs and receipts save to ComfyUI/output/VRHS/<character>. Repeat jobs reuse saved results. Increase generation_variant to request a new audition. "
                 "Paste your existing ElevenLabs voice ID into elevenlabs_voice_id. The Ettin has a separate elevenlabs_head_b_voice_id field. "
                 "See README.md for Intel Mac browser-hosted setup and ElevenLabs configuration."
             ], "color": "#34313b", "bgcolor": "#51495c"},
        ]
        workflow = {"last_node_id": 3, "last_link_id": 1, "nodes": nodes,
                    "links": [[1, 1, 0, 2, 0, "STRING"]], "groups": [], "config": {},
                    "extra": {"ds": {"scale": 0.8, "offset": [30, 30]}, "vrhs": {
                        "project": "VRSchool", "characters": 18, "required_custom_nodes": ["ComfyUI-VRHS"],
                        "built": registry["updated"]}}, "version": 0.4}
        (BASE / "workflows" / (filename + ".json")).write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n")
        # Separate API exports have no canvas layout and are for /prompt automation.
        api = {
            "1": {"class_type": "VRHSCharacter", "inputs": {
                "character": character, "action": nodes[0]["widgets_values"][1], "action_override": "", "line": "welcome", "script_override": "",
                "ettin_head": "A", "elevenlabs_voice_id": "", "elevenlabs_head_b_voice_id": "", "elevenlabs_model_id": "", "registry_json": registry_text}},
            "2": {"class_type": "VRHSFalProduction", "inputs": {
                "character_job_json": ["1", 0], "enabled": True, "mode": mode, "duration_seconds": "5", "generation_variant": 0}},
        }
        api_dir = BASE / "api-workflows"
        api_dir.mkdir(exist_ok=True)
        (api_dir / (filename + ".api.json")).write_text(json.dumps(api, ensure_ascii=False, indent=2) + "\n")
    # One editable, independently switchable section per character, including headmaster.
    grouped = {"last_node_id": 37, "last_link_id": 18, "nodes": [], "links": [], "groups": [],
               "config": {}, "extra": {"ds": {"scale": 0.45, "offset": [25, 25]}, "vrhs": {
                   "project": "VRSchool", "characters": 18, "faculty": 13, "students": 5,
                   "required_custom_nodes": ["ComfyUI-VRHS"], "built": registry["updated"]}}, "version": 0.4}
    grouped_api = {}
    preset_actions = ["greet", "teach", "teach", "listen", "teach", "greet", "listen", "greet", "teach",
                      "teach", "greet", "teach", "greet", "greet", "listen", "teach", "teach", "greet"]
    for i, record in enumerate(registry["characters"]):
        select_id, output_id, link_id = 2*i+1, 2*i+2, i+1
        x, y = (i % 3)*1220+40, (i // 3)*1070+290
        selector = copy.deepcopy(nodes[0])
        producer = copy.deepcopy(nodes[1])
        action = preset_actions[i]
        sample = record["scripts"]["welcome"]
        selector.update(id=select_id, pos=[x, y], size=[510, 850], order=2*i,
                        title=record["display_name"] + " • Action and sample dialogue")
        selector["outputs"][0]["links"] = [link_id]
        selector["widgets_values"] = [record["id"], action, record["motion_presets"][action], "welcome", sample, "A", "", "", "", registry_text]
        producer.update(id=output_id, pos=[x+570, y], size=[560, 850], order=2*i+1,
                        title="ON/OFF • " + record["display_name"])
        producer["inputs"][0]["link"] = link_id
        producer["widgets_values"] = [i == 1, "preview", "5", 0]
        grouped["nodes"].extend([selector, producer])
        grouped["links"].append([link_id, select_id, 0, output_id, 0, "STRING"])
        color = "#b39b5b" if record["role"] == "headmaster" else "#6d82a8" if record["role"] == "teacher" else "#849d7c"
        grouped["groups"].append({"id": i+1, "title": f"{i+1:02d} • {record['display_name']}",
                                  "bounding": [x-20, y-65, 1170, 955], "color": color, "font_size": 26, "flags": {}})
        grouped_api[str(select_id)] = {"class_type": "VRHSCharacter", "inputs": {
            "character": record["id"], "action": action, "action_override": record["motion_presets"][action],
            "line": "welcome", "script_override": sample, "ettin_head": "A", "elevenlabs_voice_id": "", "elevenlabs_head_b_voice_id": "", "elevenlabs_model_id": "", "registry_json": registry_text}}
        grouped_api[str(output_id)] = {"class_type": "VRHSFalProduction", "inputs": {
            "character_job_json": [str(select_id), 0], "enabled": i == 1, "mode": "preview", "duration_seconds": "5",
            "generation_variant": 0}}
    note = copy.deepcopy(nodes[2])
    note.update(id=37, pos=[40, 20], size=[3570, 180], order=36,
                title="VRHS • 18 character sections • 13 faculty including the Headmaster + 5 students")
    note["widgets_values"] = [
        "Every colored section is one character. The first node contains a prefilled action, sample spoken text, and the full character bible. "
        "Toggle enabled ON/OFF in that section's right-hand output node. OFF makes no ElevenLabs or fal calls and saves no media. "
        "Only the Yeti section is ON by default, in FREE PREVIEW mode; all other sections start OFF. "
        "Select audio, motion_video or talking_video in enabled sections to generate paid media. Run queues every enabled section. "
        "Sample teacher dialogue comes from the character sheets; student dialogue is proposed. The Headmaster has section 13. "
        "Paste each character's ElevenLabs voice ID in its left node. Ettin: set both voice-ID fields, change head A/B, and clear script_override to use that head's sample. "
        "Clear action_override when changing the action preset; clear script_override when changing the line preset. "
        "Full setup: README.md. Outputs: ComfyUI/output/VRHS/<character>."
    ]
    grouped["nodes"].append(note)
    (BASE / "workflows" / "VRHS-All-Characters-Grouped.json").write_text(json.dumps(grouped, ensure_ascii=False, indent=2)+"\n")
    (BASE / "api-workflows" / "VRHS-All-Characters-Grouped.api.json").write_text(json.dumps(grouped_api, ensure_ascii=False, indent=2)+"\n")
    archive = BASE / "VRHS-ComfyUI-Starter.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for folder in [PACK, BASE / "workflows", BASE / "api-workflows"]:
            for path in sorted(folder.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc" and path.name != "config.ini":
                    bundle.write(path, "VRHS-ComfyUI-Starter/" + path.relative_to(BASE).as_posix())
        for filename in ["README.md", "vrhs-characters.json", "build_bundle.py", "queue_batch.py"]:
            path = BASE / filename
            if path.exists():
                bundle.write(path, "VRHS-ComfyUI-Starter/" + filename)
    print(f"Built five UI graphs, five API graphs and {archive.name}")


if __name__ == "__main__":
    build()
