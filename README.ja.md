<div align="center">

  <h1>ComfyUI Skill CLI</h1>

  <p><strong>AI エージェント向けに設計された、ComfyUI ワークフロー管理・実行用の CLI ツール</strong></p>

  <p>
    Shell コマンドを実行できる AI エージェント（Claude Code、Codex、OpenClaw など）であれば、この CLI 経由で ComfyUI を利用できます。
  </p>

  <p>
    <a href="https://pypi.org/project/comfyui-skill-cli/"><img src="https://img.shields.io/pypi/v/comfyui-skill-cli?style=flat&color=4F46E5&logo=pypi&logoColor=white" alt="PyPI"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=10B981" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3B82F6&style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/stargazers"><img src="https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=EAB308&logo=github" alt="GitHub stars"></a>
  </p>

  <p>
    <a href="#インストール">インストール</a> ·
    <a href="#クイックスタート">クイックスタート</a> ·
    <a href="#コマンド">コマンド</a> ·
    <a href="#ai-エージェント向け">AI エージェント向け</a>
  </p>

  <p>
    <a href="./README.md">English</a> ·
    <a href="./README.zh.md">简体中文</a> ·
    <a href="./README.zh-TW.md">繁體中文</a> ·
    <strong>日本語</strong> ·
    <a href="./README.ko.md">한국어</a> ·
    <a href="./README.es.md">Español</a>
  </p>

</div>

---

## なぜ comfyui-skill なのか？

| 機能 | 価値 |
|------|------|
| **エージェントネイティブ** | 構造化 JSON 出力に対応し、パイプ処理にも向いていて、AI エージェントからの呼び出しを前提に設計されています |
| **ゼロ設定** | カレントディレクトリの `config.json` と `data/` を読み込むため、すぐに使い始められます |
| **ライフサイクル全体をカバー** | ワークフローの発見、インポート、実行、キャンセル、依存関係の管理まで 1 つのツールで対応できます |
| **マルチサーバー対応** | 複数の ComfyUI インスタンスをまとめて管理し、ジョブを適切なハードウェアに振り分けられます |
| **モデル探索** | 対象サーバー上のモデルフォルダと利用可能なモデル名を直接確認できます |
| **複数ワークフロー管理** | 複数のワークフローをまとめてインポート、有効化、無効化、削除、移行できます |
| **エラーガイダンス** | OOM、認証失敗、モデル不足など、よくある失敗に対して対処しやすいヒントを返します |

## インストール

```bash
pipx install comfyui-skill-cli
```

または pip:

```bash
pip install comfyui-skill-cli
```

### 更新

```bash
pipx upgrade comfyui-skill-cli
```

### 開発モード

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

## クイックスタート

```bash
# 1. ComfyUI Skills プロジェクトのディレクトリへ移動
cd /path/to/your-skills-project

# 2. サーバー状態を確認
comfyui-skill server status

# 3. 利用可能なワークフローを一覧
comfyui-skill list

# 4. ワークフローを実行
comfyui-skill run local/txt2img --args '{"prompt": "a white cat"}'
```

すべてのコマンドで `--json` を指定でき、構造化データとして出力できます。

## ID 規約

ワークフローは `<server_id>/<workflow_id>` 形式で指定します。

```bash
comfyui-skill run local/txt2img          # サーバーを明示
comfyui-skill run txt2img                # デフォルトサーバーを使用
comfyui-skill run txt2img -s my_server   # --server で上書き
```

## コマンド

### ワークフローの発見と実行

