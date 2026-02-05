# Folio 修正計画 v2 — 詳細実装計画書

> 作成日: 2026-02-06
> ステータス: 承認待ち

---

## 修正概要

| # | 修正内容 | 対象ファイル | 優先度 |
|---|---|---|---|
| 1 | 構造単位を「章 → 話（Episode）」の二階層に変更 | editor.md, plotter.md, workspace構造 | HIGH |
| 2 | Phase 0.5 → Phase 3: Design に改名＋キャラクター確認ゲート | editor.md, CLAUDE.md | HIGH |
| 3 | Phase 2 に規模選択を追加 | editor.md, CLAUDE.md | MEDIUM |
| 4 | 話（Episode）単位で /output に書き出し | editor.md, export.md | HIGH |
| 5 | 章開始前に流れ確認ゲート（第二章以降） | editor.md | HIGH |
| 6 | 章完了時にユーザー確認ゲート | editor.md | HIGH |
| 7 | 伏線追跡システムの導入 | editor.md, plotter.md | MEDIUM |
| 8 | Quality Gate の二段階化 | editor.md | MEDIUM |
| 9 | Crew評価項目の追加 | plotter.md, persona.md | MEDIUM |
| 10 | 新規コマンドの追加 | .claude/commands/ | LOW |

---

## 1. 構造単位の変更

### 1.1 workspace 構造の変更

**Before（現行）**
```
workspace/current/chapters/
├── ch01/
│   ├── draft-01.md
│   └── reviews/round-01/
├── ch02/
└── ...
```

**After（修正後）**
```
workspace/current/chapters/
├── ch01/
│   ├── outline.json           # 章の流れ（選択されたパターン）
│   ├── consistency.json       # 整合性チェック結果
│   ├── ep01/
│   │   ├── draft-01.md
│   │   ├── draft-02.md
│   │   └── reviews/
│   │       ├── round-01/
│   │       │   ├── plotter.json
│   │       │   ├── stylist.json
│   │       │   └── ...
│   │       └── round-02/
│   ├── ep02/
│   │   ├── draft-01.md
│   │   └── reviews/
│   ├── ep03/
│   ├── ep04/
│   ├── chapter-review.json    # 章通読レビュー結果
│   └── status.json            # confirmed / pending
├── ch02/
└── ...
```

### 1.2 ボリューム設定（idea.json に追加）

```json
{
  "scale": {
    "type": "medium",
    "total_chars": "30000-120000",
    "chapter_count": "3-5",
    "episode_count": "10-40",
    "episode_chars": "2000-4000"
  }
}
```

### 1.3 ファイル変更一覧

| ファイル | 変更内容 |
|---------|---------|
| `prompts/editor.md` | Phase 4 のループ単位を Episode に変更 |
| `prompts/crew/plotter.md` | ドラフト生成を Episode 単位に変更、word_count_range 追加 |
| `prompts/crew/pacer.md` | episode_hook 評価軸を追加 |
| `.claude/commands/export.md` | Episode 単位のエクスポートに対応 |

### 1.4 スコアカードの target フィールド変更

**Before:** `ch01-draft-02`
**After:** `ch01-ep03-draft-02`

---

## 2. Phase 構成の再設計

### 2.1 新しい Phase 構成

| Phase | 名称 | 内容 | ユーザー確認 |
|-------|------|------|-------------|
| 0 | Intake | アイデア構造化 | - |
| 1 | Paths | 3パターン生成 | - |
| 2 | Select | パス選択 + **規模選択** | ✅ 必須 |
| 3 | Design | キャラ生成 + 世界観設計 + **確認ゲート** | ✅ 必須 (NEW) |
| 4 | Loop | Episode単位の執筆ループ | 章完了時に確認 |
| 5 | Assemble | 最終仕上げ | - |

### 2.2 Phase 2 の変更（規模選択の追加）

**progress.json 出力例:**
```json
{
  "phase": 2,
  "awaiting_user": true,
  "selection_type": "path_and_scale",
  "paths": [
    {"id": "A", "title": "...", "approach": "..."},
    {"id": "B", "title": "...", "approach": "..."},
    {"id": "C", "title": "...", "approach": "..."}
  ],
  "scale_options": [
    {"id": "short", "label": "短編", "chars": "〜1万字", "chapters": "1章", "episodes": "3〜5話"},
    {"id": "medium", "label": "中編", "chars": "3万〜12万字", "chapters": "3〜5章", "episodes": "10〜40話"},
    {"id": "long", "label": "長編", "chars": "8万〜12万字", "chapters": "5〜8章", "episodes": "25〜40話"},
    {"id": "serial", "label": "連載", "chars": "30万字〜", "chapters": "10章〜", "episodes": "100話〜"}
  ]
}
```

