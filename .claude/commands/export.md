# /export

完成した原稿をエクスポートします。

## 使用方法

```bash
/export [--format=<format>]
```

## オプション

- `--format=<format>` - 出力形式（デフォルト: md）
  - `md` - Markdown形式
  - `txt` - プレーンテキスト形式

## 動作

1. `workspace/current/idea.json` からタイトルを取得
2. `workspace/current/chapters/` の全章をスキャン
3. 各章の最終ドラフト（`draft-{最大R}.md`）を結合
4. `output/manuscript.md`（または `.txt`）に出力

## 出力形式

```markdown
# {タイトル}

{章1の最終ドラフト内容}

---

{章2の最終ドラフト内容}

---

...
```

## エラー処理

- `workspace/current/chapters/` が存在しない場合:
  ```
  エクスポート可能なドラフトがありません。
  /plan コマンドで章立てを作成してください。
  ```

- 章が存在するがドラフトファイルがない場合:
  ```
  警告: 章{N}のドラフトが見つかりません（スキップします）
  ```

- `idea.json` が存在しない場合:
  ```
  エラー: idea.json が見つかりません。
  /init コマンドでプロジェクトを初期化してください。
  ```

## 実装例

```bash
# Markdown形式でエクスポート（デフォルト）
/export

# テキスト形式でエクスポート
/export --format=txt
```

## 期待される出力

```
原稿をエクスポートしています...

✓ タイトル: 「異世界転生した俺は、村人Aとして生きることにした」
✓ 章1: 第一章「転生」（draft-3.md）
✓ 章2: 第二章「村での生活」（draft-2.md）
✓ 章3: 第三章「隠された力」（draft-1.md）

エクスポート完了: output/manuscript.md
総文字数: 15,234文字
```

## 関連コマンド

- `/plan` - 章立て作成
- `/write` - ドラフト執筆
- `/review` - レビュー実施
