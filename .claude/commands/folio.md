---
description: |
  Folio小説オーケストレーションのメインコマンド。
  プロンプトを受け取り、Editor subagentを起動して
  Phase 0 → 1 → 2 → 4 のフローを制御します。

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

### Phase 2: 進捗監視とユーザー中継

6. **progress.jsonを定期的にチェック**:
   - Editorが更新する `workspace/current/progress.json` を監視
   - 進捗状況をユーザーに表示

7. **ユーザー選択の中継**:
   - `progress.json` の `awaiting_user: true` を検知
   - 選択肢（path-A, path-B, path-C）をユーザーに提示
   - ユーザーの選択を受け取る
   - 選択結果を `workspace/current/user_selection.json` に書き込む:
   ```json
   {
     "type": "path_selection",
     "selected_path": "path-A",
     "metadata": {
       "selected_at": "YYYY-MM-DDTHH:MM:SSZ"
     }
   }
   ```
   - Editor subagentに選択完了を通知（再起動または状態更新）

### Phase 3: 完了報告

6. **Editorの完了を待機**:
   - Phase 4ループが完了するまで待機
   - 最終的な成果物を確認

7. **ユーザーに報告**:
   - 完成した章の一覧
   - 各章のクオリティスコア
   - `workspace/current/chapters/` の構造

## Deskの役割

- **Silent Relay**: Editorとユーザーの間を中継（Editorは直接話さない）
- **Progress Display**: `progress.json` を読み取り、進捗をビジュアル表示
- **User Input**: Path選択やその他のユーザー判断を受け取りEditorへ渡す

## Phase Flow概要

```
Phase 0: Intake       → idea.json作成
Phase 1: Paths        → 3つの展開案生成
Phase 2: Select       → ユーザーが1つ選択
Phase 4: Loop         → Draft → Review → Refine（Quality Gateまで）
```

## 注意事項

- Editorは **opus** モデルで起動（オーケストレーション負荷が高いため）
- Crew agents（Plotter, Stylist等）は **sonnet** で起動（Editorが管理）
- `workspace/current/progress.json` がDeskとEditorの唯一の通信手段
- ユーザーに直接JSONを見せず、わかりやすく翻訳して表示

## セキュリティ対策一覧

1. **入力長制限**: 5000文字まで（DoS攻撃防止）
2. **プロンプトインジェクション対策**: ユーザー入力をJSONファイルに隔離し、テンプレート経由で渡す
3. **パストラバーサル対策**: 絶対パスでディレクトリ検証、シンボリックリンクチェック
4. **Phase 2選択の構造化**: 選択結果もJSONファイルで管理し、直接プロンプトに埋め込まない

## 参照

- Editor定義: `prompts/editor.md`
- Plotter定義: `prompts/plotter.md`
- Stylist定義: `prompts/stylist.md`
