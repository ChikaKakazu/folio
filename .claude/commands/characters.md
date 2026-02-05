# /characters

キャラクター一覧を表示します。

## 処理

1. `output/characters/` ディレクトリを確認
2. キャラクターファイル一覧を取得
3. `_index.md` があれば内容を表示
4. なければ個別ファイルをリスト表示

## 表示フォーマット

```
━━━ 登場人物一覧 ━━━

【メインキャラクター】
- 水野 遥（主人公） → output/characters/水野遥.md
- ARIA（AI相棒） → output/characters/ARIA.md

【サブキャラクター】
- 佐藤 健一（地上管制責任者） → output/characters/佐藤健一.md

詳細は各ファイルをご確認ください。
```

## エラーハンドリング

- `output/characters/` が存在しない場合:
  ```
  キャラクター情報がまだありません。
  /folio でオーケストレーションを開始し、Phase 3 完了後に確認できます。
  ```

## 実装

```
Read output/characters/_index.md if exists
else Glob output/characters/*.md and list files
Display formatted output
```
