# Folio

AI駆動の小説オーケストレーションツール。Claude Codeのサブエージェント機能を活用し、複数のAIエージェントが協調して小説を執筆・評価・改稿します。

## 概要

Folioは3層アーキテクチャで構成されています：

```
USER ─────────────────────────────────────────
  │
  │ /folio, /status, /export
  ▼
DESK (CLAUDE.md) ─────────────────────────────
  │ 薄いリレー層 - 創作作業は行わない
  │
  │ Task tool (folio-editor)
  ▼
EDITOR (prompts/editor.md) ───────────────────
  │ オーケストレーションコア
  │ 品質ゲート、状態管理
  │
  │ Task tool (folio-plotter, folio-stylist, etc.)
  ▼
CREW (8 agents) ──────────────────────────────
  Plotter, Persona, Stylist, Pacer,
  Lens, Anchor, Voice, Atlas
```

## クイックスタート

### 前提条件

- [Claude Code](https://claude.ai/code) がインストールされていること
- Claude Max サブスクリプション（並列サブエージェント用）

### 使い方

1. プロジェクトディレクトリでClaude Codeを起動
2. 小説のアイデアを渡して実行：

```
/folio 宇宙飛行士が孤独な火星ミッション中にAIと心を通わせる物語
```

3. 3つのPath（展開案）から選択
4. 執筆ループが完了するまで待機
5. 完成したら出力：

```
/export
```

## コマンド

| コマンド | 説明 |
|----------|------|
| `/folio <プロンプト>` | 小説オーケストレーションを開始 |
| `/status` | 現在の進捗を表示 |
| `/export` | 原稿を `output/` に出力 |

## ワークフロー

```
Phase 0:   Intake      → idea.json（アイデア構造化）
Phase 0.5: Characters  → キャラクターシート生成
Phase 1:   Paths       → 3つの展開案を生成
Phase 2:   Select      → ユーザーが1つ選択
Phase 4:   Loop        → 執筆 → 評価 → 改稿（品質ゲート通過まで）
```

## 品質ゲート

各チャプターは以下の基準を満たすまでループします：

- 全体平均スコア: 7.0以上
- 各評価軸: 6.5以上
- クリティカルな問題: なし
- 最大ラウンド: 5回

## Crewエージェント

| エージェント | 役割 |
|-------------|------|
| Plotter | プロット構成、ドラフト生成 |
| Persona | キャラクター一貫性 |
| Stylist | 文章品質 |
| Pacer | ペーシング |
| Lens | 読者視点、クロスレビュー |
| Anchor | テーマ一貫性 |
| Voice | 会話品質 |
| Atlas | 世界観・設定 |

## ディレクトリ構造

```
folio/
├── CLAUDE.md              # Deskシステムプロンプト
├── prompts/
│   ├── editor.md          # Editorシステムプロンプト
│   ├── crew/              # Crewエージェント定義
│   └── templates/         # テンプレート
├── workspace/
│   ├── current/           # 現在の執筆セッション
│   └── paths/             # 生成されたPath
├── output/                # 出力先
└── .claude/
    ├── settings.json      # サブエージェント設定
    └── commands/          # スラッシュコマンド定義
```

## ドキュメント

- [使い方ガイド](docs/USAGE.md) - 詳細な使用方法
- [CLAUDE.md](CLAUDE.md) - Deskのシステムプロンプト

## ライセンス

MIT