**Desk 表示例:**
```
━━━ パスと規模の選択 ━━━

【パス選択】
A. 覚醒の月光 — 王道・安定・広い読者層
B. 暗黒の夜明け — 意外性・挑戦的展開
C. 静寂の絆 — キャラ深掘り・感情重視

【規模選択】
1. 短編（〜1万字 / 1章 / 3〜5話）
2. 中編（3万〜12万字 / 3〜5章 / 10〜40話）
3. 長編（8万〜12万字 / 5〜8章 / 25〜40話）
4. 連載（30万字〜 / 10章〜 / 100話〜）

→ パス [A/B/C] と規模 [1/2/3/4] を選択してください
   例: "A2"（パスA、中編）
```

### 2.3 Phase 3: Design の実装（旧 Phase 0.5 の拡張）

**実行内容:**
1. キャラクターシート生成（現行 Phase 0.5 の処理）
2. 世界観設定の生成（Atlas エージェント活用）
3. `/output/characters/` への書き出し
4. **キャラクター確認ゲート**（ユーザー承認必須）

**新規ファイル: `prompts/templates/character.md`**

キャラクターシートのMarkdownテンプレートを追加（詳細は別途）

---

## 3. キャラクター確認ゲート

### 3.1 タイミング

| タイミング | 発生条件 |
|-----------|---------|
| Phase 3 完了後 | 初期キャラクター全員の確認 |
| 執筆中に新キャラ登場時 | Plotter が新キャラ必要と判断した場合 |
| 既存キャラの重大な設定変更時 | Editor が判断 |

### 3.2 出力ディレクトリ構造

```
/output/characters/
├── _index.md              # 登場人物一覧
├── 水野遥.md              # キャラクターごとの個別ファイル
├── ARIA.md
└── 佐藤健一.md
```

### 3.3 キャラクターシート テンプレート

**ファイル: `/output/characters/{キャラ名}.md`**

```markdown
# {名前}（{読み}）

## 基本情報

| 項目 | 内容 |
|---|---|
| 名前 | {名前}（{読み}） |
| 年齢 | {年齢} |
| 性別 | {性別} |
| 役割 | {protagonist/supporting/antagonist} |
| 初登場 | 第{N}章 第{M}話 |

## 行動原理（最重要）

| 項目 | 内容 |
|---|---|
| 目的 | {短期〜長期の目的} |
| 動機 | {なぜその目的を持つのか} |
| 信念 | {行動の根幹にある価値観} |
| 好き | {3つ程度} |
| 嫌い | {3つ程度} |

## 精神的特徴

| 項目 | 内容 |
|---|---|
| 性格（長所） | {3〜4つ} |
| 性格（短所） | {3〜4つ} |
| 口調 | {具体的な話し方の特徴} |
| 癖 | {無意識の動作、独り言など} |

## 肉体的特徴

| 項目 | 内容 |
|---|---|
| 容姿 | {全体的な印象} |
| 髪型 | {詳細} |
| 服装 | {通常の服装} |
| 特徴 | {目立つ特徴、傷跡など} |

## 背景（バックボーン）

{2〜3段落で生い立ちや過去のエピソードを記述}

## キャラクターアーク

```
{開始状態} → {転機1} → {転機2} → {最終状態}
```

## 関連キャラクター

- [{関連キャラ1}](./{関連キャラ1}.md) — {関係性}
- [{関連キャラ2}](./{関連キャラ2}.md) — {関係性}

## 登場話一覧

| 話 | 役割 |
|---|---|
| 第1話「...」 | {主要/登場/言及} |
| ... | ... |

---
[← 登場人物一覧に戻る](./_index.md)
```

### 3.4 確認フロー

