# FARLENS Brand Film #000 — Motion Seed Test

Status: WORKING MOTION TEST — NON-CANONICAL
Scope: Section 0 / Section 4 / Final only

Working Lock済みの縦型静止画3枚へ、生成を使わない決定論的2D Motionを加えた判断用Prototype。55秒全編、音声、字幕、BGM、Section 1〜10制作、Canonical昇格は対象外。

## Review

1. `index.html` をiPhoneで開く。
2. 3本連続版を無音で一度見る。
3. Section 0 / Section 4 / Finalを個別に再生し、静けさ、意味、視認性を確認する。
4. `MOTION_DESIGN_NOTES.md` の自己評価と既知の制約を確認する。

## Rebuild

既存の `python3`、`ffmpeg`、`ffprobe` だけを使う。ネットワーク接続や外部AIサービスは使わない。

```sh
./scripts/build.sh
```

## Source lock

`assets/source/*.jpg` はユーザー添付原本のコピー。`checksums.sha256` と `technical-evidence.json` にSHA-256を記録する。レンダラーは毎フレームでJPEG全体をベースにし、上から弱い光と既存パス上の追光を加える。Section 0の最大ズームは1.2%、Section 4の奥行き差は0.6%に限定。Finalだけは既存文字と光点の明るい元画素を一時的に減光して露出復帰を作り、最後2秒以上は元静止画の見え方へ完全に戻して停止する。文字や背景の再生成は行わない。

## Authority boundary

このPrototypeはWorking artifactであり、元画像やMotion候補をCanonical化しない。Mergeしない。
