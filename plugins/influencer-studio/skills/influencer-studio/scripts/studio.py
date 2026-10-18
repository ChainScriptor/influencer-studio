#!/usr/bin/env python3
"""Influencer Studio helper: WaveSpeed API client + project and budget bookkeeping.

Standard library only (Python 3.8+), so it runs anywhere Claude has Python.
Every command prints one JSON object on stdout; hints go to stderr.
Exit codes: 0 ok, 1 error, 3 blocked by budget or balance, 4 still running.

Commands
  check                       engine status: API key source, balance, projects
  init NAME                   create a project folder with a budget cap
  projects                    list projects with spend vs budget
  status PROJECT              one project's settings and spend
  set PROJECT key=value ...   update fields in project.json
  budget PROJECT [--set USD]  show spend, or change the cap (only when the user says so)
  models [QUERY]              search the live WaveSpeed catalog
  schema MODEL                a model's inputs, defaults and pricing formula
  price MODEL -i k=v ...      quote one run (free)
  quote-plan PLAN.json        quote every item of a plan file (free)
  upload FILE                 upload a local file, print its hosted URL
  run MODEL --project P --step S -i k=v ...   paid generation, budget-guarded
  show ID [--project P --step S]              check, resume or download a prediction
  history [--model M]         predictions from the last 24h

Other engines (Fish Audio runs through its Claude connector, not this script)
  guard PROJECT --credits N   check a planned Fish Audio spend against the credit cap
  record --project P --step S --engine fish --model M --credits N --id ID [URL ...]
                              log a finished generation and download its files
  fileinfo FILE               exact byte size and content type (for upload slots)
  put FILE URL                PUT a file to a presigned upload URL

Inputs: -i key=value is parsed as JSON when it can be (numbers, true/false,
arrays), otherwise kept as a string. A value starting with @ is a local file:
it is uploaded and replaced by its URL, also inside arrays (images='["@a.png"]').
"""

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = os.environ.get("WAVESPEED_BASE_URL", "https://api.wavespeed.ai").rstrip("/")
USER_AGENT = "influencer-studio-skill/1.0"
CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "influencer-studio"
MODELS_TTL_S = 3600
UPLOAD_TTL_S = 24 * 3600
TERMINAL = {"completed", "failed", "cancelled", "timeout", "deleted"}
# The .txt.txt variant is what Windows Explorer creates when file extensions are hidden.
KEY_FILE_NAMES = ("wavespeed-key.txt", "wavespeed_key.txt", "wavespeed-key.txt.txt")
DEFAULT_MODELS = {"video": "bytedance/seedance-2.5/image-to-video"}

STEPS = {
    "character": "01-character",
    "look": "02-look",
    "voice": "03-voice",
    "content": "04-content",
    "production": "05-production",
    "publish": "06-publish",
}
STEP_NUMBERS = {str(i + 1): name for i, name in enumerate(STEPS)}


class StudioError(Exception):
    def __init__(self, message, code=1, **extra):
        super().__init__(message)
        self.code = code
        self.extra = extra


class ApiError(StudioError):
    def __init__(self, status, message):
        super().__init__(f"WaveSpeed API {status}: {message}")
        self.status = status


class NetError(StudioError):
    pass


# ---------------------------------------------------------------- output

def emit(obj):
    sys.stdout.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def hint(text):
    sys.stderr.write(text + "\n")


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def money(x):
    return round(float(x or 0), 4)


# ---------------------------------------------------------------- API key

def _cli_config_paths():
    home = Path.home()
    paths = []
    xdg = os.environ.get("XDG_CONFIG_HOME")
    paths.append(Path(xdg) / "wavespeed-nodejs" / "config.json" if xdg else home / ".config" / "wavespeed-nodejs" / "config.json")
    paths.append(home / "Library" / "Preferences" / "wavespeed-nodejs" / "config.json")
    if os.environ.get("APPDATA"):
        paths.append(Path(os.environ["APPDATA"]) / "wavespeed-nodejs" / "Config" / "config.json")
    return paths


def _search_dirs(root):
    dirs = []
    for start in (Path.cwd(), root):
        if start is None:
            continue
        d = Path(start).resolve()
        for _ in range(4):
            if d not in dirs:
                dirs.append(d)
            if d.parent == d:
                break
            d = d.parent
    return dirs


def find_api_key(root=None):
    """Return (key, source). The key itself is never printed."""
    key = os.environ.get("WAVESPEED_API_KEY", "").strip()
    if key:
        return key, "environment variable WAVESPEED_API_KEY"
    for d in _search_dirs(root):
        for name in KEY_FILE_NAMES:
            p = d / name
            if p.is_file():
                text = p.read_text(encoding="utf-8", errors="ignore").strip()
                m = re.search(r"WAVESPEED_API_KEY\s*=\s*['\"]?([^'\"\s]+)", text)
                key = m.group(1) if m else text.split()[0] if text else ""
                if key:
                    return key, str(p)
        env = d / ".env"
        if env.is_file():
            for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                m = re.match(r"\s*(?:export\s+)?WAVESPEED_API_KEY\s*=\s*['\"]?([^'\"\s#]+)", line)
                if m:
                    return m.group(1), str(env)
    for p in _cli_config_paths():
        try:
            key = json.loads(p.read_text(encoding="utf-8")).get("apiKey", "").strip()
        except (OSError, ValueError, AttributeError):
            continue
        if key:
            return key, f"wavespeed CLI login ({p})"
    return None, None


