---
description: Folioの現在の執筆進捗を表示する
---

Folioの執筆セッションの進捗状況を表示してください。

## 実行手順

### 1. 進捗ファイルの確認

```bash
cat workspace/current/progress.json
```

### 2. 進捗の表示

`progress.json` の内容を以下の形式で表示:

```
── Folio Status ──────────────────────────────
 Phase: {phase} | Chapter: {chapter} | Round: {round}/{max_rounds}
 Average Score: {average_score} ({delta})

 Crew Status:
 Plotter: {status} {score}
 Stylist: {status} {score}
──────────────────────────────────────────────
```

#### 表示項目の説明

- **phase**: 現在のフェーズ（plot, draft, refine等）
- **chapter**: 執筆中のチャプター
- **round**: 現在のラウンド数 / 最大ラウンド数
- **average_score**: 全エージェントの平均スコア
- **delta**: 前回からのスコア変化（↑ +0.5 / ↓ -0.2 など）
- **status**: エージェントの状態（working, done, waiting等）
- **score**: エージェントの評価スコア（0.0-10.0）

### 3. エラー処理

`progress.json` が存在しない、または読み込めない場合:

```
── Folio Status ──────────────────────────────
 実行中のセッションがありません

 セッションを開始するには:
 /go <chapter_name> を実行してください
──────────────────────────────────────────────
```

### 4. 追加情報（オプション）

進捗ファイルに以下の情報がある場合は併せて表示:

- **last_update**: 最終更新日時
- **warnings**: 警告メッセージ（スコア低下、スタック等）
- **next_action**: 次のアクション（あれば）

## 注意事項

- このコマンドは読み取り専用
- ファイルの変更は一切行わない
- progress.json のパースエラー時は生データを表示し、Conductorに報告
