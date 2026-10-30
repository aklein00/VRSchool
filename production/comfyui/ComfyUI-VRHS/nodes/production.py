"""VRSchool character selection, ElevenLabs speech and fal video. Credentials never enter a graph."""

from __future__ import annotations

import hashlib
import configparser
import json
import os
import shutil
import time
from pathlib import Path
from urllib.parse import urlparse, quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "characters.json"
ELEVEN_TTS = "https://api.elevenlabs.io/v1/text-to-speech/"
MOTION = "fal-ai/kling-video/v2.1/standard/image-to-video"
AVATAR = "fal-ai/kling-video/ai-avatar/v2/standard"


def api_key(name):
    value = os.environ.get(name, "").strip()
    if value:
        return value
    config = configparser.ConfigParser(interpolation=None)
    config.read(ROOT / "config.ini", encoding="utf-8")
    return config.get("API", name, fallback="").strip()


def read_registry(text=None):
    registry = json.loads(text) if text and text.strip() else json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if registry.get("schema_version") != "1.0" or not registry.get("characters"):
        raise ValueError("Expected the VRHS character registry, schema_version 1.0.")
    return registry


def reference_path(record):
    base = (ROOT / "references").resolve()
    path = (base / record["reference"]["bundle_file"]).resolve()
    if base not in path.parents or not path.is_file():
        raise ValueError("Reference image missing. Copy the complete ComfyUI-VRHS folder, including references.")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != record["reference"]["sha256"]:
        raise ValueError("Reference checksum differs from the registry. Update the registry when replacing artwork.")
    return path


def atomic_json(path, data):
    import uuid
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def safe_url(url):
    if urlparse(url).scheme != "https" or not urlparse(url).netloc:
        raise ValueError("Use a publicly accessible HTTPS media URL.")
    return url


def select_character(registry, character, action, line, script_override, ettin_head, action_override="",
                     elevenlabs_voice_id="", elevenlabs_head_b_voice_id="", elevenlabs_model_id=""):
    records = {c["id"]: c for c in registry["characters"]}
    record = records[character]
    voice = record["voice"]
    if voice.get("heads"):
        voice = voice["heads"][ettin_head]
        script = record["scripts_by_head"][ettin_head].get(line, record["scripts"][line])
    else:
        script = record["scripts"][line]
    eleven = dict(voice.get("elevenlabs", {}))
    override = elevenlabs_head_b_voice_id if record["voice"].get("heads") and ettin_head == "B" else elevenlabs_voice_id
    eleven["voice_id"] = override.strip() or eleven.get("voice_id") or ""
    eleven["model_id"] = elevenlabs_model_id.strip() or eleven.get("model_id") or "eleven_multilingual_v2"
    script = script_override.strip() or script
    if not script or len(script) > 3000:
        raise ValueError("Use a nonempty short script of at most 3,000 characters; split longer lessons into clips.")
    motion = action_override.strip() or record["motion_presets"][action]
    if record["id"] == "05-geography-ettin":
        motion += f" Head {ettin_head} is the only speaker; the other head keeps its mouth closed."
    video_prompt = " ".join([
        registry["defaults"]["style_prompt"], record["appearance"],
        "Preserve the exact reference anatomy, silhouette, costume and existing props.", motion,
        "Locked camera, full character inside frame, plain white background, no cuts or added text.",
    ])
    return {
        "character": record, "action": action, "line": line, "ettin_head": ettin_head,
        "script": script, "voice_prompt": voice["description"], "video_prompt": video_prompt,
        "negative_prompt": registry["defaults"]["negative_prompt"],
        "notes": record.get("production_notes", []),
        "elevenlabs": eleven,
    }


