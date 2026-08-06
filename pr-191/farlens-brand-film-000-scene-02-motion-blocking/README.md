# FARLENS Brand Film #000｜Scene 2 Motion Blocking

Status: **WORKING TEST / NON-CANONICAL / PIPELINE STAGE 3**

Scene 2「増える情報、深まる問い」（Brand Film 10.0〜23.0秒）のMotion Blockingです。CEO採用済みA1〜A5とDraft PR #190のMotion Blocking Designだけを設計入力にし、Draft PR #188のRenderer・Review Artifact構成を再利用しています。

## 実装方式

- A1〜A5原本PNGをSHA固定で直接読み込む。原本は変更しない。
- 8枚のInformation Membraneを固定Slot Maskとして分離し、認識可能数とPriorityだけを変える。
- A1=3、A2=6、A3=8、A4=8由来を維持しPriority低下、A5=認識可能0。
- A3の見えにくさはRefraction量で作り、Depth Blurを使わない。
- A4では既存の左下量塊を、Depth Blur・輪郭分離・膜Priority低下だけで親子として認識させる。
- Compass RevisionではA3の左下量塊を固定Focus PlateとしてA4・A5まで保持し、中心・比率・接地面・輪郭を変えず、局所明度差と背景側Depth Blurだけを段階化する。
- A4背景の採用画像は焦点領域外へ0.95秒遅らせて入れ、7.2秒付近の全画面Blendを弱める。
- A5では空側を同一採用世界の膜なし状態へ段階的に戻し、地形・親子・右遠景の既存暖色光を保持する。
- Swift/CoreGraphicsで390 Frameを決定論的に描画し、FFmpegでH.264/yuv420p/faststartへ書き出す。

## Timeline

| Frame | Local | Brand Film | Meaning |
| --- | --- | --- | --- |
| A1 | 0.0–2.2s | 10.0–12.2s | 静かな世界に3枚の膜が認識される |
| A2 | 2.2–4.6s | 12.2–14.6s | 6枚へ増え、重なり部分の屈折が増す |
| A3 | 4.6–7.2s | 14.6–17.2s | 8枚と屈折で、存在したまま見えにくくなる |
| A4 | 7.2–10.0s | 17.2–20.0s | 新規追加なしで親子が認識される |
| A5 | 10.0–13.0s | 20.0–23.0s | 膜0枚、世界と余白の可読性が戻る |

機械可読版は [`beat-map.json`](./beat-map.json) を参照してください。

## Rebuild

新規依存はありません。macOS Swift/CoreGraphicsと既存FFmpegだけを使用します。

```sh
./scripts/build_scene02.sh
```

## Review scope

- 5 Beatがナレーションなしで読めるか
- A3が「消えた」ではなく「存在しているが見えにくい」か
- A4で新しい親子が追加されたように見えないか
- A5で情報消滅ではなくPriorityが退き、世界の可読性が戻るか
- 右遠景の光が答え・ゴールに見えないか
- Scene 1→2が同じ世界の別地点へ入る呼吸としてつながるか

## Compass revision evidence

- `assets/review/a3-to-a4-before-after.png`: 上段が修正前、下段が修正後の同時刻比較
- `assets/review/max-change-frame.png`: 修正前後の差が最大となったFrame 243（8.100秒／絶対18.100秒）の修正版
- `revision-evidence.json`: 非変更区間、全画面Blend低下、焦点連続性の機械検査

Sound、Narration、字幕、Final textureはMotion Blockingの対象外です。

## Authority boundary

- Draft PR #190へ実装を追加しない
- Draft PR #188を変更しない
- Static画像、台本、Beat、Genesis OSを変更しない
- Mergeしない