```
Phase 3 完了
  ↓
Editor: キャラクターシート生成
  ↓
Editor → /output/characters/ にファイル書き出し
  ↓
Editor → progress.json を更新
  {
    "phase": 3,
    "awaiting_user": true,
    "gate_type": "character_confirmation",
    "characters": [
      {"name": "水野遥", "role": "protagonist", "file": "/output/characters/水野遥.md"},
      {"name": "ARIA", "role": "supporting", "file": "/output/characters/ARIA.md"}
    ]
  }
  ↓
Desk: ユーザーに提示
  「キャラクター設定が完成しました。
   /output/characters/ をご確認ください。

   - 水野遥.md（主人公）
   - ARIA.md（AI相棒）

   承認しますか？ 修正点があればお伝えください。」
  ↓
ユーザー: 承認 or 修正指示
  ↓
Desk → user_input.json に書き込み
  ↓
承認 → Phase 4 へ進行
修正 → Editor がキャラシート修正 → 再度確認
```

### 3.5 新キャラ登場時の確認（Plotter が判定）

**Plotter の新キャラ判定ロジック:**

1. ドラフト生成時に「この展開には新キャラが必要」と判断
2. ドラフトに新キャラ提案を含めて返却:
   ```json
   {
     "draft": "...",
     "new_character_proposal": {
       "needed": true,
       "reason": "第3話の対立シーンで敵対勢力の代表者が必要",
       "suggestion": {
         "name": "黒崎 玲",
         "role": "antagonist",
         "brief": "敵対組織のリーダー。冷酷だが信念を持つ"
       }
     }
   }
   ```
3. Editor が提案を検出 → Phase 4 ループを一時停止
4. Editor が新キャラシートを生成 → `/output/characters/` に追加
5. Desk → ユーザーに確認
6. 承認後、Phase 4 ループを再開

---

## 4. 話（Episode）単位の出力

### 4.1 出力ルール

- Quality Gate を通過した時点で `/output/episodes/` に自動書き出し
- ファイル名: `第XX話_タイトル.md`
- 各話ファイルの先頭にメタデータ付与

### 4.2 出力先構造

```
/output/
├── characters/
│   ├── _index.md
│   ├── 水野遥.md
│   └── ARIA.md
└── episodes/
    ├── _index.md              # 目次
    ├── 第01話_目覚め.md
    ├── 第02話_出会い.md
    ├── 第03話_決意.md
    ├── 第04話_門出.md          # ← 第一章ここまで
    ├── 第05話_嵐の前.md        # ← 第二章ここから
    └── ...
```

### 4.3 話ファイルのフォーマット

```markdown
---
話数: 3
タイトル: 決意
章: 第一章「旅立ち」
文字数: 3200
ステータス: 確定
最終スコア: 7.8
レビューラウンド: 3
---

# 第3話「決意」

（本文）

---
[← 前話: 第2話「出会い」](./第02話_出会い.md) | [次話: 第4話「門出」 →](./第04話_門出.md)

[目次に戻る](./_index.md)
```

### 4.4 目次ファイル（`_index.md`）

```markdown
# {作品タイトル} — 目次

## 第一章「旅立ち」
- [第1話「目覚め」](./第01話_目覚め.md) — 3,100字
- [第2話「出会い」](./第02話_出会い.md) — 2,800字
- [第3話「決意」](./第03話_決意.md) — 3,200字
- [第4話「門出」](./第04話_門出.md) — 2,900字

## 第二章「試練」（執筆中）
- [第5話「嵐の前」](./第05話_嵐の前.md) — 3,400字
- 第6話（執筆中）

---
総文字数: 15,400字 / 5話完了
```

---

## 5. 章開始前の流れ確認ゲート（第二章以降）

### 5.1 実行条件

- **第一章**: 省略（Path 選択の内容で直接執筆開始）
- **第二章以降**: 必ず実行

### 5.2 フロー

```
第N章（N >= 2）の執筆開始前
  ↓
Editor → Plotter × 3 並列起動
  「第N章の流れを3パターン提案せよ」
  ↓
Plotter A, B, C → 各パターンを生成
  ↓
Editor → 整合性チェック（後述）
  ↓
整合性 NG のパターンがあれば修正 or 除外
  ↓
Editor → progress.json を更新
  {
    "phase": 4,
    "awaiting_user": true,
    "gate_type": "chapter_outline",
    "chapter": 3,
    "patterns": [
      {
        "id": "A",
        "label": "穏やかな展開",
        "episodes": [...],
        "consistency": "OK"
      },
      {
        "id": "B",
        "label": "緊迫した展開",
        "episodes": [...],
        "consistency": "OK"
      },
      {
        "id": "C",
        "label": "（整合性NGのため除外）",
        "reason": "第二章末の伏線が未回収のまま矛盾"
      }
    ]
  }
  ↓
Desk → ユーザーに表示
  ↓
ユーザー: 選択
  ↓
Desk → user_input.json に書き込み
  ↓
Editor → 選択されたパターンで Phase 4 開始
```

