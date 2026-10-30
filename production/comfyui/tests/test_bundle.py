"""Offline checks: actual preview outputs, graph contracts, identity and queue recovery."""
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
PACK = BASE / "ComfyUI-VRHS"
spec = importlib.util.spec_from_file_location("vrhs_production", PACK / "nodes/production.py")
nodes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nodes)
REGISTRY = nodes.read_registry()


class BundleTests(unittest.TestCase):
    def test_private_settings_file_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(nodes, "ROOT", Path(tmp)), patch.dict("os.environ", {}, clear=True):
            (Path(tmp) / "config.ini").write_text("[API]\nELEVENLABS_API_KEY = private%value\nFAL_KEY = private-fal\n")
            self.assertEqual(nodes.api_key("ELEVENLABS_API_KEY"), "private%value")
            self.assertEqual(nodes.api_key("FAL_KEY"), "private-fal")
            with patch.dict("os.environ", {"FAL_KEY": "environment-fal"}):
                self.assertEqual(nodes.api_key("FAL_KEY"), "environment-fal")

    def job(self, record, **overrides):
        params = dict(character=record["id"], action="greet", line="welcome", script_override="", ettin_head="A")
        params.update(overrides)
        return nodes.select_character(REGISTRY, **params)

    def test_cast_canon_and_reference_checksums(self):
        cast = REGISTRY["characters"]
        self.assertEqual(len(cast), 18)
        self.assertEqual(sum(c["role"] != "student" for c in cast), 13)
        self.assertEqual(len({c["id"] for c in cast}), 18)
        for c in cast:
            self.assertTrue(nodes.reference_path(c).exists())
            self.assertEqual(set(c["motion_presets"]), {"idle", "listen", "greet", "teach", "travel", "speak"})
            self.assertTrue(c["sample_dialogue"])
            self.assertTrue(all(c["scripts"].values()))
        by_id = {c["id"]: c for c in cast}
        for cid in ["06-language-arts-dragon", "08-pe-gnoll", "13-headmaster-lich"]:
            self.assertEqual((by_id[cid]["gender"], by_id[cid]["pronouns"]), ("Female", "she/her"))
        self.assertEqual(by_id["09-art-oobleck"]["pronouns"], "they/them")
        self.assertEqual(by_id["12-technology-mimic"]["pronouns"], "they/them")

    def test_all_preview_jobs_write_real_media_and_reuse_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder_paths = types.SimpleNamespace(get_output_directory=lambda: tmp)
            with patch.dict(sys.modules, {"folder_paths": folder_paths}):
                for c in REGISTRY["characters"]:
                    job = self.job(c)
                    output = nodes.VRHSFalProduction().produce(json.dumps(job), mode="preview")
                    manifest = json.loads(output["result"][2])
                    path = Path(output["result"][1])
                    self.assertTrue(path.is_file())
                    self.assertEqual(path.read_bytes(), nodes.reference_path(c).read_bytes())
                    self.assertTrue(manifest["result"]["preview_only"])
                    timestamp = path.stat().st_mtime_ns
                    again = nodes.VRHSFalProduction().produce(json.dumps(job), mode="preview")
                    self.assertEqual(again["result"][1], str(path))
                    self.assertEqual(path.stat().st_mtime_ns, timestamp)

    def test_disabled_sections_do_no_work_even_with_bad_input(self):
        output = nodes.VRHSFalProduction().produce("not even JSON", mode="talking_video", enabled=False)
        self.assertEqual(json.loads(output["result"][0]), {"disabled": True})

    def test_voice_requests_and_ettin_turns(self):
        ettin = REGISTRY["characters"][4]
        a = self.job(ettin, elevenlabs_voice_id="HeadAVoice", elevenlabs_head_b_voice_id="HeadBVoice")
        b = self.job(ettin, ettin_head="B", elevenlabs_voice_id="HeadAVoice", elevenlabs_head_b_voice_id="HeadBVoice")
        self.assertNotEqual(a["voice_prompt"], b["voice_prompt"])
        self.assertNotEqual(a["script"], b["script"])
        self.assertIn("Head B is the only speaker", b["video_prompt"])
        self.assertIn("/HeadAVoice?", nodes.speech_request(a)[0])
        self.assertIn("/HeadBVoice?", nodes.speech_request(b)[0])
        with self.assertRaises(ValueError):
            nodes.speech_request(self.job(ettin, ettin_head="B", elevenlabs_voice_id="OnlyHeadA"))
        for c in REGISTRY["characters"]:
            job = self.job(c, elevenlabs_voice_id="MyExistingVoice")
            endpoint, payload = nodes.speech_request(job)
            self.assertIn("api.elevenlabs.io/v1/text-to-speech/MyExistingVoice?", endpoint)
            self.assertEqual(payload, {"text": job["script"], "model_id": "eleven_multilingual_v2"})
            missing = self.job(c)
            with self.assertRaises(ValueError): nodes.speech_request(missing)
            self.assertIn("voice-id-not-set", nodes.speech_request(missing, require_voice=False)[0])

    def test_ui_and_api_graphs_match_node_contracts(self):
        for path in (BASE / "workflows").glob("*.json"):
            graph = json.loads(path.read_text())
            api_path = BASE / "api-workflows" / (path.stem + ".api.json")
            api = json.loads(api_path.read_text())
            for node in graph["nodes"]:
                if node["type"] == "Note":
                    continue
                cls = nodes.NODE_CLASS_MAPPINGS[node["type"]]
                inputs = cls.INPUT_TYPES()["required"]
                widgets = [key for key, (_, opts) in inputs.items() if not opts.get("forceInput")]
                self.assertEqual(len(node["widgets_values"]), len(widgets), path.name)
                data = api[str(node["id"])]["inputs"]
                self.assertEqual(set(data), set(inputs), path.name)
                for key, value in zip(widgets, node["widgets_values"]):
                    self.assertEqual(data[key], value, (path.name, key))
                    choices = inputs[key][0]
                    if isinstance(choices, list):
                        self.assertIn(value, choices)
            for link_id, source, source_slot, target, target_slot, kind in graph["links"]:
                self.assertEqual(api[str(target)]["inputs"]["character_job_json"], [str(source), source_slot])
        grouped = json.loads((BASE / "workflows/VRHS-All-Characters-Grouped.json").read_text())
        self.assertEqual(len(grouped["groups"]), 18)
        self.assertTrue(any("Headmaster" in g["title"] for g in grouped["groups"]))
        outputs = [n for n in grouped["nodes"] if n["type"] == "VRHSFalProduction"]
        self.assertEqual(sum(n["widgets_values"][0] for n in outputs), 1)
        for output in outputs:
            self.assertEqual(output["widgets_values"][1], "preview")
        for selector in [n for n in grouped["nodes"] if n["type"] == "VRHSCharacter"]:
            self.assertTrue(selector["widgets_values"][2])  # explicit prefilled action
            self.assertTrue(selector["widgets_values"][4])  # explicit sample text

    def test_journal_resumes_without_submitting_twice(self):
        class FakeHandle:
            request_id = "test-request"
            def iter_events(self, **kwargs):
                yield object()
        submissions = []
        fake = types.SimpleNamespace(
            submit=lambda endpoint, arguments: (submissions.append((endpoint, arguments)) or FakeHandle()),
            get_handle=lambda endpoint, request_id: FakeHandle(),
            result=lambda endpoint, request_id: {"audio": {"url": "https://example.com/a.mp3"}},
        )
        fake.SyncClient = lambda **kwargs: fake
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {"fal_client": fake}):
            queue = nodes.FalQueue(Path(tmp))
            one, receipt = queue.call(nodes.MOTION, {"prompt": "Wave"})
            # Simulate a restart after submission but before result was persisted.
            cache = next(Path(tmp).glob("*.json"))
            state = json.loads(cache.read_text())
            state.pop("result")
            cache.write_text(json.dumps(state))
            two, _ = nodes.FalQueue(Path(tmp)).call(nodes.MOTION, {"prompt": "Wave"})
            three, _ = nodes.FalQueue(Path(tmp)).call(nodes.MOTION, {"prompt": "Wave"})
            self.assertEqual(len(submissions), 1)
            self.assertEqual(one, two)
            self.assertEqual(two, three)

    def test_payload_modes_and_local_talking_audio(self):
        calls = []
        class FakeQueue:
            def __init__(self, *args): pass
            def upload(self, path):
                return "https://example.com/uploaded-" + path.suffix[1:]
            def call(self, endpoint, arguments):
                calls.append((endpoint, arguments))
                return {"video": {"url": "https://example.com/result"}}, {"endpoint": endpoint, "request_id": "mock-request", "arguments": arguments}
        def fake_download(url, path): path.write_bytes(b"mock video")
        def fake_speech(job, directory, variant):
            directory.mkdir(parents=True, exist_ok=True)
            audio = directory / "mock.mp3"; audio.write_bytes(b"mock speech")
            return audio, {"provider": "elevenlabs", "request_id": "mock-eleven-request"}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {"folder_paths": types.SimpleNamespace(get_output_directory=lambda: tmp)}), patch.dict("os.environ", {"FAL_KEY": "offline-fal", "ELEVENLABS_API_KEY": "offline-eleven"}), patch.object(nodes, "FalQueue", FakeQueue), patch.object(nodes, "download", fake_download), patch.object(nodes, "elevenlabs_audio", fake_speech):
            job = json.dumps(self.job(REGISTRY["characters"][1], elevenlabs_voice_id="ExistingVoice"))
            for mode in ["audio", "motion_video", "talking_video"]:
                output = nodes.VRHSFalProduction().produce(job, mode=mode)
                self.assertTrue(Path(output["result"][1]).exists())
            avatar_args = next(args for endpoint, args in calls if endpoint == nodes.AVATAR)
            self.assertEqual(avatar_args["audio_url"], "https://example.com/uploaded-mp3")
            self.assertNotIn("duration", avatar_args)
            motion_args = next(args for endpoint, args in calls if endpoint == nodes.MOTION)
            self.assertEqual(motion_args["duration"], "5")
            self.assertEqual(len(calls), 2)  # speech never goes through fal

    def test_elevenlabs_transport_cache_and_secret_handling(self):
        import io
        class Response(io.BytesIO):
            headers = {"Content-Type": "audio/mpeg", "request-id": "eleven-request"}
        requests = []
        def transport(request, timeout):
            requests.append(request)
            return Response(b"audio bytes")
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test-secret"}, clear=True), patch.object(nodes, "urlopen", transport):
            job = self.job(REGISTRY["characters"][1], elevenlabs_voice_id="ExistingVoice")
            audio, receipt = nodes.elevenlabs_audio(job, Path(tmp))
            nodes.elevenlabs_audio(job, Path(tmp))
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0].get_header("Xi-api-key"), "test-secret")
            self.assertEqual(json.loads(requests[0].data)["text"], job["script"])
            self.assertNotIn("test-secret", json.dumps(receipt))
            self.assertEqual(receipt["request_id"], "eleven-request")
            # Audio alone needs neither fal-client nor FAL_KEY.
            with patch.dict(sys.modules, {"folder_paths": types.SimpleNamespace(get_output_directory=lambda: tmp)}):
                result = nodes.VRHSFalProduction().produce(json.dumps(job), mode="audio")
                self.assertEqual(Path(result["result"][1]).suffix, ".mp3")
            nodes.elevenlabs_audio(job, Path(tmp), variant=1)
            self.assertEqual(len(requests), 3)

    def test_talking_video_validates_both_accounts_before_paid_calls(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {"folder_paths": types.SimpleNamespace(get_output_directory=lambda: tmp)}), patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test-key"}, clear=True), patch.object(nodes, "elevenlabs_audio") as speech:
            job = json.dumps(self.job(REGISTRY["characters"][1], elevenlabs_voice_id="ExistingVoice"))
            with self.assertRaisesRegex(ValueError, "FAL_KEY"):
                nodes.VRHSFalProduction().produce(job, mode="talking_video")
            speech.assert_not_called()


if __name__ == "__main__":
    unittest.main()
