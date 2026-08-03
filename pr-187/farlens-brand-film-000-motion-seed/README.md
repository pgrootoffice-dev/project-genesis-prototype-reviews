# FARLENS Brand Film #000 — Section 0 Layer-first Motion D Prototype

Status: WORKING MOTION TEST — NON-CANONICAL
Scope: Section 0 D addition; existing A/B/C, Section 4, and Final are unchanged references

Working Lock済みの縦型静止画を9つの同一キャンバス素材へ決定論的に分離し、役割交代型Motionを検証する判断用Prototype。現行A/B/CをSHA-256 Lockしたまま、Section 0 DでEarth → Clouds → Traveling Light → Family responseを検証する。55秒全編、音声、字幕、BGM、他Section制作、Canonical昇格は対象外。

## Review

1. `index.html` をiPhoneで開く。
2. Section 0 A→B→C→D連続版を無音で一度見る。
3. Section 0のA、B、C、D、横並び、Layer Breakdownを確認する。
4. `SECTION_0_MOTION_D_NOTES.md` と `SECTION_0_MOTION_D_COST_REPORT.md` を確認する。

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

Dの9レイヤー、D本編、A/B/C/D比較、Layer Breakdown、技術Evidenceを再生成する場合：

```sh
./scripts/build_section0_d.sh
```

このBuildは処理前後で既存A/B/C、Section 4、Finalの31ファイルを検査する。レイヤー再合成が元JPEGと画素単位で一致しない場合、またはHold・動画仕様・連続Motion契約に違反した場合は失敗する。

## Source lock

`assets/source/*.jpg` はユーザー添付原本のコピー。Aは `checksums.sha256`、Bは `layered-semantic-checksums.sha256`、Cは `section-0-c-checksums.sha256`、Dは `section-0-d-checksums.sha256` に固定値を記録する。Dは決定論的マスクと元画素由来の局所Underlayだけを使い、再合成MAE 0.0を検査する。生成補完、背景生成、外部アップロードは行わない。

## Compass Review Bridge v0.2

PR WorkflowはSection 0 A→B→C→D連続版、D単体、A/B/C/D横並び、Layer Breakdown、9 PNG、再合成、差分、Contact Sheet、Timeline Frames、Source Comparison、ManifestをGitHub Pagesと固定規則 `compass-review-bundle-pr-{PR_NUMBER}` のGitHub Actions Artifactへ生成する。Pages公開成功とCompass Connector実取得は別ステータスとして扱い、Compass確認前は `WAITING_FOR_COMPASS_VERIFICATION` のままにする。

## Authority boundary

このPrototypeはWorking artifactであり、元画像やMotion候補をCanonical化しない。Mergeしない。