### 5.3 整合性チェック項目（必須）

Editor が各パターンに対して以下を**すべて**チェック。1つでも NG なら修正 or 除外。

**ファイル: `workspace/current/chapters/ch{N}/consistency.json`**

```json
{
  "consistency_check": {
    "chapter": 3,
    "pattern": "A",
    "checks": [
      {
        "item": "前章末との接続",
        "description": "前章の最終話の状況から自然に続くか",
        "status": "OK",
        "detail": "第8話末で通信途絶の予兆 → 第9話で異変に気づく流れは自然"
      },
      {
        "item": "未回収伏線の扱い",
        "description": "前章までに張った伏線が矛盾なく扱われているか",
        "status": "OK",
        "detail": "第5話の「管制の不審な指令」→ 第10話で通信途絶として回収予定"
      },
      {
        "item": "キャラクターの状態連続性",
        "description": "前章末のキャラの心理状態・物理状態と矛盾しないか",
        "status": "OK",
        "detail": "遥: 第8話末でARIAへの警戒心が薄れ始めている → 第9話の反応と整合"
      },
      {
        "item": "時系列の整合性",
        "description": "時間経過に矛盾がないか",
        "status": "OK",
        "detail": "第8話から数日後の設定。船内カレンダーと矛盾なし"
      },
      {
        "item": "世界観設定との整合性",
        "description": "確立された世界観ルールに違反しないか",
        "status": "OK",
        "detail": "通信途絶の原因が太陽フレア → 設定資料のフレア頻度と矛盾なし"
      },
      {
        "item": "キャラクターアークの進行",
        "description": "この章でキャラの成長弧が適切に進むか",
        "status": "OK",
        "detail": "遥のアーク「依存への恐怖 → 危機での協力」がこの章で進行"
      }
    ],
    "overall": "PASS",
    "warnings": []
  }
}
```

---

## 6. 章完了時のユーザー確認ゲート

### 6.1 実行条件

章に含まれる全話が Quality Gate を通過した時点で発動。

### 6.2 フロー

```
章内の全話が Quality Gate 通過
  ↓
Editor: 章全体の通読レビューを実施
  - 話間の整合性
  - 章全体のペーシング
  - 伏線の状況（張った / 回収した / 持ち越し）
  ↓
Editor → workspace/current/chapters/ch{N}/chapter-review.json を生成
  ↓
Editor → progress.json を更新
  {
    "phase": 4,
    "awaiting_user": true,
    "gate_type": "chapter_completion",
    "chapter": 2,
    "chapter_review": {
      "episode_range": "5-8",
      "total_chars": 12800,
      "avg_score": 7.6,
      "episode_scores": [
        {"ep": 5, "title": "嵐の前", "score": 7.2},
        {"ep": 6, "title": "対峙", "score": 7.8},
        {"ep": 7, "title": "裏切り", "score": 8.1},
        {"ep": 8, "title": "決断", "score": 7.3}
      ],
      "foreshadowing": {
        "resolved": [
          {"id": "fs-002", "desc": "ARIAの記憶断片", "planted": "ep03", "resolved": "ep07"}
        ],
        "carried_over": [
          {"id": "fs-001", "desc": "管制の不審な指令", "planted": "ep05", "planned": "ch03"},
          {"id": "fs-003", "desc": "遥の左頬の傷", "planted": "ep01", "planned": "ch04"}
        ]
      }
    }
  }
  ↓
Desk → ユーザーに表示
  ↓
ユーザー: 承認 → 次章の流れ確認ゲートへ
ユーザー: 修正指示 → 該当話を再編集 → 再レビュー → 再確認
```

---

## 7. 伏線追跡システム

### 7.1 データ構造

**ファイル: `workspace/current/foreshadowing.json`**

```json
{
  "foreshadowings": [
    {
      "id": "fs-001",
      "description": "管制からの不審な指令",
      "planted_at": { "chapter": 2, "episode": 5, "paragraph": 12 },
      "planned_payoff": { "chapter": 3, "episode": 10 },
      "status": "open",
      "importance": "major"
    },
    {
      "id": "fs-002",
      "description": "ARIAの記憶断片",
      "planted_at": { "chapter": 1, "episode": 3, "paragraph": 8 },
      "resolved_at": { "chapter": 2, "episode": 7, "paragraph": 22 },
      "status": "resolved",
      "importance": "major"
    }
  ]
}
```

