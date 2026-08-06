# Scene 1 Static Sequence Source Provenance

Status: **WORKING LOCK INPUT / NON-CANONICAL**

このファイルはMotion Blocking入力の来歴だけを記録する。PR #186の設計文書を複製・変更・Canonical化しない。

- Repository: `pgrootoffice-dev/project-genesis`
- Reference Draft PR: [#186](https://github.com/pgrootoffice-dev/project-genesis/pull/186)
- Reference commit: [`5cdb67d94154f99c4304612abc48d230b64961de`](https://github.com/pgrootoffice-dev/project-genesis/commit/5cdb67d94154f99c4304612abc48d230b64961de)
- Original path: `docs/farlens/brand-film/assets/scene-01/BRAND_FILM_000_SCENE_01_STATIC_SEQUENCE_WORKING_LOCK.png`
- Implementation input path: `docs/farlens/brand-film/assets/scene-01/BRAND_FILM_000_SCENE_01_STATIC_SEQUENCE_WORKING_LOCK.png`
- Public-review byte copy: `assets/source/static-sequence-working-lock.png`
- Dimensions: 1536×1024 RGB PNG
- SHA-256: `97bfd90afc8e6ceaa6d6bf3e8a26d78b6cf9b9d506240af5fd84fb5b9d290c59`
- Approval state carried from PR #186: CEO / Compass実画像レビュー済み、Motion Blocking次工程への作業採用済み
- Authority boundary: Working Lock / Non-Canonical。Final Visual、Final Motion、Merge承認ではない

Frame / Beat対応は固定する。

1. Frame 1 = Beat 1
2. Frame 2 = Beat 2
3. Frame 3 = Beat 3
4. Frame 4 = Beat 4（接続から世界全体への広がりを開始）
5. Frame 5 = Beat 4完了（7.6〜9.3秒）＋Beat 5接続安定（9.3〜10.0秒）

参照設計文書はPR #186に留め、この実装PRから変更しない。

## Scene 2 connection boundary

PR #191のScene 2 Masterは読み取り専用参照としてのみ扱う。Scene 1終端9.95秒のPNGは、PR #191が保持するScene 1 terminal referenceと同一SHAでなければBuildを失敗させる。

- PR #191 Head: `23cc8f2446f77895f926e7e19264f49dfc9012dd`
- Scene 2 Master SHA-256: `3e51b0fbf461d7cfc49c91c05420777f2da1bc843b476a65127483fb50a76904`
- Scene 1 terminal reference SHA-256: `32b9a74ea1ee1a01386671726abb47201bdcbc7c3ff4dd2f59a51cd157258c1c`
- Scene 2 Static A1〜A5、Renderer、Motion、Timingは変更しない