class VRHSCharacter:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("character_job_json",)
    FUNCTION = "select"
    CATEGORY = "VRHS"

    @classmethod
    def INPUT_TYPES(cls):
        registry = read_registry()
        return {"required": {
            "character": ([c["id"] for c in registry["characters"]], {"default": "02-math-yeti"}),
            "action": (["idle", "listen", "greet", "teach", "travel", "speak"], {"default": "greet"}),
            "action_override": ("STRING", {"default": "", "multiline": True, "tooltip": "Optional explicit action. Empty uses this character's selected movement preset. Clear when switching character or action."}),
            "line": (["welcome", "reassure", "prompt"], {"default": "welcome"}),
            "script_override": ("STRING", {"default": "", "multiline": True}),
            "ettin_head": (["A", "B"], {"default": "A"}),
            "elevenlabs_voice_id": ("STRING", {"default": "", "tooltip": "Your ElevenLabs voice ID for this character (Ettin head A). A voice ID is not an API key."}),
            "elevenlabs_head_b_voice_id": ("STRING", {"default": "", "tooltip": "Ettin head B only. Uses its own voice; never silently substitutes head A."}),
            "elevenlabs_model_id": ("STRING", {"default": "", "tooltip": "Optional model override. Blank uses the character registry model (default eleven_multilingual_v2). You can enter eleven_v3."}),
            "registry_json": ("STRING", {"default": "", "multiline": True}),
        }}

    def select(self, character, action, line, script_override="", ettin_head="A", registry_json="", action_override="",
               elevenlabs_voice_id="", elevenlabs_head_b_voice_id="", elevenlabs_model_id=""):
        job = select_character(read_registry(registry_json), character, action, line, script_override, ettin_head, action_override,
                               elevenlabs_voice_id, elevenlabs_head_b_voice_id, elevenlabs_model_id)
        return (json.dumps(job, ensure_ascii=False),)


def speech_request(job, require_voice=True):
    config = job.get("elevenlabs", {})
    voice_id = config.get("voice_id", "").strip()
    if require_voice and not voice_id:
        raise ValueError("Set elevenlabs_voice_id for this character. For Ettin head B, set elevenlabs_head_b_voice_id. Find IDs in ElevenLabs > My Voices > More actions > Copy voice ID.")
    if voice_id and not all(c.isascii() and (c.isalnum() or c in "_-") for c in voice_id):
        raise ValueError("Paste only the ElevenLabs voice ID, not a share URL or API key.")
    endpoint = ELEVEN_TTS + (quote(voice_id, safe="") if voice_id else "<voice-id-not-set>") + "?output_format=mp3_44100_128"
    args = {"text": job["script"], "model_id": config.get("model_id") or "eleven_multilingual_v2"}
    return endpoint, args