### 7.2 伏線の追加・更新タイミング

| タイミング | 担当 | 処理 |
|-----------|------|------|
| ドラフト生成時 | Plotter | 新規伏線を検出して `planted_at` を追加 |
| レビュー時 | Editor | 伏線回収を検出して `resolved_at` を追加 |
| 章開始前 | Editor | 整合性チェックで未回収伏線を検証 |
| 章完了時 | Editor | 伏線状況レポートを生成 |

---

## 8. Quality Gate の二段階化

### 8.1 話レベル Gate（Episode Gate）

```python
EPISODE_GATE = {
    "min_overall": 7.0,        # 全体平均
    "min_each": 6.5,           # 各エージェント最小値
    "no_critical": True,       # クリティカル問題なし
    "max_rounds": 5,           # 最大5ラウンド
    "min_improvement": 0.3,    # 前ラウンドからの改善
    "word_count_range": [2000, 4000],  # なろう/カクヨム適正範囲
}
```

### 8.2 章レベル Gate（Chapter Gate）

話 Gate 通過後に追加で実行。

```python
CHAPTER_GATE = {
    "inter_episode_consistency": True,   # 話間の整合性チェック必須
    "pacing_check": True,               # 章全体のペーシング確認
    "foreshadowing_tracking": True,      # 伏線追跡（張り/回収/持越し）
    "character_arc_progress": True,      # キャラアーク進行の確認
    "user_approval_required": True,      # ユーザー承認必須
}
```

---

## 9. Crew 評価項目の追加

### 9.1 Plotter に追加

| 評価軸 | 説明 |
|--------|------|
| `episode_hook` | 話末の引き（次話への期待度） |
| `web_novel_pacing` | Web小説としてのテンポ（スクロール読みに適しているか） |

### 9.2 Persona に追加

| 評価軸 | 説明 |
|--------|------|
| `new_character_necessity` | 新キャラの必要性判定（不要な新キャラの乱立防止） |
| `character_sheet_compliance` | キャラシートとの一致度チェック |

### 9.3 Editor の整合性チェックに追加

| チェック項目 | 説明 |
|--------------|------|
| `foreshadowing_status` | 伏線追跡データとの照合 |
| `chapter_boundary_continuity` | 章境界での状態連続性 |

---

## 10. 新規コマンドの追加

### 10.1 `/characters` コマンド

**ファイル: `.claude/commands/characters.md`**

`/output/characters/` の一覧を表示。

### 10.2 `/foreshadowing` コマンド

**ファイル: `.claude/commands/foreshadowing.md`**

伏線の状況一覧（open / resolved）を表示。

### 10.3 `/chapter-status` コマンド

**ファイル: `.claude/commands/chapter-status.md`**

各章の確認状態（confirmed / pending）を表示。

---

## 11. 修正後のワークフロー全体図

```
Phase 0: Intake（アイディア投入）
  ↓
Phase 1: Paths（3パターン生成）
  ↓
Phase 2: Select（パス選択 + ★規模選択★）← NEW
  ↓
Phase 3: Design（キャラ生成 + 世界観設計）← 旧 Phase 0.5 改名
  ↓
★ キャラクター確認ゲート ★ ← NEW
  Editor → /output/characters/ 書き出し
  Desk → ユーザー確認
  承認されるまで次に進まない
  ↓
━━━ 第一章 ━━━
  ↓
Phase 4: Loop（Episode単位）
  ↓
★ 第一章完了 ユーザー確認ゲート ★ ← NEW
  ↓
━━━ 第二章以降繰り返し ━━━
  ↓
★ 章開始前 流れ確認ゲート ★ ← NEW（第二章以降）
  Plotter × 3 で流れパターン生成
  Editor が整合性チェック（必須）
  整合性OKのパターンのみ Desk → ユーザーに提示
  ユーザーが選択
  ↓
Phase 4: Loop（Episode単位）
  ↓ ← 話（Episode）単位でループ
  │
  │  Plotter: 1話分のドラフト生成（2,000〜4,000字）
  │  ├─ 新キャラ提案があれば → 一時停止 → 確認ゲート
  │  Crew 8名: 並列レビュー
  │  Editor: スコア集約 → 収束判定
  │  ↓
  │  Episode Quality Gate 通過 → /output/episodes/ に書き出し ← NEW
  │  次の話へ
  │
  ↓ 章内の全話完了
  ↓
★ 章完了 ユーザー確認ゲート ★ ← NEW
  Editor: 章通読レビュー + 伏線状況報告
  Desk → ユーザー確認
  承認されるまで次章に進まない
  ↓
━━━ 次章の流れ確認ゲートに戻る ━━━
  ↓
Phase 5: Assemble（全章完了後の最終仕上げ）
```

