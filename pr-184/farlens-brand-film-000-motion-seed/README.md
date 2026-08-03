# FARLENS Brand Film #000 — Section 0 Motion A/B/C Test

Status: WORKING MOTION TEST — NON-CANONICAL
Scope: Section 0 C addition; existing A/B, Section 4, and Final are unchanged references

Working Lock済みの縦型静止画へ、生成を使わない決定論的2D Motionを加えた判断用Prototype。現行A/BをByte Lockしたまま、Section 0 Cで既存ライン上を移動する光を検証する。55秒全編、音声、字幕、BGM、他Section制作、Canonical昇格は対象外。

## Review

1. `index.html` をiPhoneで開く。
2. Section 0 A→B→C連続版を無音で一度見る。
3. Section 0のA、B、C、横並びを確認する。
4. `SECTION_0_MOTION_C_NOTES.md` の意味設計、自己評価、コストを確認する。

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

CとA/B/C比較だけを再生成する場合：

```sh
./scripts/build_section0_c.sh
```

このBuildは先に既存A/B、Section 4、Finalの20ファイルをSHA-256検査し、不一致ならCを生成しない。

## Source lock

`assets/source/*.jpg` はユーザー添付原本のコピー。Aは `checksums.sha256`、B/A-Bは `layered-semantic-checksums.sha256` と `layered-semantic-technical-evidence.json` にSHA-256を記録する。Bも毎フレームでJPEG全体をベースにし、元画素の局所複製、既存パス周辺の反応、局所的な光だけを重ねる。欠損補完、背景再生成、外部アップロードは行わない。

## Compass Review Bridge v0.2

PR WorkflowはSection 0 A→B→C連続版、C単体、A/B/C横並び、既存参照、Contact Sheet、Timeline Frames、Source Comparison、ManifestをGitHub Pagesと固定名 `compass-review-bundle-pr-184` のGitHub Actions Artifactへ生成する。Pages公開成功とCompass Connector実取得は別ステータスとして扱い、Compass確認前は `WAITING_FOR_COMPASS_VERIFICATION` のままにする。

## Authority boundary

このPrototypeはWorking artifactであり、元画像やMotion候補をCanonical化しない。Mergeしない。
