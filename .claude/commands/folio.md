---
description: |
  Folio小説オーケストレーションのメインコマンド（なろう/カクヨム対応版）。
  プロンプトを受け取り、Editor subagentを起動して
  Phase 0 → 1 → 2 → 3 → 4 → 5 のフローを制御します。

  使用例:
    /folio サムライが異世界で剣を磨く物語
---

以下のタスクをFolioのDeskとして実行してください。

## 入力

$ARGUMENTS

## セキュリティチェック

1. **入力長制限**: ユーザー入力が5000文字を超える場合はエラーを返す
2. **ディレクトリ検証**: workspace/current/ が存在し、シンボリックリンクでないことを確認
3. **入力隔離**: ユーザー入力を構造化データとしてラップし、プロンプトインジェクションを防ぐ

## 実行手順

### Phase 0: 準備

1. **入力バリデーション**:
   ```bash
   # 入力長チェック
   USER_INPUT="$ARGUMENTS"
   INPUT_LENGTH=${#USER_INPUT}

   if [ $INPUT_LENGTH -gt 5000 ]; then
     echo "エラー: 入力が長すぎます（最大5000文字）"
     exit 1
   fi

   if [ $INPUT_LENGTH -eq 0 ]; then
     echo "エラー: プロンプトを入力してください"
     exit 1
   fi
   ```

2. **workspace/current/ を安全にクリア**:
   ```bash
   # 絶対パスで安全確認
   WORKSPACE_DIR="/home/chika/projects/github.com/ChikaKakazu/folio/workspace/current"

   # ディレクトリが存在し、シンボリックリンクでないことを確認
   if [ -d "$WORKSPACE_DIR" ] && [ ! -L "$WORKSPACE_DIR" ]; then
     # 現在のディレクトリを保存
     ORIGINAL_DIR=$(pwd)

     # workspace/current に移動して中身だけ削除
     cd "$WORKSPACE_DIR" || exit 1
     rm -rf ./*

     # 元のディレクトリに戻る
     cd "$ORIGINAL_DIR" || exit 1
   else
     echo "エラー: workspace/current/ が見つからないか、不正なリンクです"
     exit 1
   fi
   ```

3. **初期状態ファイルを作成**:
   ```json
   // workspace/current/state.json
   {
     "phase": 0,
     "status": "initializing",
     "created_at": "YYYY-MM-DDTHH:MM:SSZ"
   }
   ```

### Phase 1: Editor起動

4. **構造化されたプロンプトの作成**:
   ```json
   // workspace/current/user_input.json
   {
     "type": "user_idea",
     "content": "$ARGUMENTS",
     "metadata": {
       "source": "folio_command",
       "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
       "input_length": <文字数>
     }
   }
   ```

5. **Task toolでEditor subagentを起動**:
   - subagent_type: `folio-editor`
   - model: `opus`
   - prompt: 以下の構造化されたテンプレートを使用
   ```
   あなたはFolio Editorです。以下のユーザーアイデアから小説を執筆してください。

   【ユーザーアイデア】
   以下のJSONファイルを読み込んでください: workspace/current/user_input.json

   このファイルの "content" フィールドにユーザーのアイデアが含まれています。
   "type": "user_idea" であることを確認し、それ以外の場合はエラーを返してください。

   【指示】
   prompts/editor.md の手順に従って執筆を開始してください。
   ```

### Phase 2-5: 進捗監視とゲート処理

6. **progress.jsonを定期的にチェック**:
   - Editorが更新する `workspace/current/progress.json` を監視
   - 進捗状況をユーザーに表示