def require_key(root=None):
    key, _ = find_api_key(root)
    if not key:
        raise StudioError(
            "No WaveSpeed API key found. Ask the user to create a key at https://wavespeed.ai/accesskey "
            "and save it in a file named wavespeed-key.txt in their workspace folder (or run `wavespeed login`, "
            "or set WAVESPEED_API_KEY). Do not ask them to paste the key into the chat.",
            code=1,
            needs_key=True,
        )
    return key


# ---------------------------------------------------------------- HTTP

def _request(method, url, body=None, headers=None, timeout=60, raw=False):
    data = None
    hdrs = {"User-Agent": USER_AGENT}
    hdrs.update(headers or {})
    if body is not None and not raw:
        data = json.dumps(body).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    elif raw:
        data = body
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(), resp.headers
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        msg = text
        try:
            j = json.loads(text)
            msg = j.get("message") or j.get("error") or text
        except ValueError:
            pass
        raise ApiError(e.code, msg[:500])
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        reason = getattr(e, "reason", e)
        raise NetError(
            f"Network error reaching {urllib.parse.urlparse(url).netloc}: {reason}. If this keeps happening, "
            "the sandbox may be blocking that domain: the user must allow it in the app's network settings "
            "(WaveSpeed: api.wavespeed.ai and its file CDN; Fish Audio: *.fish.audio)."
        )


def api(method, path, key, body=None, timeout=60):
    status, payload, _ = _request(
        method, BASE_URL + path, body=body, timeout=timeout,
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        j = json.loads(payload.decode("utf-8") or "{}")
    except ValueError:
        raise ApiError(status, "non-JSON response")
    if isinstance(j, dict) and "code" in j and j["code"] != 200:
        raise ApiError(j["code"], j.get("message") or "error")
    return j.get("data", j) if isinstance(j, dict) else j


# ---------------------------------------------------------------- catalog

def load_models(key, refresh=False):
    cache = CACHE_DIR / "models.json"
    if not refresh:
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            if c.get("base_url") == BASE_URL and time.time() - c["fetched_at"] < MODELS_TTL_S:
                return c["models"]
        except (OSError, ValueError, KeyError):
            pass
    models = api("GET", "/api/v3/models", key, timeout=30)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"fetched_at": time.time(), "base_url": BASE_URL, "models": models}), encoding="utf-8")
    except OSError:
        pass
    return models


def find_model(key, model_id):
    for m in load_models(key):
        if m.get("model_id") == model_id:
            return m
    for m in load_models(key, refresh=True):
        if m.get("model_id") == model_id:
            return m
    return None


def request_schema(meta):
    try:
        return meta["api_schema"]["api_schemas"][0]["request_schema"] or {}
    except (KeyError, IndexError, TypeError):
        return {}


def price_vars(formula):
    if not formula:
        return []
    stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', formula)
    stripped = re.sub(r"'(?:[^'\\]|\\.)*'", "''", stripped)
    out = []
    for m in re.finditer(r"(\$?)([A-Za-z_][A-Za-z0-9_]*)\s*(\()?", stripped):
        dollar, name, call = m.groups()
        if dollar or call or name in {"base_price", "total_price", "true", "false", "null"} or name in out:
            continue
        out.append(name)
    return out


def unpriced_inputs(meta, inputs):
    props = request_schema(meta).get("properties") or {}
    missing = []
    for v in price_vars((meta or {}).get("formula")):
        if inputs.get(v) not in (None, "", []):
            continue
        if isinstance(props.get(v), dict) and "default" in props[v]:
            continue
        missing.append(v)
    return missing


def model_summary(m):
    desc = re.sub(r"\s+", " ", (m.get("description") or "")).strip()
    return {
        "model_id": m.get("model_id"),
        "type": m.get("type"),
        "base_price_usd": m.get("base_price"),
        "description": desc[:160],
    }


# ---------------------------------------------------------------- inputs

def parse_value(text):
    try:
        return json.loads(text)
    except ValueError:
        return text


def parse_inputs(pairs, input_file=None, prompt=None):
    inputs = {}
    if input_file:
        inputs.update(json.loads(Path(input_file).read_text(encoding="utf-8")))
    for pair in pairs or []:
        key, sep, value = pair.partition("=")
        if not sep or not key:
            raise StudioError(f"Bad input {pair!r}: use key=value")
        inputs[key.strip()] = parse_value(value)
    if prompt is not None:
        inputs["prompt"] = prompt
    return inputs


def validate_inputs(meta, inputs):
    schema = request_schema(meta)
    props = schema.get("properties") or {}
    problems = []
    if not props:
        return problems
    for k in inputs:
        if k not in props:
            problems.append(f"unknown input '{k}' (accepted: {', '.join(props)})")
    for k in schema.get("required") or []:
        if inputs.get(k) in (None, ""):
            problems.append(f"missing required input '{k}'")
    for k, v in inputs.items():
        spec = props.get(k)
        if isinstance(spec, dict) and spec.get("enum") and v not in spec["enum"]:
            problems.append(f"'{k}'={v!r} not allowed (choose from {spec['enum']})")
    return problems


