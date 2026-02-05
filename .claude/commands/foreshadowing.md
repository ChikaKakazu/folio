# /foreshadowing

伏線の状況一覧を表示します。

## 処理

1. `workspace/current/foreshadowing.json` を読み込む
2. open（未回収）と resolved（回収済）に分類
3. 重要度（major/minor）でソート
4. 一覧を表示

## 表示フォーマット

```
━━━ 伏線状況 ━━━

【未回収（open）】
⚠️ [major] 管制からの不審な指令
   張り: 第2章 第5話 ¶12
   回収予定: 第3章 第10話

⚠️ [minor] 遥の左頬の傷跡
   張り: 第1章 第1話 ¶3
   回収予定: 第4章 第15話

【回収済（resolved）】
✓ [major] ARIAの記憶断片
   張り: 第1章 第3話 ¶8
   回収: 第2章 第7話 ¶22

━━━━━━━━━━━━━━━━━━━━━
未回収: 2件（major: 1, minor: 1）
回収済: 1件
```

## エラーハンドリング

- `foreshadowing.json` が存在しない場合:
  ```
  伏線情報がまだありません。
  /folio でオーケストレーションを開始し、Phase 4 で執筆が始まると追跡されます。
  ```

- 伏線が0件の場合:
  ```
  現在追跡中の伏線はありません。
  ```

## 実装

```
Read workspace/current/foreshadowing.json
Parse and categorize foreshadowings by status
Display formatted output with counts
```