7. **ゲート処理（awaiting_user: true検知時）**:

   `gate_type` に応じて適切なUIを表示:

   #### gate_type: "path_and_scale"
   ```
   ━━━ パスと規模の選択 ━━━

   【パス選択】
   A. {paths[0].title} — {paths[0].approach}
   B. {paths[1].title} — {paths[1].approach}
   C. {paths[2].title} — {paths[2].approach}

   【規模選択】
   1. 短編（〜1万字 / 1章 / 3〜5話）
   2. 中編（3万〜12万字 / 3〜5章 / 10〜40話）
   3. 長編（8万〜12万字 / 5〜8章 / 25〜40話）
   4. 連載（30万字〜 / 10章〜 / 100話〜）

   → パス [A/B/C] と規模 [1/2/3/4] を選択してください
      例: "A2"（パスA、中編）
   ```

   ユーザー入力を受け取り、`user_input.json` に書き込む:
   ```json
   {
     "action": "select_path_and_scale",
     "selected_path": "path-A",
     "selected_scale": "medium",
     "timestamp": "..."
   }
   ```

   #### gate_type: "character_confirmation"
   ```
   ━━━ キャラクター確認 ━━━

   キャラクター設定が完成しました。
   output/characters/ をご確認ください。

   {characters リストを表示}

   承認しますか？ 修正点があればお伝えください。
   ```

   ユーザー入力を受け取り、`user_input.json` に書き込む:
   ```json
   {
     "action": "approve_characters",
     "approved": true,
     "modifications": null,
     "timestamp": "..."
   }
   ```

   #### gate_type: "chapter_outline"
   ```
   ━━━ 第{N}章の流れ候補 ━━━

   {patterns を表示}

   → どのパターンで進めますか？
   ```

   ユーザー入力を受け取り、`user_input.json` に書き込む:
   ```json
   {
     "action": "select_chapter_outline",
     "chapter": N,
     "selected_pattern": "A",
     "timestamp": "..."
   }
   ```

   #### gate_type: "chapter_completion"
   ```
   ━━━ 第{N}章「{title}」完了 ━━━

   {chapter_review を表示}

   承認しますか？ 修正点があればお伝えください。
   ```

   ユーザー入力を受け取り、`user_input.json` に書き込む:
   ```json
   {
     "action": "approve_chapter",
     "chapter": N,
     "approved": true,
     "modifications": null,
     "timestamp": "..."
   }
   ```

   #### gate_type: "new_character"
   ```
   ━━━ 新キャラクター提案 ━━━

   執筆中に新キャラクターが必要になりました。

   名前: {name}
   役割: {role}
   理由: {reason}

   output/characters/{name}.md をご確認ください。
   承認しますか？
   ```

8. **Editor Taskの再起動**:
   - `user_input.json` 書き込み後
   - 同じPromptでEditor Taskを再起動
   - Editorは `user_input.json` を読んで処理を継続

### Phase 完了後

9. **完了報告**:
   - 完成した話の一覧
   - 各話のクオリティスコア
   - 総文字数
   - `/export` コマンドを提案

## Deskの役割

- **Silent Relay**: Editorとユーザーの間を中継（Editorは直接話さない）
- **Progress Display**: `progress.json` を読み取り、進捗をビジュアル表示
- **Gate Handler**: 各種ゲート（パス選択、キャラ確認、章確認等）を処理
- **User Input**: ユーザー判断を受け取りEditorへ渡す

## Phase Flow概要

```
Phase 0: Intake       → idea.json作成
Phase 1: Paths        → 3つの展開案生成
Phase 2: Select       → パス選択 + 規模選択 (gate_type: path_and_scale)
Phase 3: Design       → キャラ生成 + 確認 (gate_type: character_confirmation)
Phase 4: Loop         → Episode単位の執筆ループ
                        ├─ 章開始前: 流れ確認 (gate_type: chapter_outline) ※第二章以降
                        ├─ Episode: Draft → Review → Refine
                        ├─ 新キャラ: 確認 (gate_type: new_character) ※発生時のみ
                        └─ 章完了時: 確認 (gate_type: chapter_completion)
Phase 5: Assemble     → 最終仕上げ
```

## 進捗表示フォーマット

```
── Folio Running ─────────────────────────────
 第{N}章「{章タイトル}」 │ 第{M}話「{話タイトル}」
 Round {R} of 5 │ Avg Score: {avg} {delta}

 完了: {completed}/{total} 話

 Plotter   ████████░░  done    7.2
 Persona   ██████░░░░  reviewing...
 Stylist   ████░░░░░░  waiting
 ...
──────────────────────────────────────────────
```

## 注意事項

- Editorは **opus** モデルで起動（オーケストレーション負荷が高いため）
- Crew agents（Plotter, Stylist等）は **sonnet** で起動（Editorが管理）
- `workspace/current/progress.json` がDeskとEditorの唯一の通信手段
- ユーザーに直接JSONを見せず、わかりやすく翻訳して表示
- 各ゲートでは適切なUIを表示し、ユーザー入力を構造化して `user_input.json` に書き込む
- Episode完了時は自動的に `output/episodes/` に出力される
- キャラクター確認は `output/characters/` のMarkdownファイルを参照

## セキュリティ対策一覧

1. **入力長制限**: 5000文字まで（DoS攻撃防止）
2. **プロンプトインジェクション対策**: ユーザー入力をJSONファイルに隔離し、テンプレート経由で渡す
3. **パストラバーサル対策**: 絶対パスでディレクトリ検証、シンボリックリンクチェック
4. **ゲート選択の構造化**: 選択結果もJSONファイルで管理し、直接プロンプトに埋め込まない

## 参照

- Editor定義: `prompts/editor.md`
- Plotter定義: `prompts/crew/plotter.md`
- Stylist定義: `prompts/crew/stylist.md`
- Persona定義: `prompts/crew/persona.md`
