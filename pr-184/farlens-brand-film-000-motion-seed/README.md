# FARLENS Brand Film #000 — Motion Seed + Layered Semantic A/B Test

Status: WORKING MOTION TEST — NON-CANONICAL
Scope: Section 0 / Section 4 A/B; Final is an unchanged reference

Working Lock済みの縦型静止画へ、生成を使わない決定論的2D Motionを加えた判断用Prototype。現行Base MotionをAとしてByte Lockし、Section 0と4だけにB（Layered Semantic Motion）を追加した。55秒全編、音声、字幕、BGM、他Section制作、Canonical昇格は対象外。

## Review

1. `index.html` をiPhoneで開く。
2. 2本連続A/B版を無音で一度見る。
3. Section 0 / Section 4のA、B、横並びを確認する。
4. `LAYERED_SEMANTIC_MOTION_NOTES.md` の意味設計、自己評価、コストを確認する。

## Rebuild

既存の `python3`、`ffmpeg`、`ffprobe` だけを使う。ネットワーク接続や外部AIサービスは使わない。

```sh
./scripts/build.sh
```

現行A/Finalを一切書き換えず、Bと比較Artifactだけを再生成する場合：

```sh
./scripts/build_layered_ab.sh
```

後者は処理の前後でA/Final 8ファイルの固定SHA-256を検査し、不一致なら失敗する。

## Source lock

`assets/source/*.jpg` はユーザー添付原本のコピー。Aは `checksums.sha256`、B/A-Bは `layered-semantic-checksums.sha256` と `layered-semantic-technical-evidence.json` にSHA-256を記録する。Bも毎フレームでJPEG全体をベースにし、元画素の局所複製、既存パス周辺の反応、局所的な光だけを重ねる。欠損補完、背景再生成、外部アップロードは行わない。

## Compass Review Bridge v0.2

PR WorkflowはA/B連続版、Section別A/B、横並び比較、Contact Sheet、Timeline Frames、Source Comparison、ManifestをGitHub Pagesと固定名 `compass-review-bundle-pr-184` のGitHub Actions Artifactへ生成する。Pages公開成功とCompass Connector実取得は別ステータスとして扱い、Compass確認前は `WAITING_FOR_COMPASS_VERIFICATION` のままにする。

## Authority boundary

このPrototypeはWorking artifactであり、元画像やMotion候補をCanonical化しない。Mergeしない。
