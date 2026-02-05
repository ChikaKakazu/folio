# Character Export Template

キャラクターシートを `output/characters/` にMarkdown形式でエクスポートする際のテンプレート。
ユーザーが直接確認できる形式で出力する。

## 出力先
`output/characters/{キャラ名}.md`

## テンプレート

```markdown
# {名前}（{読み}）

## 基本情報

| 項目 | 内容 |
|---|---|
| 名前 | {名前}（{読み}） |
| 年齢 | {年齢} |
| 性別 | {性別} |
| 役割 | {role: protagonist/supporting/antagonist} |
| 初登場 | 第{N}章 第{M}話 |

## 行動原理（最重要）

| 項目 | 内容 |
|---|---|
| 目的 | {goals.long_term} |
| 動機 | {background.motivation} |
| 信念 | {personality.core_belief} |
| 好き | {personality.likes} |
| 嫌い | {personality.dislikes} |

## 精神的特徴

| 項目 | 内容 |
|---|---|
| 性格（長所） | {personality.strengths} |
| 性格（短所） | {personality.weaknesses} |
| 口調 | {voice.speech_pattern} |
| 癖 | {voice.quirks} |

## 肉体的特徴

| 項目 | 内容 |
|---|---|
| 容姿 | {appearance.general} |
| 髪型 | {appearance.hair} |
| 服装 | {appearance.clothing} |
| 特徴 | {appearance.distinguishing_features} |

## 背景（バックボーン）

{background.history}

## キャラクターアーク

```
{arc.start} → {arc.growth} → {arc.end}
```

## 関連キャラクター

{For each relationship:}
- [{character}](./{character}.md) — {dynamic}

## 登場話一覧

| 話 | 役割 |
|---|---|
| 第{M}話「{title}」 | {主要/登場/言及} |

---
[← 登場人物一覧に戻る](./_index.md)
```

## フィールドマッピング

JSONシート（`workspace/current/characters/{id}.json`）からMarkdownへの変換:

| Markdown項目 | JSONフィールド |
|---|---|
| 名前 | `name` |
| 読み | `name_reading` |
| 年齢 | `age` |
| 性別 | `gender` |
| 役割 | `role` |
| 初登場 | `first_appearance.chapter`, `first_appearance.episode` |
| 目的 | `goals.long_term` |
| 動機 | `background.motivation` |
| 信念 | `personality.core_belief` |
| 好き | `personality.likes` |
| 嫌い | `personality.dislikes` |
| 性格（長所） | `personality.strengths` (配列をカンマ区切り) |
| 性格（短所） | `personality.weaknesses` (配列をカンマ区切り) |
| 口調 | `voice.speech_pattern` |
| 癖 | `voice.quirks` (配列をカンマ区切り) |
| 容姿 | `appearance.general` |
| 髪型 | `appearance.hair` |
| 服装 | `appearance.clothing` |
| 特徴 | `appearance.distinguishing_features` |
| 背景 | `background.history` |
| アーク開始 | `arc.start` |
| アーク成長 | `arc.growth` |
| アーク終了 | `arc.end` |
| 関連キャラ | `relationships[]` |
| 登場話 | `appearances[]` |

## インデックスファイル

`output/characters/_index.md` を同時に生成:

```markdown
# 登場人物一覧

## 主要キャラクター

| 名前 | 役割 | 初登場 |
|---|---|---|
| [{name}](./{name}.md) | {role} | 第{N}章 第{M}話 |

## サブキャラクター

| 名前 | 役割 | 初登場 |
|---|---|---|
| [{name}](./{name}.md) | {role} | 第{N}章 第{M}話 |

---
総キャラクター数: {count}
```

## 生成タイミング

- **Phase 3: Design** — キャラクター生成後、確認ゲート前に出力
- **Phase 4: Loop** — 新キャラクター承認後に追加出力
- **アーク更新時** — キャラクターの成長に伴い `arc` セクションを更新

## 注意事項

- 空のフィールドは「不明」または「—」で表示
- 配列フィールドは読点（、）またはカンマ区切りで連結
- 関連キャラクターは相対リンクで接続
- 登場話一覧は執筆進行に伴い自動更新