---

## 12. ファイル変更一覧（実装順序）

### Step 1: 構造変更

| # | ファイル | 変更内容 |
|---|----------|---------|
| 1-1 | `prompts/editor.md` | Phase 4 を Episode 単位に変更 |
| 1-2 | `prompts/crew/plotter.md` | ドラフト生成を Episode 単位に、word_count_range 追加 |
| 1-3 | `prompts/templates/character.md` | キャラクターシート Markdown テンプレート（新規） |

### Step 2: Phase 構成変更

| # | ファイル | 変更内容 |
|---|----------|---------|
| 2-1 | `prompts/editor.md` | Phase 0.5 → Phase 3 に改名、規模選択を Phase 2 に追加 |
| 2-2 | `CLAUDE.md` | Desk の Phase 説明を更新 |
| 2-3 | `.claude/commands/folio.md` | Phase 2 の規模選択 UI を追加 |

### Step 3: キャラクター確認ゲート

| # | ファイル | 変更内容 |
|---|----------|---------|
| 3-1 | `prompts/editor.md` | Phase 3 完了後の確認フローを追加 |
| 3-2 | `prompts/crew/plotter.md` | 新キャラ提案ロジックを追加 |
| 3-3 | `.claude/commands/characters.md` | `/characters` コマンド（新規） |

### Step 4: 章ゲート

| # | ファイル | 変更内容 |
|---|----------|---------|
| 4-1 | `prompts/editor.md` | 章開始前の流れ確認ゲート（第二章以降） |
| 4-2 | `prompts/editor.md` | 章完了時のユーザー確認ゲート |
| 4-3 | `prompts/editor.md` | 整合性チェックロジック |

### Step 5: 伏線追跡システム

| # | ファイル | 変更内容 |
|---|----------|---------|
| 5-1 | `prompts/editor.md` | foreshadowing.json の管理ロジック |
| 5-2 | `prompts/crew/plotter.md` | 伏線検出ロジック |
| 5-3 | `.claude/commands/foreshadowing.md` | `/foreshadowing` コマンド（新規） |

### Step 6: 出力変更

| # | ファイル | 変更内容 |
|---|----------|---------|
| 6-1 | `prompts/editor.md` | Episode の /output/episodes/ 書き出しロジック |
| 6-2 | `.claude/commands/export.md` | Episode 単位のエクスポートに対応 |
| 6-3 | `.claude/commands/chapter-status.md` | `/chapter-status` コマンド（新規） |

### Step 7: Quality Gate 二段階化

| # | ファイル | 変更内容 |
|---|----------|---------|
| 7-1 | `prompts/editor.md` | Episode Gate + Chapter Gate の実装 |

### Step 8: Crew 評価項目追加

| # | ファイル | 変更内容 |
|---|----------|---------|
| 8-1 | `prompts/crew/plotter.md` | episode_hook, web_novel_pacing 追加 |
| 8-2 | `prompts/crew/persona.md` | new_character_necessity, character_sheet_compliance 追加 |

---

## 13. 変更影響範囲サマリー

| カテゴリ | 影響ファイル数 | 新規ファイル数 |
|----------|---------------|---------------|
| prompts/ | 3 | 1 |
| .claude/commands/ | 2 | 3 |
| CLAUDE.md | 1 | 0 |
| **合計** | **6** | **4** |

---

## 14. 承認後の実装手順

この修正計画が承認されたら、以下の順序で実装を進めます:

1. **Step 1〜2**: 構造変更 + Phase 構成変更
2. **Step 3**: キャラクター確認ゲート
3. **Step 4〜5**: 章ゲート + 伏線追跡
4. **Step 6〜7**: 出力変更 + Quality Gate 二段階化
5. **Step 8**: Crew 評価項目追加

各ステップ完了後にテスト実行し、動作確認を行います。

---

*この修正計画を承認いただければ、実装を開始します。*