| コマンド | 説明 |
|----------|------|
| `comfyui-skill list` | 利用可能なワークフローとパラメータを一覧表示 |
| `comfyui-skill info <id>` | ワークフロー詳細とパラメータ schema を表示 |
| `comfyui-skill run <id> --args '{...}'` | ワークフローを実行（同期、リアルタイムWebSocketストリーミング） |
| `comfyui-skill run <id> --validate` | ワークフローを実行せずに検証 |
| `comfyui-skill submit <id> --args '{...}'` | ワークフローを送信（非同期） |
| `comfyui-skill status <prompt_id>` | 実行状態を確認し、見つかった結果を表示 |
| `comfyui-skill cancel <prompt_id>` | 実行中または待機中のジョブをキャンセル |
| `comfyui-skill upload <file>` | ワークフローで使うためのファイルを ComfyUI にアップロード |
| `comfyui-skill upload <file> --mask` | インペインティング用マスク画像のアップロード |
| `comfyui-skill upload --from-output <prompt_id>` | 前回実行の出力を次のワークフロー入力として再利用 |

### キューとリソース管理

| コマンド | 説明 |
|----------|------|
| `comfyui-skill queue list` | 実行中および待機中のジョブを表示 |
| `comfyui-skill queue clear` | 待機中のジョブをすべて削除 |
| `comfyui-skill queue delete <prompt_id>...` | 指定したジョブをキューから削除 |
| `comfyui-skill free` | GPU メモリを解放し、モデルをアンロード |
| `comfyui-skill free --models` | モデルのみアンロード |
| `comfyui-skill free --memory` | キャッシュメモリのみ解放 |

### ノード・モデル探索

| コマンド | 説明 |
|----------|------|
| `comfyui-skill nodes list` | カテゴリ別に利用可能な全ComfyUIノードを一覧表示 |
| `comfyui-skill nodes info <class>` | ノードの入出力スキーマを表示 |
| `comfyui-skill nodes search <query>` | 名前やカテゴリでノードを検索 |
| `comfyui-skill models list` | 利用可能なモデルフォルダを一覧表示 |
| `comfyui-skill models list <folder>` | 指定フォルダ内のモデルを一覧表示（例: `checkpoints`, `loras`） |

### ワークフロー管理

| コマンド | 説明 |
|----------|------|
| `comfyui-skill workflow import <path>` | ワークフローをインポート（形式自動判別、schema 自動生成） |
| `comfyui-skill workflow import --from-server` | ComfyUI サーバーの userdata から 1 つ以上のワークフローをインポート |
| `comfyui-skill workflow enable <id>` | ワークフローを有効化 |
| `comfyui-skill workflow disable <id>` | ワークフローを無効化 |
| `comfyui-skill workflow delete <id>` | ワークフローを削除 |

### サーバー管理

| コマンド | 説明 |
|----------|------|
| `comfyui-skill server list` | 設定済みサーバーを一覧表示 |
| `comfyui-skill server status` | ComfyUI サーバーがオンラインか確認 |
| `comfyui-skill server add --id <id> --url <url>` | 新しいサーバーを追加 |
| `comfyui-skill server enable/disable <id>` | サーバーの有効/無効を切り替え |
| `comfyui-skill server remove <id>` | サーバーを削除 |
| `comfyui-skill server stats` | VRAM、RAM、GPU情報を表示（`--all`で全サーバー） |

### 依存関係管理

| コマンド | 説明 |
|----------|------|
| `comfyui-skill deps check <id>` | 不足しているカスタムノードやモデルを確認 |
| `comfyui-skill deps install <id> --all` | 不足依存関係を自動検出してまとめてインストール |
| `comfyui-skill deps install <id> --repos '[...]'` | 指定したカスタムノードをインストール |
| `comfyui-skill deps install <id> --models` | Manager 経由で不足モデルをインストール |

### 設定と履歴

| コマンド | 説明 |
|----------|------|
| `comfyui-skill config export --output <path>` | 設定とワークフローをまとめてエクスポート |
| `comfyui-skill config import <path>` | 設定バンドルをインポート（`--dry-run` 対応） |
| `comfyui-skill history list <id>` | 実行履歴を一覧表示 |
| `comfyui-skill history show <id> <run_id>` | 特定の実行詳細を表示 |
| `comfyui-skill jobs list` | サーバー側ジョブ履歴を表示（`--status`でフィルタ） |
| `comfyui-skill jobs show <prompt_id>` | 特定ジョブの詳細を表示 |
| `comfyui-skill logs show` | ComfyUIサーバーログを表示 |
| `comfyui-skill templates list` | カスタムノードのワークフローテンプレートを一覧表示 |
| `comfyui-skill templates subgraphs` | 再利用可能なサブグラフコンポーネントを一覧表示 |

