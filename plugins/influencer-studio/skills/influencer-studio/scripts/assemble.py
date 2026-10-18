#!/usr/bin/env python3
"""Assemble generated clips (and stills) into one vertical short with ffmpeg.

  assemble.py --out final.mp4 shot1.mp4 shot2.png shot3.mp4
      [--voice vo.mp3] [--music bed.mp3] [--music-volume 0.12] [--clip-volume 1.0]
      [--mute-clips] [--still-seconds 2.5] [--srt captions.srt]
      [--size 1080x1920] [--fps 30] [--fit crop|pad]
      [--cover cover.jpg] [--cover-at 0.5]
  assemble.py --probe file.mp4 [file2 ...]

Clips are scaled to the target size (crop fills the frame, pad letterboxes),
joined in order, mixed with the optional voice and music, loudness-normalised
to -14 LUFS (the level TikTok, Reels and Shorts play at), and captions from an
.srt are burned in when the ffmpeg build supports it. Prints JSON.
Needs ffmpeg on PATH, or `pip install imageio-ffmpeg`.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STILL_EXT = {".png", ".jpg", ".jpeg", ".webp"}
CAPTION_STYLE = (
    "FontName=Arial,FontSize=13,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
    "BorderStyle=1,Outline=2.5,Shadow=0,Alignment=2,MarginV=70"
)


def fail(msg):
    print(json.dumps({"error": msg}, indent=2))
    sys.exit(1)


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        fail("ffmpeg not found. Install it with `pip install imageio-ffmpeg` (bundles ffmpeg) and run again.")


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stderr


def probe(ff, path):
    _, err = run([ff, "-hide_banner", "-i", str(path)])
    info = {"file": str(path), "duration_s": None, "size": None, "has_audio": " Audio:" in err}
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", err)
    if m:
        h, mi, s = m.groups()
        info["duration_s"] = round(int(h) * 3600 + int(mi) * 60 + float(s), 2)
    m = re.search(r"Video: .*?(\d{2,5})x(\d{2,5})", err)
    if m:
        info["size"] = f"{m.group(1)}x{m.group(2)}"
    return info


def video_filter(w, h, fps, fit):
    if fit == "pad":
        geo = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black"
    else:
        geo = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    return f"{geo},setsar=1,fps={fps},format=yuv420p"


def normalize(ff, src, dst, a, w, h):
    src = Path(src)
    is_still = src.suffix.lower() in STILL_EXT
    info = probe(ff, src)
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error"]
    if is_still:
        cmd += ["-loop", "1", "-t", str(a.still_seconds), "-i", str(src)]
    else:
        cmd += ["-i", str(src)]
    use_clip_audio = info["has_audio"] and not is_still and not a.mute_clips
    if not use_clip_audio:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    cmd += ["-filter_complex", f"[0:v]{video_filter(w, h, a.fps, a.fit)}[v]", "-map", "[v]",
            "-map", "0:a:0" if use_clip_audio else "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", str(dst)]
    code, err = run(cmd)
    if code != 0:
        fail(f"ffmpeg could not process {src}: {err.strip()[-600:]}")
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="clips and stills, in order")
    ap.add_argument("--probe", action="store_true", help="only report duration, size and audio of the inputs")
    ap.add_argument("--out")
    ap.add_argument("--voice")
    ap.add_argument("--music")
    ap.add_argument("--music-volume", type=float, default=0.12)
    ap.add_argument("--clip-volume", type=float, default=1.0)
    ap.add_argument("--mute-clips", action="store_true", help="drop the clips' own audio")
    ap.add_argument("--still-seconds", type=float, default=2.5)
    ap.add_argument("--srt")
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--fit", choices=["crop", "pad"], default="crop")
    ap.add_argument("--cover")
    ap.add_argument("--cover-at", type=float, default=0.5)
    a = ap.parse_args()

    ff = find_ffmpeg()
    for f in a.inputs + [x for x in (a.voice, a.music, a.srt) if x]:
        if not Path(f).is_file():
            fail(f"File not found: {f}")
    if a.probe:
        print(json.dumps([probe(ff, f) for f in a.inputs], indent=2))
        return
    if not a.out:
        fail("--out is required")
    w, h = (int(x) for x in a.size.lower().split("x"))
    warnings = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        parts, infos = [], []
        for i, src in enumerate(a.inputs):
            dst = tmp / f"part{i:03d}.mp4"
            infos.append(normalize(ff, src, dst, a, w, h))
            parts.append(dst)
        (tmp / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in parts))
        code, err = run([ff, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                         "-i", "list.txt", "-c", "copy", "joined.mp4"], cwd=tmp)
        if code != 0:
            fail(f"ffmpeg concat failed: {err.strip()[-600:]}")
        video_len = probe(ff, tmp / "joined.mp4")["duration_s"] or 0

        cmd = [ff, "-y", "-hide_banner", "-loglevel", "error", "-i", "joined.mp4"]
        mix = [f"[0:a]volume={a.clip_volume}[a0]"]
        labels = ["[a0]"]
        n = 1
        if a.voice:
            shutil.copy(a.voice, tmp / ("voice" + Path(a.voice).suffix))
            cmd += ["-i", "voice" + Path(a.voice).suffix]
            mix.append(f"[{n}:a]volume=1.0[a{n}]")
            labels.append(f"[a{n}]")
            voice_len = probe(ff, a.voice)["duration_s"] or 0
            if voice_len > video_len + 0.3:
                warnings.append(f"Voice is {voice_len}s but the video is {video_len}s: the end of the voice is cut. "
                                "Add or lengthen shots.")
            n += 1
        if a.music:
            shutil.copy(a.music, tmp / ("music" + Path(a.music).suffix))
            cmd += ["-stream_loop", "-1", "-i", "music" + Path(a.music).suffix]
            mix.append(f"[{n}:a]volume={a.music_volume}[a{n}]")
            labels.append(f"[a{n}]")
            n += 1
        audio = (";".join(mix) + f";{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
                 "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

        vf = "[0:v]null[vout]"
        burned = False
        if a.srt:
            shutil.copy(a.srt, tmp / "subs.srt")
            vf = f"[0:v]subtitles=subs.srt:force_style='{CAPTION_STYLE}'[vout]"
        out_tmp = tmp / "final.mp4"
        tail = ["-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", str(video_len),
                out_tmp.name]
        code, err = run(cmd + ["-filter_complex", f"{vf};{audio}"] + tail, cwd=tmp)
        if code != 0 and a.srt:
            warnings.append("This ffmpeg build cannot burn captions (no libass); the video has no captions. "
                            "Upload the .srt as a caption file or use the platform's auto-captions.")
            code, err = run(cmd + ["-filter_complex", f"[0:v]null[vout];{audio}"] + tail, cwd=tmp)
        elif code == 0 and a.srt:
            burned = True
        if code != 0:
            fail(f"ffmpeg final render failed: {err.strip()[-600:]}")

        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(out_tmp), out)

    result = {"out": str(out), **{k: v for k, v in probe(ff, out).items() if k != "file"},
              "captions_burned": burned, "inputs": infos, "warnings": warnings}
    if a.cover:
        Path(a.cover).parent.mkdir(parents=True, exist_ok=True)
        code, err = run([ff, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(a.cover_at), "-i", str(out),
                         "-frames:v", "1", "-q:v", "2", str(a.cover)])
        result["cover"] = a.cover if code == 0 else None
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