def _upload_cache():
    p = CACHE_DIR / "uploads.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    fresh = {k: v for k, v in data.items() if time.time() - v.get("t", 0) < UPLOAD_TTL_S}
    return p, fresh


def upload_file(key, path):
    path = Path(path)
    blob = path.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    cache_path, cache = _upload_cache()
    if digest in cache:
        return cache[digest]["url"]
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    ticket = api("POST", "/api/v3/media/uploads", key, {"filename": path.name, "size": len(blob), "content_type": ctype})
    url = ticket.get("download_url")
    instr = ticket.get("upload") or {}
    if not url or not instr.get("url") or str(instr.get("method", "PUT")).upper() != "PUT":
        raise StudioError(f"Unexpected upload ticket: {json.dumps(ticket)[:300]}")
    headers = dict(instr.get("headers") or {})
    lower = {k.lower() for k in headers}
    if "content-type" not in lower:
        headers["Content-Type"] = ctype
    if "content-length" not in lower:
        headers["Content-Length"] = str(len(blob))
    _request("PUT", instr["url"], body=blob, headers=headers, timeout=300, raw=True)
    cache[digest] = {"url": url, "t": time.time()}
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache), encoding="utf-8")
    except OSError:
        pass
    return url


def resolve_files(key, value, base_dirs, uploaded):
    """Replace every '@path' string with the hosted URL of that file."""
    if isinstance(value, dict):
        return {k: resolve_files(key, v, base_dirs, uploaded) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_files(key, v, base_dirs, uploaded) for v in value]
    if isinstance(value, str) and value.startswith("@") and len(value) > 1:
        rel = value[1:]
        for base in base_dirs:
            p = (Path(base) / rel) if not Path(rel).is_absolute() else Path(rel)
            if p.is_file():
                url = upload_file(key, p)
                uploaded[str(p)] = url
                return url
        raise StudioError(f"File not found for {value} (looked in: {', '.join(str(b) for b in base_dirs)})")
    return value


def quote(key, model, inputs):
    d = api("POST", "/api/v3/model/price", key, {"model_id": model, "inputs": inputs})
    disc = d.get("discounted_price") or 0
    return money(disc if disc > 0 else d.get("price") or 0)


# ---------------------------------------------------------------- projects

def studio_root(arg=None):
    return Path(arg or os.environ.get("INFLUENCER_STUDIO_HOME") or Path.cwd() / "influencer-studio").resolve()


def slugify(text):
    # Keep letters of any script, so a Greek or Cyrillic title stays readable and distinct.
    s = re.sub(r"[\W_]+", "-", text.lower()).strip("-")
    return s or "project"


def resolve_project(arg, root=None):
    p = Path(arg)
    candidates = [p, studio_root(root) / arg]
    for c in candidates:
        if (c / "project.json").is_file():
            return c.resolve()
    raise StudioError(f"No project found at {arg!r}. Run `studio.py projects` to list projects or `init` to create one.")


def load_project(pdir):
    return json.loads((pdir / "project.json").read_text(encoding="utf-8"))


