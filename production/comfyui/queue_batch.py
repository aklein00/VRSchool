"""Preview and optionally queue one small VRHS batch through a local ComfyUI server."""
import argparse
import copy
import json
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["preview", "audio", "motion_video", "talking_video"], default="preview")
    parser.add_argument("--characters", nargs="+", default=["02-math-yeti"], help="Character IDs, or 'faculty' or 'all'.")
    parser.add_argument("--actions", nargs="+", choices=["idle", "listen", "greet", "teach", "travel", "speak"], default=["greet"])
    parser.add_argument("--line", choices=["welcome", "reassure", "prompt"], default="welcome")
    parser.add_argument("--ettin-head", choices=["A", "B"], default="A")
    parser.add_argument("--duration", choices=["5", "10"], default="5")
    parser.add_argument("--variant", type=int, default=0)
    parser.add_argument("--max-jobs", type=int, default=3)
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--submit", action="store_true", help="Actually queue the listed jobs; paid modes can incur fal charges.")
    args = parser.parse_args()
    parsed = urlparse(args.server)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("This helper queues only to your local ComfyUI server (http://127.0.0.1:8188).")
    registry = json.loads((BASE / "vrhs-characters.json").read_text())
    known = {c["id"]: c for c in registry["characters"]}
    if args.characters == ["faculty"]:
        selected = [c["id"] for c in known.values() if c["role"] != "student"]
    elif args.characters == ["all"]:
        selected = list(known)
    else:
        selected = args.characters
    for char in selected:
        if char not in known:
            parser.error(f"Unknown character: {char}")
    jobs = [(c, a) for c in selected for a in args.actions]
    if len(jobs) > args.max_jobs:
        parser.error(f"{len(jobs)} jobs exceeds --max-jobs {args.max_jobs}; choose fewer or set an explicit larger cap.")
    label = {"preview": "00-preview", "audio": "01-audio", "motion_video": "02-motion-video", "talking_video": "03-talking-video"}[args.mode]
    template = json.loads((BASE / "api-workflows" / (label + ".api.json")).read_text())
    log_path = BASE / "submitted-jobs.jsonl"
    for char, action in jobs:
        graph = copy.deepcopy(template)
        graph["1"]["inputs"].update(character=char, action=action, line=args.line, ettin_head=args.ettin_head,
                                    registry_json=json.dumps(registry, ensure_ascii=False))
        graph["2"]["inputs"].update(duration_seconds=args.duration, generation_variant=args.variant)
        print(f"{args.mode}: {char} / {action} / {args.line} / head {args.ettin_head}")
        if args.submit:
            body = json.dumps({"prompt": graph, "client_id": str(uuid.uuid4())}).encode()
            request = Request(args.server.rstrip("/") + "/prompt", data=body, headers={"Content-Type": "application/json"})
            with urlopen(request, timeout=30) as response:
                result = json.load(response)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"character": char, "action": action, "mode": args.mode, **result}) + "\n")
            print("  queued: " + result["prompt_id"])
    if not args.submit:
        print("Dry run only. Add --submit to queue these jobs. Paid modes use fal credits.")


if __name__ == "__main__":
    main()
