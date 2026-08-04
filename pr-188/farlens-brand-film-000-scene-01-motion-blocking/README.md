# FARLENS Brand Film #000｜Scene 1 Motion Blocking

Status: **WORKING TEST / NON-CANONICAL / PIPELINE STAGE 3**

0〜10秒のScene 1「世界は動き始めている」を、CEO / Compass作業採用済みのRevised 5 FramesからMotion Blocking化したものです。本番映像・Final Visual・Canonical Motion Grammarではありません。

## 実装方式

- 承認済みStatic Sequence PNGを唯一の画面設計入力にする。
- 元PNGは編集せず、レンダー時に5つの既存Frame領域を参照する。
- 元PNGのレビュー番号領域は上塗りせず、入力Cropから除外する。映像内に番号・ラベル・説明文字を描画しない。
- 同一Frame由来の背景延長Layerで16:9全体を満たし、比率維持の主画をFeather Maskで接続する。
- Frameを単純クロスフェードせず、非円形のOrganic Arrival Mask、伝播線、交差Flow、世界規模への開きで到達状態を橋渡しする。
- Frame 2→3だけは専用のDepth Arrivalを使い、起点の近景を残したまま奥景→中景→前景へ開く。3本のFlow到達量をReveal範囲に同期し、Frame 3全景の先行表示を防ぐ。
- Swift/CoreGraphicsで300フレームを決定論的に描画し、既存FFmpegでH.264へ書き出す。
- カメラは固定。主要変化はFrame内の光、層、構造、相互作用側で起こす。

## Blockingで確認すること

- Frame 1〜5とBeat 1〜4の対応が崩れていないか。
- Beat 1の静けさからBeat 4の世界規模への始動まで、Motion量が段階的に増えるか。
- Frame 3が「異なる現象の発生」、Frame 4が「接続と相互作用」に見えるか。
- ナレーションなしでも「小さな変化 → 伝播 → 相互作用 → 世界全体の始動」が読めるか。
- 主役交代と10秒のテンポが適切か。

## Final工程へ残すこと

- 個別レイヤーの精密分離と本番用素材制作
- 粒子、光、質感、陰影、エッジの最終仕上げ
- Sound Design、Narration、字幕、音とMotionの同期
- Final Color、レンズ表現、微細な環境Motion
- 16:9以外への構図最適化

Blockingでは上記を評価対象にせず、安価で局所修正可能な意味・テンポ検証に限定します。

## Frame / Beat timeline

| Frame | Beat | Time | Blocking change |
| --- | --- | --- | --- |
| 1 | Beat 1 | 0.0–1.6s | 静かな世界。環境光の微弱な呼吸のみ。 |
| 2 | Beat 2 | 1.6–3.0s | Frame 1内の一点へ光が集まり、局所変化が立ち上がって定着。 |
| 3 | Beat 3 | 3.0–5.3s | Beat 2の起点と近景を橋として残し、3方向のFlow到達後に奥景→中景→前景が順に立ち上がってFrame 3状態へ到達。 |
| 4 | Beat 3→4 | 5.3–7.6s | 既存Flowが関係を持ち、交差Flowと反応点で相互作用・加速。 |
| 5 | Beat 4 | 7.6–10.0s | 既存の接続が世界規模へ広がり、9.3秒以降は静かに安定。 |

機械可読版は [`beat-map.json`](./beat-map.json) にあります。

## Rebuild

既存のmacOS Swift / CoreGraphicsとFFmpegのみを使用します。新規パッケージや有料サービスは不要です。

```sh
./scripts/build_scene01.sh
```

出力:

- `output/master/scene-01-motion-blocking.mp4`
- `output/iphone/scene-01-motion-blocking-iphone.mp4`
- `assets/keyframes/`
- `assets/review/storyboard-motion-contact-sheet.png`
- `assets/review/transition-contact-sheet.png`
- `assets/review/max-change-frame.jpg`
- `assets/review/contact-sheet-0.5-second.png`
- `assets/review/transition-frame-1-to-2.png`
- `assets/review/transition-frame-2-to-3.png`
- `assets/review/comparison-frame-2-to-3-before-after.png`（左: commit `97a10ca` / 右: 現行版）
- `assets/review/transition-frame-3-to-4.png`
- `assets/review/transition-frame-4-to-5.png`
- `technical-evidence.json`
- `checksums.sha256`

## Input integrity

Input: `docs/farlens/brand-film/assets/scene-01/BRAND_FILM_000_SCENE_01_STATIC_SEQUENCE_WORKING_LOCK.png`

Expected SHA-256: `97bfd90afc8e6ceaa6d6bf3e8a26d78b6cf9b9d506240af5fd84fb5b9d290c59`

ビルドと検査はSHA不一致時に失敗します。公開ページ用コピーも同一バイトです。
参照元PR・commit・Frame対応は [`assets/source/SOURCE_PROVENANCE.md`](./assets/source/SOURCE_PROVENANCE.md) に固定しています。

## Authority boundary

- 参照設計: Draft PR #186
- PR #186へ実装commitを追加しない
- Static Sequence、台本、Beat、Frame構成を変更しない
- 画像生成・画像編集・外部AI動画生成を行わない
- 本成果物はMotion Blockingであり、本番品質・Canonical・Merge承認を意味しない