def elevenlabs_audio(job, directory, variant=0):
    """Cache the downloaded speech across actions and video retries. No automatic POST retries."""
    endpoint, arguments = speech_request(job)
    key = api_key("ELEVENLABS_API_KEY")
    if not key:
        raise ValueError("Set ELEVENLABS_API_KEY in ComfyUI-VRHS/config.ini [API] or the server environment. Keep it out of the workflow.")
    identity = json.dumps([endpoint, arguments, int(variant)], sort_keys=True)
    digest = hashlib.sha256(identity.encode()).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    audio = directory / (digest + ".mp3")
    receipt_path = directory / (digest + ".json")
    if audio.is_file() and receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text())
        if hashlib.sha256(audio.read_bytes()).hexdigest() == receipt["audio_sha256"]:
            return audio, receipt
    request = Request(endpoint, data=json.dumps(arguments).encode(), method="POST",
                      headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    temporary = audio.with_suffix(".part")
    try:
        with urlopen(request, timeout=180) as response, temporary.open("wb") as output:
            if "audio" not in response.headers.get("Content-Type", "").lower():
                raise ValueError("ElevenLabs returned a non-audio response; no speech file was saved.")
            shutil.copyfileobj(response, output)
            receipt = {"provider": "elevenlabs", "endpoint": endpoint, "arguments": arguments,
                       "request_id": response.headers.get("request-id") or response.headers.get("x-request-id"),
                       "created_at": time.time(), "variant": int(variant)}
        if temporary.stat().st_size == 0:
            raise ValueError("ElevenLabs returned an empty audio file.")
        os.replace(temporary, audio)
        receipt["audio_sha256"] = hashlib.sha256(audio.read_bytes()).hexdigest()
        atomic_json(receipt_path, receipt)
        return audio, receipt
    except HTTPError as exc:
        # Do not include request headers or credentials in errors or receipts.
        raise ValueError(f"ElevenLabs request failed (HTTP {exc.code}). Check the selected voice ID, API access, model and available credits in your ElevenLabs account.") from None
    finally:
        temporary.unlink(missing_ok=True)


class FalQueue:
    """Journal request IDs before polling; reuse completed results across restarts.

    A submit response lost before its ID is written is inherently ambiguous; no
    automatic resubmit is attempted inside submit(). Check fal's dashboard first.
    """
    def __init__(self, directory, variant=0):
        import fal_client
        self.client = fal_client.SyncClient(key=api_key("FAL_KEY") or None)
        self.directory = directory
        self.variant = int(variant)

    def call(self, endpoint, arguments):
        identity = json.dumps([endpoint, arguments, self.variant], sort_keys=True)
        key = hashlib.sha256(identity.encode()).hexdigest()
        path = self.directory / (key + ".json")
        state = json.loads(path.read_text()) if path.exists() else {}
        if "result" in state:
            return state["result"], state
        if state.get("request_id"):
            handle = self.client.get_handle(endpoint, state["request_id"])
        else:
            handle = self.client.submit(endpoint, arguments=arguments)
            state = {"endpoint": endpoint, "request_id": handle.request_id, "arguments": arguments,
                     "variant": self.variant, "submitted_at": time.time()}
            atomic_json(path, state)
        # Cancellation exits locally while retaining the fal request ID for resume.
        # It does not assume a local interruption cancels remote billing.
        for _ in handle.iter_events(interval=2):
            try:
                import comfy.model_management
                comfy.model_management.throw_exception_if_processing_interrupted()
            except ImportError:
                pass
        state["result"] = self.client.result(endpoint, state["request_id"])
        atomic_json(path, state)
        return state["result"], state

    def upload(self, path):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        cache = self.directory / ("upload-" + digest + ".json")
        if cache.exists():
            data = json.loads(cache.read_text())
            if time.time() - data["created_at"] < 6 * 3600:
                return data["url"]
        url = self.client.upload_file(str(path))
        atomic_json(cache, {"url": url, "created_at": time.time()})
        return url


def download(url, path):
    safe_url(url)
    temporary = path.with_suffix(path.suffix + ".part")
    try:
        with urlopen(url, timeout=120) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def media_descriptor(path, output_root):
    return {"filename": path.name, "subfolder": path.parent.relative_to(output_root).as_posix(), "type": "output"}


class VRHSFalProduction:
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("result_json", "local_media_path", "manifest_json")
    FUNCTION = "produce"
    CATEGORY = "VRHS"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "character_job_json": ("STRING", {"forceInput": True}),
            "enabled": ("BOOLEAN", {"default": True, "label_on": "ON", "label_off": "OFF", "tooltip": "OFF skips this section without ElevenLabs or fal calls or saved media."}),
            "mode": (["preview", "audio", "motion_video", "talking_video"], {"default": "preview"}),
            "duration_seconds": (["5", "10"], {"default": "5"}),
            "generation_variant": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
        }}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always visit the output node so missing downloads can be recovered.
        # Remote generation is protected by the persistent FalQueue journal.
        return float("nan")

    def produce(self, character_job_json, mode="preview", duration_seconds="5", generation_variant=0, enabled=True):
        if not enabled:
            return {"ui": {}, "result": ('{"disabled":true}', "", '{"disabled":true}')}
        import folder_paths
        job = json.loads(character_job_json)
        record = job["character"]
        if not record["id"] or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in record["id"]):
            raise ValueError("Character IDs must contain only lowercase letters, numbers and hyphens.")
        reference = reference_path(record)
        output_root = Path(folder_paths.get_output_directory()).resolve()
        folder = output_root / "VRHS" / record["id"]
        folder.mkdir(parents=True, exist_ok=True)
        identity = json.dumps(["elevenlabs-v1", job, mode, duration_seconds, generation_variant], sort_keys=True)
        job_id = hashlib.sha256(identity.encode()).hexdigest()[:12]
        stem = f"{mode}-{job['action']}-{job['line']}-{job['ettin_head']}-{job_id}"
        manifest_path = folder / (stem + ".json")
        # A complete local artifact remains usable after temporary fal URLs expire.
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            media = folder / manifest["media_file"]
            if media.is_file() and hashlib.sha256(media.read_bytes()).hexdigest() == manifest["media_sha256"]:
                return self.response(manifest, media, output_root)
        manifest = {"version": "1.0", "job_id": job_id, "mode": mode, "job": job,
                    "reference_sha256": record["reference"]["sha256"], "requests": [], "created_at": time.time()}
        if mode == "preview":
            media = folder / (stem + ".png")
            shutil.copyfile(reference, media)
            manifest["result"] = {"preview_only": True, "speech_request": speech_request(job, require_voice=False),
                                  "voice_id_configured": bool(job["elevenlabs"].get("voice_id")),
                                  "motion_request": {"endpoint": MOTION, "arguments": {
                                      "prompt": job["video_prompt"], "duration": duration_seconds,
                                      "negative_prompt": job["negative_prompt"], "image_url": "<uploaded reference at generation time>"}}}
        else:
            if mode not in {"audio", "motion_video", "talking_video"}:
                raise ValueError("Unknown production mode.")
            # Validate every required account before making any paid calls.
            if mode in {"audio", "talking_video"}:
                speech_request(job)
                if not api_key("ELEVENLABS_API_KEY"):
                    raise ValueError("Set ELEVENLABS_API_KEY in ComfyUI-VRHS/config.ini [API] or the server environment.")
            if mode in {"motion_video", "talking_video"} and not api_key("FAL_KEY"):
                raise ValueError("Set FAL_KEY in ComfyUI-VRHS/config.ini [API] or the server environment.")
            queue = FalQueue(output_root / "VRHS" / ".fal_jobs", generation_variant) if mode != "audio" else None
            if mode == "motion_video":
                args = {"image_url": queue.upload(reference), "prompt": job["video_prompt"],
                        "duration": duration_seconds, "negative_prompt": job["negative_prompt"]}
                result, receipt = queue.call(MOTION, args)
                manifest["requests"].append(receipt)
                url = result["video"]["url"]
                media = folder / (stem + ".mp4")
            else:
                cached_audio, receipt = elevenlabs_audio(job, output_root / "VRHS" / ".elevenlabs_jobs", generation_variant)
                manifest["requests"].append(receipt)
                # Always archive the original speech, including for talking videos.
                audio = folder / (stem + ".mp3")
                shutil.copyfile(cached_audio, audio)
                manifest["speech_audio_file"] = audio.name
                result = {"audio": {"local_file": audio.name}, "provider": "elevenlabs",
                          "voice_id": job["elevenlabs"]["voice_id"]}
                media = audio
                if mode == "talking_video":
                    # Re-upload the durable local audio instead of chaining an expired
                    # cached fal result URL after a previous interrupted run.
                    args = {"image_url": queue.upload(reference), "audio_url": queue.upload(audio),
                            "prompt": job["video_prompt"] + " Speak naturally to the supplied audio. "
                                      "Keep non-speaking appendages quiet and preserve the drawing style."}
                    result, receipt = queue.call(AVATAR, args)
                    manifest["requests"].append(receipt)
                    url = result["video"]["url"]
                    media = folder / (stem + ".mp4")
            if mode != "audio" and not media.exists():
                download(url, media)
            manifest["result"] = result
            if mode != "audio":
                manifest["result_url"] = url
        manifest["media_file"] = media.name
        manifest["media_sha256"] = hashlib.sha256(media.read_bytes()).hexdigest()
        atomic_json(manifest_path, manifest)
        return self.response(manifest, media, output_root)

    @staticmethod
    def response(manifest, media, output_root):
        descriptor = media_descriptor(media, output_root)
        if media.suffix == ".mp3":
            ui = {"audio": [descriptor]}
        elif media.suffix == ".mp4":
            ui = {"images": [descriptor], "animated": (True,)}
        elif media.suffix == ".png":
            ui = {"images": [descriptor]}
        else:
            ui = {}
        return {"ui": ui, "result": (json.dumps(manifest["result"], ensure_ascii=False), str(media),
                                      json.dumps(manifest, ensure_ascii=False))}


NODE_CLASS_MAPPINGS = {"VRHSCharacter": VRHSCharacter, "VRHSFalProduction": VRHSFalProduction}
NODE_DISPLAY_NAME_MAPPINGS = {"VRHSCharacter": "VRHS • Choose Character & Performance",
                             "VRHSFalProduction": "VRHS • ElevenLabs Speech + fal Video"}
