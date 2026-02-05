# Character Sheet Template

キャラクター情報を構造化するためのテンプレート。
Plotter がドラフト生成時に参照し、Persona がレビュー時に整合性をチェックする。

## 出力形式
workspace/current/characters/{character_id}.json

## スキーマ

```json
{
  "id": "protagonist",
  "name": "柊真人",
  "role": "主人公",
  "age": 35,
  "occupation": "宇宙飛行士",
  "appearance": {
    "height": "178cm",
    "build": "引き締まった体型",
    "features": ["短い黒髪", "鋭い目つき"]
  },
  "personality": {
    "traits": ["責任感が強い", "頑固", "内向的"],
    "strengths": ["冷静な判断力", "技術への理解"],
    "weaknesses": ["感情表現が苦手", "他者に頼れない"]
  },
  "background": {
    "family": "妻・美咲、娘・陽菜（5歳）",
    "history": "幼少期に父を事故で失い、母子家庭で育つ。宇宙飛行士を目指した動機は父への憧れ。",
    "motivation": "家族のもとに帰る"
  },
  "arc": {
    "start": "孤独を恐れ、他者を拒絶",
    "growth": "AIとの交流で心を開く",
    "end": "繋がりの価値を理解"
  },
  "voice": {
    "speech_pattern": "短く断定的",
    "vocabulary": "技術用語を多用",
    "quirks": ["独り言が多い", "敬語を使わない"]
  },
  "relationships": [
    {"character": "ソラ", "type": "AI companion", "dynamic": "拒絶→信頼"}
  ]
}
```

## フィールド説明

### id (string, required)
キャラクターの一意識別子。ファイル名と一致させる。

### name (string, required)
キャラクターの名前。

### role (string, required)
物語内での役割（主人公、ヒロイン、敵対者、サポーター等）。

### age (number, optional)
年齢。

### occupation (string, optional)
職業。

### appearance (object, optional)
外見の特徴。
- `height`: 身長
- `build`: 体型
- `features`: 特徴的な外見（配列）

### personality (object, required)
性格・心理。
- `traits`: 性格の特徴（配列）
- `strengths`: 長所（配列）
- `weaknesses`: 短所（配列）

### background (object, optional)
背景情報。
- `family`: 家族構成
- `history`: 過去の経歴
- `motivation`: 行動動機

### arc (object, optional)
キャラクターアーク（変化）。
- `start`: 物語開始時の状態
- `growth`: 成長のプロセス
- `end`: 物語終了時の状態

### voice (object, optional)
話し方・言語表現。
- `speech_pattern`: 話し方の特徴
- `vocabulary`: 使用語彙
- `quirks`: 口癖や癖（配列）

### relationships (array, optional)
他キャラクターとの関係。
- `character`: 関係するキャラクター名
- `type`: 関係の種類
- `dynamic`: 関係の変化

## 生成タイミング

Phase 0.5: Character Generation にて自動生成される。
Editor が `idea.json` の `characters` フィールドから主要キャラを抽出し、
Plotter に各キャラのシート生成を依頼する。

## レビュー利用

- **Plotter**: ドラフト生成時に参照し、キャラの行動や台詞を整合させる
- **Persona**: レビュー時にキャラシートと照合し、一貫性を評価する
- **Voice**: 会話シーンのレビュー時に `voice` フィールドを参照する

## 更新プロトコル

- 物語の展開に伴いキャラが成長した場合、Editor が Persona に更新を依頼
- 更新は `workspace/current/characters/{character_id}.json` に上書き
- 更新履歴は `workspace/current/characters/history/{character_id}-{timestamp}.json` にバックアップ
