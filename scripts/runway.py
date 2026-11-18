#!/usr/bin/env python3
"""Generowanie zdjęć i wideo lamp przez Runway API (bez zależności spoza stdlib).

Klucz API: zwykle dokłada go proxy środowiska (Network secret dla api.dev.runwayml.com).
Lokalnie można go podać w zmiennej środowiskowej RUNWAYML_API_SECRET.

Przykłady:
  # zdjęcie aranżacji z prawdziwym zdjęciem lampy jako referencją
  python3 scripts/runway.py image --ref lampa.jpg --prompt-file prompt.txt --ratio 1024:1024 --out salon.jpg
  # krótkie wideo (5 s) z gotowego zdjęcia
  python3 scripts/runway.py video --image salon.jpg --prompt "slow camera push-in" --out salon.mp4
  # sprawdzenie klucza i stanu kredytów
  python3 scripts/runway.py credits
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.dev.runwayml.com/v1"
VERSION = "2024-11-06"
PROMPT_LIMIT = 1000


def call(method, path, body=None):
    headers = {"X-Runway-Version": VERSION, "Content-Type": "application/json"}
    key = os.environ.get("RUNWAYML_API_SECRET")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Runway API {e.code}: {e.read().decode(errors='replace')}")


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def read_prompt(args):
    text = open(args.prompt_file).read() if args.prompt_file else args.prompt
    text = " ".join(text.split())
    if len(text) > PROMPT_LIMIT:
        sys.exit(f"Prompt ma {len(text)} znaków, Runway przyjmuje max {PROMPT_LIMIT}")
    return text


def wait(task_id):
    print(f"Zadanie Runway: {task_id}", file=sys.stderr)
    while True:
        task = call("GET", f"/tasks/{task_id}")
        status = task["status"]
        if status == "SUCCEEDED":
            return task["output"]
        if status in ("FAILED", "CANCELLED"):
            sys.exit(f"Zadanie {task_id}: {status} {task.get('failure', '')}")
        print(f"  {status}...", file=sys.stderr)
        time.sleep(5)


def save(urls, out):
    root, ext = os.path.splitext(out)
    for i, url in enumerate(urls):
        path = out if len(urls) == 1 else f"{root}-{i + 1}{ext}"
        # adres wyniku jest ważny tylko przez ograniczony czas, więc zapisujemy go od razu
        with open(path + ".url", "w") as f:
            f.write(url + "\n")
        try:
            urllib.request.urlretrieve(url, path)
        except urllib.error.URLError as e:
            sys.exit(f"Nie udało się pobrać {url}: {e}")
        print(path)


def cmd_image(args):
    body = {"model": args.model, "promptText": read_prompt(args), "ratio": args.ratio}
    if args.ref:
        body["referenceImages"] = [
            {"uri": data_uri(p), "tag": f"lamp{i + 1}" if len(args.ref) > 1 else "lamp"}
            for i, p in enumerate(args.ref)
        ]
    task = call("POST", "/text_to_image", body)
    save(wait(task["id"]), args.out)


def cmd_video(args):
    body = {
        "model": args.model,
        "promptImage": data_uri(args.image),
        "promptText": read_prompt(args),
        "ratio": args.ratio,
        "duration": args.duration,
    }
    task = call("POST", "/image_to_video", body)
    save(wait(task["id"]), args.out)


def cmd_credits(_args):
    print(json.dumps(call("GET", "/organization"), indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def prompt_args(sp):
        g = sp.add_mutually_exclusive_group(required=True)
        g.add_argument("--prompt")
        g.add_argument("--prompt-file")
        sp.add_argument("--out", required=True)

    img = sub.add_parser("image", help="zdjęcie z promptu (+ zdjęcia referencyjne)")
    prompt_args(img)
    img.add_argument("--ref", action="append", help="zdjęcie referencyjne lampy (można kilka)")
    img.add_argument("--ratio", default="1024:1024")
    img.add_argument("--model", default="gen4_image")
    img.set_defaults(func=cmd_image)

    vid = sub.add_parser("video", help="wideo ze zdjęcia")
    prompt_args(vid)
    vid.add_argument("--image", required=True)
    vid.add_argument("--ratio", default="1280:720")
    vid.add_argument("--duration", type=int, choices=(5, 10), default=5)
    vid.add_argument("--model", default="gen4_turbo")
    vid.set_defaults(func=cmd_video)

    sub.add_parser("credits", help="sprawdź klucz i kredyty").set_defaults(func=cmd_credits)

    get = sub.add_parser("get", help="pobierz wynik istniejącego zadania")
    get.add_argument("task_id")
    get.add_argument("--out", required=True)
    get.set_defaults(func=lambda a: save(wait(a.task_id), a.out))

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