### グローバルオプション

| オプション | 説明 |
|------------|------|
| `--json, -j` | JSON 出力を強制 |
| `--output-format` | 出力形式: `text`, `json`, `stream-json` |
| `--server, -s` | サーバー ID を指定 |
| `--dir, -d` | データディレクトリを指定（デフォルト: カレントディレクトリ） |
| `--verbose, -v` | 詳細出力 |
| `--no-update-check` | CLI の自動更新チェックをスキップ |

### 出力モード

| モード | 用途 | 形式 |
|--------|------|------|
| Text | TTY ターミナル | Rich テーブルと進捗表示 |
| JSON | パイプまたは `--json` | 単一の JSON 結果 |
| Stream JSON | `--output-format stream-json` | リアルタイム NDJSON イベント |
| Errors | 常に | stderr |

## よくある管理タスク

### サーバー上のモデルを確認する

```bash
comfyui-skill models list
comfyui-skill models list checkpoints
comfyui-skill models list loras
```

ワークフローや schema に書く前にモデル名を確認したいときに便利です。

### 複数のワークフローを管理する

```bash
# ComfyUI サーバー userdata にあるワークフローをプレビュー
comfyui-skill workflow import --from-server --preview

# 名前に一致するワークフローをサーバーから取り込む
comfyui-skill workflow import --from-server --name sdxl

# 一時的に無効化 / 再度有効化
comfyui-skill workflow disable local/old-flow
comfyui-skill workflow enable local/old-flow

# もう公開しないワークフローを削除
comfyui-skill workflow delete local/old-flow
```

### ワークフローバンドルを別マシンへ移す

```bash
comfyui-skill config export --output ./bundle.json --portable-only
comfyui-skill config import ./bundle.json --dry-run
comfyui-skill config import ./bundle.json --apply-environment
```

複数のワークフローを一度に移したい場合は、個別に再インポートするよりこの方法の方が効率的です。

### 実行前にモデルと依存関係を確認する

```bash
comfyui-skill deps check local/txt2img
comfyui-skill deps install local/txt2img --models
comfyui-skill deps install local/txt2img --all
```

## AI エージェント向け

この CLI は `SKILL.md` から呼び出されることを想定して設計されています。典型的なエージェント利用フローは次のとおりです。

```bash
comfyui-skill server status --json                    # 1. サーバー確認
comfyui-skill list --json                             # 2. ワークフロー発見
comfyui-skill info local/txt2img --json               # 3. パラメータ確認
comfyui-skill run local/txt2img --args '{...}' --json # 4. 実行
```

### ワークフロー連結（多段パイプライン）

```bash
# 最初のワークフローを実行
comfyui-skill run local/txt2img --args '{"prompt": "a cat"}' --json

# 出力を次のワークフローへ引き継ぐ
comfyui-skill upload --from-output <prompt_id> --json
comfyui-skill run local/upscale --args '{"image": "<uploaded_name>"}' --json
```

### インポートと検証

```bash
comfyui-skill workflow import ./workflow.json --check-deps --json
comfyui-skill deps install local/my-workflow --all --json
```

## コントリビューション

コントリビューション歓迎です。設計方針や PR フローについては、メインリポジトリの [Contributing Guide](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/blob/main/CONTRIBUTING.md) を参照してください。

## 関連リソース

- [ComfyUI Skills OpenClaw](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw) — メインの skills リポジトリ
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — この CLI がオーケストレーションするバックエンド
- [Typer](https://typer.tiangolo.com/) — 本プロジェクトで使用している CLI フレームワーク
