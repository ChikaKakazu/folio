# /chapter-status

各章の確認状態を表示します。

## 処理

1. `workspace/current/chapters/` 配下の各章ディレクトリをスキャン
2. 各章の `status.json` を読み込む
3. `confirmed` / `pending` / `in_progress` の状態を表示
4. Episode の完了状況も併せて表示

## 表示フォーマット

```
━━━ 章の進捗状況 ━━━

第1章「旅立ち」
  状態: ✓ confirmed（ユーザー承認済み）
  話数: 第1話〜第4話（4話）
  スコア: 平均 7.6

第2章「試練」
  状態: ⏳ in_progress（執筆中）
  話数: 第5話〜第6話（2/4話 完了）
  現在: 第7話 Round 2

第3章「真実」
  状態: ○ pending（未着手）

━━━━━━━━━━━━━━━━━━━━━
確認済み: 1章 / 執筆中: 1章 / 未着手: 1章
総話数: 6話完了 / 12話予定
```

## エラーハンドリング

- `workspace/current/chapters/` が存在しない場合:
  ```
  章の情報がまだありません。
  /folio でオーケストレーションを開始してください。
  ```

- `selected_path.json` がない場合:
  ```
  パスが選択されていません。
  /folio を実行し、Phase 2 でパスを選択してください。
  ```

## 状態の意味

| status | 意味 |
|--------|------|
| `confirmed` | 全話完了＋ユーザー承認済み。次章に進める状態 |
| `in_progress` | 執筆中。Episode ループを実行中 |
| `pending` | 未着手。前章の確認待ち |

## 実装

```
Glob workspace/current/chapters/ch*/status.json
For each chapter:
  Read status.json
  Count episodes in ep*/ directories
  Read chapter-review.json if exists for scores
Display formatted summary
```