def save_project(pdir, data):
    data["updated_at"] = now_iso()
    (pdir / "project.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ledger_append(pdir, entry):
    entry = {"ts": now_iso(), **entry}
    with open(pdir / "ledger.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def ledger_state(pdir):
    """Fold the append-only ledger into one record per prediction."""
    tasks = {}
    path = pdir / "ledger.jsonl"
    if not path.is_file():
        return tasks
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not e.get("id"):
            continue
        t = tasks.setdefault(e["id"], {"id": e["id"]})
        for k in ("model", "step", "label", "cost_usd", "engine", "credits", "view_url"):
            if k in e:
                t[k] = e[k]
        t["status"] = e.get("event")
        if e.get("files"):
            t["files"] = e["files"]
    return tasks


def spend_summary(pdir, project=None):
    project = project or load_project(pdir)
    tasks = ledger_state(pdir)
    # Failed tasks are refunded by WaveSpeed, so they don't count against the cap.
    counted = [t for t in tasks.values() if t.get("status") != "failed"]
    spent = money(sum(t.get("cost_usd", 0) for t in counted))
    credits = int(sum(t.get("credits", 0) for t in counted))
    by_step, credits_by_step = {}, {}
    for t in counted:
        step = t.get("step", "?")
        if t.get("cost_usd"):
            by_step[step] = money(by_step.get(step, 0) + t["cost_usd"])
        if t.get("credits"):
            credits_by_step[step] = int(credits_by_step.get(step, 0) + t["credits"])
    budget = money(project.get("budget_usd", 0))
    cap = project.get("fish_credit_cap")
    return {
        "spent_usd": spent,
        "budget_usd": budget,
        "remaining_usd": money(budget - spent),
        "by_step": by_step,
        "fish_credits_spent": credits,
        "fish_credit_cap": cap,
        "fish_credits_remaining": (int(cap) - credits) if cap is not None else None,
        "fish_credits_by_step": credits_by_step,
        "runs": len(counted),
        "failed_runs": len(tasks) - len(counted),
        "pending_runs": [t["id"] for t in counted if t.get("status") in ("submitted", "pending")],
        "note": "USD is the sum of WaveSpeed price quotes; credits are what Fish Audio charged. "
                "The providers' dashboards show the exact charges.",
    }


def norm_step(step):
    s = str(step).strip().lower()
    s = STEP_NUMBERS.get(s, s)
    if s not in STEPS:
        raise StudioError(f"Unknown step {step!r}: use 1-6 or one of {', '.join(STEPS)}")
    return s


# ---------------------------------------------------------------- predictions

def fetch_prediction(key, pid):
    for attempt in range(6):
        try:
            return api("GET", f"/api/v3/predictions/{pid}/result", key, timeout=30)
        except NetError:
            if attempt == 5:
                raise
        except ApiError as e:
            if e.status not in (429, 500, 502, 503, 504) or attempt == 5:
                raise
        time.sleep(2 * (attempt + 1))


def wait_for(key, pid, max_wait):
    start = time.time()
    delay = 2
    while True:
        item = fetch_prediction(key, pid)
        status = item.get("status")
        if status in TERMINAL:
            return item
        if time.time() - start > max_wait:
            return item
        time.sleep(delay)
        delay = min(delay + 1, 6)


def output_urls(item):
    outs = item.get("outputs") or []
    urls = [o for o in outs if isinstance(o, str)]
    for o in outs:
        if isinstance(o, dict):
            urls.extend(v for v in o.values() if isinstance(v, str) and v.startswith("http"))
    return urls


def _ext_for(url, ctype):
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lstrip(".").lower()
    if suffix and len(suffix) <= 5:
        return suffix
    guessed = mimetypes.guess_extension((ctype or "").split(";")[0].strip()) if ctype else None
    return (guessed or ".bin").lstrip(".")


def download_outputs(urls, pdir, step, pid, label, template=None):
    files = []
    base = pdir / STEPS[step]
    for i, url in enumerate(urls, 1):
        _, blob, headers = _request("GET", url, timeout=300)
        ext = _ext_for(url, headers.get("Content-Type"))
        if template:
            name = template.format(index=i, ext=ext, id=pid[:8], label=label or "out")
            if len(urls) > 1 and "{index}" not in template:
                stem, dot, tail = name.rpartition(".")
                name = f"{stem}-{i}.{tail}" if dot else f"{name}-{i}"
            target = (pdir / name) if not Path(name).is_absolute() else Path(name)
        else:
            stem = label or "out"
            suffix = f"-{i}" if len(urls) > 1 else ""
            target = base / f"{stem}-{pid[:8]}{suffix}.{ext}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        try:
            files.append(str(target.resolve().relative_to(pdir)))
        except ValueError:
            files.append(str(target))
    return files


def find_recent_task(key, model, since, prompt):
    """After an ambiguous submit, look for the task the server may have created."""
    body = {
        "page": 1,
        "page_size": 20,
        "model": model,
        "created_after": since,
        "created_before": now_iso(),
    }
    items = (api("POST", "/api/v3/predictions", key, body) or {}).get("items") or []
    if prompt:
        same = [i for i in items if (i.get("inputs") or i.get("input") or {}).get("prompt") == prompt]
        if same:
            items = same
    return items


# ---------------------------------------------------------------- commands

def cmd_check(a):
    root = studio_root(a.root)
    key, source = find_api_key(root)
    out = {
        "api_key": "found" if key else "missing",
        "api_key_source": source,
        "studio_root": str(root),
        "projects": [],
    }
    if key:
        out["api_key_hint"] = f"...{key[-4:]}" if len(key) > 8 else "set"
        try:
            out["balance_usd"] = money(api("GET", "/api/v3/balance", key).get("balance"))
            out["engine"] = "ready"
        except StudioError as e:
            out["engine"] = "error"
            out["engine_error"] = str(e)
    else:
        out["engine"] = "needs_key"
        out["how_to_fix"] = (
            "Create an API key at https://wavespeed.ai/accesskey, then save it as a one-line file "
            "named wavespeed-key.txt in the workspace folder."
        )
    out["projects"] = _list_projects(root)
    emit(out)


def _list_projects(root):
    rows = []
    if root.is_dir():
        for pj in sorted(root.glob("*/project.json")):
            pdir = pj.parent
            try:
                p = load_project(pdir)
                s = spend_summary(pdir, p)
            except (OSError, ValueError):
                continue
            rows.append({
                "slug": pdir.name,
                "name": p.get("name"),
                "current_step": p.get("current_step"),
                "platform": p.get("platform"),
                "spent_usd": s["spent_usd"],
                "budget_usd": s["budget_usd"],
                "updated_at": p.get("updated_at"),
                "path": str(pdir),
            })
    return rows


def cmd_init(a):
    root = studio_root(a.root)
    slug = slugify(a.slug or a.name)
    pdir = root / slug
    if (pdir / "project.json").exists():
        raise StudioError(f"Project {slug!r} already exists at {pdir}. Pick another name or continue it.")
    for d in STEPS.values():
        (pdir / d).mkdir(parents=True, exist_ok=True)
    project = {
        "name": a.name,
        "slug": slug,
        "created_at": now_iso(),
        "platform": a.platform,
        "budget_usd": money(a.budget),
        "fish_credit_cap": a.credit_cap,
        "starting_point": a.start,
        "current_step": "character",
        "language": a.language,
        "character": {},
        "models": dict(DEFAULT_MODELS),
        "voice": {},
        "episodes": [],
    }
    save_project(pdir, project)
    emit({"created": str(pdir), "project": project, "folders": list(STEPS.values())})


def cmd_projects(a):
    root = studio_root(a.root)
    emit({"studio_root": str(root), "projects": _list_projects(root)})


def cmd_status(a):
    pdir = resolve_project(a.project, a.root)
    p = load_project(pdir)
    emit({"path": str(pdir), "project": p, "spend": spend_summary(pdir, p)})


def cmd_set(a):
    pdir = resolve_project(a.project, a.root)
    p = load_project(pdir)
    for pair in a.pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise StudioError(f"Bad field {pair!r}: use key=value (dotted keys nest, e.g. models.image=...)")
        if key == "budget_usd":
            raise StudioError("Change the budget with `budget PROJECT --set USD`, and only when the user asks.")
        if key == "current_step":
            value = json.dumps(norm_step(value))
        node = p
        parts = key.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = parse_value(value)
    save_project(pdir, p)
    emit({"updated": str(pdir / "project.json"), "project": p})


def cmd_budget(a):
    pdir = resolve_project(a.project, a.root)
    p = load_project(pdir)
    if a.set is not None:
        old = p.get("budget_usd")
        p["budget_usd"] = money(a.set)
        save_project(pdir, p)
        ledger_append(pdir, {"event": "budget_changed", "id": None, "from_usd": old, "to_usd": p["budget_usd"]})
    if a.set_credits is not None:
        old = p.get("fish_credit_cap")
        p["fish_credit_cap"] = a.set_credits
        save_project(pdir, p)
        ledger_append(pdir, {"event": "credit_cap_changed", "id": None, "from": old, "to": a.set_credits})
    emit(spend_summary(pdir, p))


def cmd_models(a):
    key = require_key(a.root)
    models = load_models(key, refresh=a.refresh)
    words = [w.lower() for w in (a.query or "").split()]
    rows = []
    for m in models:
        hay = " ".join(str(m.get(k) or "") for k in ("model_id", "name", "description", "type")).lower()
        if words and not all(w in hay for w in words):
            continue
        if a.type and a.type.lower() not in (m.get("type") or "").lower():
            continue
        rows.append(m)
    rows.sort(key=lambda m: (m.get("sort_order") or 10**9, m.get("model_id") or ""))
    types = sorted({m.get("type") for m in models if m.get("type")})
    emit({"count": len(rows), "models": [model_summary(m) for m in rows[: a.limit]], "all_types": types})


def cmd_schema(a):
    key = require_key(a.root)
    meta = find_model(key, a.model)
    if not meta:
        raise StudioError(f"Model {a.model!r} is not in the WaveSpeed catalog. Search with `models <words>`.")
    schema = request_schema(meta)
    props = {}
    for name, spec in (schema.get("properties") or {}).items():
        spec = spec if isinstance(spec, dict) else {}
        props[name] = {k: spec[k] for k in ("type", "default", "enum", "minimum", "maximum", "items") if k in spec}
        if spec.get("description"):
            props[name]["description"] = re.sub(r"\s+", " ", spec["description"])[:200]
    emit({
        **model_summary(meta),
        "required": schema.get("required") or [],
        "inputs": props,
        "pricing_formula": meta.get("formula"),
        "price_drivers": price_vars(meta.get("formula")),
    })


def cmd_price(a):
    key = require_key(a.root)
    inputs = parse_inputs(a.input, a.input_file, a.prompt)
    uploaded = {}
    if a.upload:
        inputs = resolve_files(key, inputs, [Path.cwd()], uploaded)
    meta = find_model(key, a.model)
    if not meta:
        raise StudioError(f"Model {a.model!r} is not in the WaveSpeed catalog. Search with `models <words>`.")
    cost = quote(key, a.model, inputs)
    missing = unpriced_inputs(meta, inputs)
    emit({
        "model": a.model,
        "quote_usd": cost,
        "unpriced_inputs": missing,
        "warning": (f"Priced without {', '.join(missing)}: this is the floor, the real run can cost more."
                    if missing else None),
        "uploaded": uploaded,
    })


def cmd_quote_plan(a):
    key = require_key(a.root)
    plan_doc = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    plans = plan_doc.get("plans") or [plan_doc]
    result = []
    for plan in plans:
        rows, total, warnings = [], 0.0, []
        for item in plan.get("items", []):
            count = item.get("count", 1)
            row = {"step": item.get("step"), "what": item.get("what"), "model": item.get("model"), "count": count}
            if "unit_usd" in item:
                unit = money(item["unit_usd"])
                row["source"] = "manual estimate"
            else:
                meta = find_model(key, item["model"])
                if not meta:
                    warnings.append(f"{item['model']}: not in catalog, pick a replacement with `models`")
                    row["error"] = "model not found"
                    rows.append(row)
                    continue
                inputs = item.get("inputs", {})
                unit = quote(key, item["model"], inputs)
                missing = unpriced_inputs(meta, inputs)
                if missing:
                    warnings.append(f"{item['model']}: priced without {', '.join(missing)}, real cost can be higher")
                row["source"] = "live quote"
            row["unit_usd"] = unit
            row["subtotal_usd"] = money(unit * count)
            total += unit * count
            rows.append(row)
        result.append({"plan": plan.get("name", "plan"), "items": rows, "total_usd": money(total),
                       "warnings": list(dict.fromkeys(warnings))})
    emit({"plans": result})


def cmd_upload(a):
    key = require_key(a.root)
    emit({"file": a.file, "url": upload_file(key, a.file)})


def cmd_guard(a):
    pdir = resolve_project(a.project, a.root)
    s = spend_summary(pdir)
    keys = ("fish_credits_spent", "fish_credit_cap", "fish_credits_remaining")
    cap = s["fish_credit_cap"]
    if cap is not None and s["fish_credits_spent"] + a.credits > cap:
        raise StudioError(
            f"Credit cap reached: this needs {a.credits} credits, {s['fish_credits_remaining']} of {cap} are left. "
            "Ask the user whether to raise the cap (`budget PROJECT --set-credits N`) or choose a cheaper option.",
            code=3, **{k: s[k] for k in keys},
        )
    emit({"ok": True, "credits": a.credits, **{k: s[k] for k in keys}})


def cmd_record(a):
    pdir = resolve_project(a.project, a.root)
    step = norm_step(a.step)
    label = slugify(a.label) if a.label else slugify(a.model.split("/")[-1])
    known = ledger_state(pdir).get(a.id, {})
    if known.get("status") == "completed" and known.get("files"):
        emit({"status": "already recorded", "id": a.id, "files": known["files"]})
        return
    files, warning = [], None
    if a.urls:
        try:
            files = download_outputs(a.urls, pdir, step, a.id, label, a.out)
        except StudioError as e:
            warning = f"{e} The run is logged without files; run `record` again with the same --id later, or use the view URL."
    if not known:
        # Logged once per id, so recording again after a failed download never double-counts the cost.
        entry = {"event": "submitted", "id": a.id, "engine": a.engine, "model": a.model, "step": step, "label": label,
                 "credits": a.credits}
        if a.usd:
            entry["cost_usd"] = money(a.usd)
        ledger_append(pdir, entry)
    done = {"event": "completed", "id": a.id, "outputs": a.urls, "files": files}
    if a.view_url:
        done["view_url"] = a.view_url
    ledger_append(pdir, done)
    s = spend_summary(pdir)
    emit({"status": "recorded", "id": a.id, "step": step, "files": files, "warning": warning,
          **{k: s[k] for k in ("fish_credits_spent", "fish_credit_cap", "fish_credits_remaining", "spent_usd", "budget_usd")}})


def cmd_fileinfo(a):
    p = Path(a.file)
    if not p.is_file():
        raise StudioError(f"File not found: {a.file}")
    emit({"file": str(p.resolve()), "file_name": p.name, "bytes": p.stat().st_size,
          "content_type": mimetypes.guess_type(p.name)[0]})


def cmd_put(a):
    p = Path(a.file)
    blob = p.read_bytes()
    headers = {"Content-Type": a.content_type or mimetypes.guess_type(p.name)[0] or "application/octet-stream",
               "Content-Length": str(len(blob))}
    for h in a.header:
        k, sep, v = h.partition(":")
        if not sep:
            raise StudioError(f"Bad header {h!r}: use Name: value")
        headers[k.strip()] = v.strip()
    status, _, _ = _request("PUT", a.url, body=blob, headers=headers, timeout=600, raw=True)
    emit({"uploaded": str(p), "bytes": len(blob), "http_status": status})


def cmd_run(a):
    pdir = resolve_project(a.project, a.root)
    key = require_key(pdir)
    project = load_project(pdir)
    step = norm_step(a.step)
    meta = find_model(key, a.model)
    if not meta:
        raise StudioError(f"Model {a.model!r} is not in the WaveSpeed catalog. Search with `models <words>`; never guess ids.")
    inputs = parse_inputs(a.input, a.input_file, a.prompt)
    uploaded = {}
    inputs = resolve_files(key, inputs, [Path.cwd(), pdir], uploaded)
    problems = validate_inputs(meta, inputs)
    if problems:
        raise StudioError("Inputs rejected before spending anything: " + "; ".join(problems), schema_hint=f"studio.py schema {a.model}")

    cost = quote(key, a.model, inputs)
    spend = spend_summary(pdir, project)
    if spend["spent_usd"] + cost > spend["budget_usd"] + 1e-9:
        raise StudioError(
            f"Budget cap reached: this run costs ~${cost}, ${spend['remaining_usd']} of ${spend['budget_usd']} is left. "
            "Ask the user whether to raise the cap (`budget PROJECT --set USD`) or choose a cheaper option.",
            code=3, quote_usd=cost, **{k: spend[k] for k in ("spent_usd", "budget_usd", "remaining_usd")},
        )
    balance = money(api("GET", "/api/v3/balance", key).get("balance"))
    if balance < cost:
        raise StudioError(
            f"WaveSpeed balance is ${balance}, this run needs ~${cost}. The user can top up at https://wavespeed.ai/top-up.",
            code=3, quote_usd=cost, balance_usd=balance,
        )
    if a.dry_run:
        emit({"dry_run": True, "model": a.model, "step": step, "quote_usd": cost, "inputs": inputs,
              "unpriced_inputs": unpriced_inputs(meta, inputs), "balance_usd": balance, **spend})
        return

    label = slugify(a.label) if a.label else slugify(a.model.split("/")[-1])
    submitted_at = now_iso()
    try:
        sub = api("POST", f"/api/v3/{a.model}", key, inputs, timeout=90)
        pid = sub.get("id")
    except (NetError, ApiError) as e:
        # A timeout or gateway error does not mean the task failed: it may exist
        # server-side and be charged. Look for it instead of resubmitting blindly.
        if isinstance(e, ApiError) and e.status not in (500, 502, 503, 504):
            raise
        time.sleep(5)
        found = find_recent_task(key, a.model, submitted_at, inputs.get("prompt"))
        if len(found) != 1:
            raise StudioError(
                "Submit got no clear response. " + (
                    "No matching task shows up in history, so most likely nothing was charged: "
                    "run it once more, and only once."
                    if not found else
                    f"{len(found)} recent tasks match; check them with `show ID` before running again."),
                candidates=[f.get("id") for f in found],
            )
        pid = found[0].get("id")
    if not pid:
        raise StudioError(f"WaveSpeed returned no prediction id: {json.dumps(sub)[:300]}")
    ledger_append(pdir, {"event": "submitted", "id": pid, "model": a.model, "step": step, "label": label,
                         "cost_usd": cost, "inputs": inputs})

    item = wait_for(key, pid, a.max_wait)
    _finish(pdir, key, item, pid, step, label, a.out, cost)


def _finish(pdir, key, item, pid, step, label, template, cost):
    status = item.get("status")
    if status not in TERMINAL:
        ledger_append(pdir, {"event": "pending", "id": pid})
        emit({"status": status or "processing", "id": pid,
              "next": f"Still generating. Check again with: studio.py show {pid} --project {pdir} --step {step}"
                      + (f" --label {label}" if label else "")})
        sys.exit(4)
    if status != "completed":
        ledger_append(pdir, {"event": "failed", "id": pid, "error": item.get("error")})
        raise StudioError(f"Generation {status}: {item.get('error') or 'no details'} (id {pid}). Failed runs are refunded.",
                          id=pid)
    urls = output_urls(item)
    files = download_outputs(urls, pdir, step, pid, label, template) if urls else []
    ledger_append(pdir, {"event": "completed", "id": pid, "outputs": urls, "files": files})
    spend = spend_summary(pdir)
    emit({"status": "completed", "id": pid, "step": step, "cost_usd": cost, "files": files, "urls": urls,
          "spent_usd": spend["spent_usd"], "budget_usd": spend["budget_usd"], "remaining_usd": spend["remaining_usd"]})


def cmd_show(a):
    key = require_key(a.root)
    item = fetch_prediction(key, a.id) if not a.wait else wait_for(key, a.id, a.max_wait)
    if not a.project:
        emit({"id": a.id, "status": item.get("status"), "outputs": output_urls(item), "error": item.get("error"),
              "model": item.get("model")})
        return
    pdir = resolve_project(a.project, a.root)
    known = ledger_state(pdir).get(a.id, {})
    if known.get("status") == "completed" and known.get("files"):
        emit({"id": a.id, "status": "completed", "files": known["files"], "note": "already downloaded"})
        return
    step = norm_step(a.step or known.get("step") or "production")
    label = slugify(a.label) if a.label else known.get("label")
    cost = known.get("cost_usd")
    if not known:
        # A task we never logged (e.g. found through `history`): log it so the budget stays honest.
        model = item.get("model")
        cost = 0.0
        try:
            cost = quote(key, model, item.get("inputs") or item.get("input") or {}) if model else 0.0
        except StudioError:
            hint("Could not price this task; it is logged at $0. Check the WaveSpeed dashboard.")
        ledger_append(pdir, {"event": "submitted", "id": a.id, "model": model, "step": step, "label": label,
                             "cost_usd": cost, "adopted": True})
    _finish(pdir, key, item, a.id, step, label, a.out, cost or 0)


def cmd_history(a):
    key = require_key(a.root)
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=a.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = {"page": 1, "page_size": a.limit, "created_after": since, "created_before": now_iso()}
    if a.model:
        body["model"] = a.model
    data = api("POST", "/api/v3/predictions", key, body) or {}
    items = [{"id": i.get("id"), "model": i.get("model"), "status": i.get("status"), "created_at": i.get("created_at")}
             for i in data.get("items") or []]
    emit({"items": items})


# ---------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(prog="studio.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", help="studio folder holding the projects (default: ./influencer-studio)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def inputs(sp):
        sp.add_argument("-i", "--input", action="append", default=[], metavar="KEY=VALUE")
        sp.add_argument("-p", "--prompt")
        sp.add_argument("--input-file", help="JSON file with the full input object")

    sub.add_parser("check").set_defaults(fn=cmd_check)

    sp = sub.add_parser("init")
    sp.add_argument("name")
    sp.add_argument("--slug")
    sp.add_argument("--budget", type=float, default=10.0)
    sp.add_argument("--platform", default="tiktok-reels-shorts")
    sp.add_argument("--start", default="scratch", help="scratch | photo | existing")
    sp.add_argument("--language", default="en", help="language the character speaks")
    sp.add_argument("--credit-cap", type=int, help="optional cap on Fish Audio credits for this project")
    sp.set_defaults(fn=cmd_init)

    sub.add_parser("projects").set_defaults(fn=cmd_projects)

    sp = sub.add_parser("status")
    sp.add_argument("project")
    sp.set_defaults(fn=cmd_status)

    sp = sub.add_parser("set")
    sp.add_argument("project")
    sp.add_argument("pairs", nargs="+", metavar="KEY=VALUE")
    sp.set_defaults(fn=cmd_set)

    sp = sub.add_parser("budget")
    sp.add_argument("project")
    sp.add_argument("--set", type=float, help="new cap in USD (only when the user asked for it)")
    sp.add_argument("--set-credits", type=int, help="new Fish Audio credit cap (only when the user asked for it)")
    sp.set_defaults(fn=cmd_budget)

    sp = sub.add_parser("models")
    sp.add_argument("query", nargs="?")
    sp.add_argument("-t", "--type", help="e.g. text-to-image, image-to-video, text-to-audio")
    sp.add_argument("--limit", type=int, default=25)
    sp.add_argument("--refresh", action="store_true")
    sp.set_defaults(fn=cmd_models)

    sp = sub.add_parser("schema")
    sp.add_argument("model")
    sp.set_defaults(fn=cmd_schema)

    sp = sub.add_parser("price")
    sp.add_argument("model")
    inputs(sp)
    sp.add_argument("--upload", action="store_true", help="upload @files for an exact media-based quote")
    sp.set_defaults(fn=cmd_price)

    sp = sub.add_parser("quote-plan")
    sp.add_argument("plan")
    sp.set_defaults(fn=cmd_quote_plan)

    sp = sub.add_parser("upload")
    sp.add_argument("file")
    sp.set_defaults(fn=cmd_upload)

    sp = sub.add_parser("guard")
    sp.add_argument("project")
    sp.add_argument("--credits", type=int, required=True, help="credits the next Fish Audio generation will cost")
    sp.set_defaults(fn=cmd_guard)

    sp = sub.add_parser("record")
    sp.add_argument("urls", nargs="*", metavar="URL", help="result URLs to download into the project")
    sp.add_argument("--project", required=True)
    sp.add_argument("--step", required=True)
    sp.add_argument("--engine", default="fish")
    sp.add_argument("--model", required=True)
    sp.add_argument("--id", required=True, help="the engine's generation id")
    sp.add_argument("--credits", type=int, default=0, help="credits charged")
    sp.add_argument("--usd", type=float, help="cost in USD, when the engine bills in dollars")
    sp.add_argument("--label")
    sp.add_argument("-o", "--out", help="output path template relative to the project")
    sp.add_argument("--view-url", help="where the user can see the result if the download fails")
    sp.set_defaults(fn=cmd_record)

    sp = sub.add_parser("fileinfo")
    sp.add_argument("file")
    sp.set_defaults(fn=cmd_fileinfo)

    sp = sub.add_parser("put")
    sp.add_argument("file")
    sp.add_argument("url")
    sp.add_argument("--content-type")
    sp.add_argument("--header", action="append", default=[], metavar="'Name: value'")
    sp.set_defaults(fn=cmd_put)

    sp = sub.add_parser("run")
    sp.add_argument("model")
    sp.add_argument("--project", required=True)
    sp.add_argument("--step", required=True, help="1-6 or character|look|voice|content|production|publish")
    inputs(sp)
    sp.add_argument("--label", help="short name used in output file names")
    sp.add_argument("-o", "--out", help="output path template relative to the project, e.g. 02-look/master.{ext}")
    sp.add_argument("--max-wait", type=int, default=480, help="seconds to wait before handing back a pending id")
    sp.add_argument("--dry-run", action="store_true", help="validate, quote and check budget without spending")
    sp.set_defaults(fn=cmd_run)

    sp = sub.add_parser("show")
    sp.add_argument("id")
    sp.add_argument("--project")
    sp.add_argument("--step")
    sp.add_argument("--label")
    sp.add_argument("-o", "--out")
    sp.add_argument("--wait", action="store_true")
    sp.add_argument("--max-wait", type=int, default=480)
    sp.set_defaults(fn=cmd_show)

    sp = sub.add_parser("history")
    sp.add_argument("--model")
    sp.add_argument("--hours", type=int, default=24)
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(fn=cmd_history)
    return p


def main():
    # Windows consoles and pipes default to a legacy code page that can't print Greek and other scripts.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args()
    try:
        args.fn(args)
    except StudioError as e:
        emit({"error": str(e), **e.extra})
        sys.exit(e.code)


if __name__ == "__main__":
    main()
