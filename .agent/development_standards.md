# AI 開発標準 (Development Standards)

`Superscan` プロジェクトにおける技術スタックとコーディング規約の標準です。

## 1. プロジェクトバージョン
- **Version**: 0.1.0
- **Status**: Phase 1 (Planning & Setup)

## 2. 技術スタック (Tech Stack)

### Backend
- **Language**: Python 3.x
- **Framework**: FastAPI (Asynchronous)
- **Server**: Uvicorn
- **Vision**: OpenCV (映像取得・画像処理)
- **AI**: Azure OpenAI API (GPT-4o)

### Frontend (Chrome Extension)
- **Platform**: Chrome Extension (Manifest V3)
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **Build**: なし (Vanilla JS) または必要に応じて軽量なバンドラ

## 3. Windows 環境での開発
- **ターミナル**: PowerShell を基本としますが、実行ポリシーや権限の問題でエラーが出る場合は、`cmd /c` をプリフィックスとして使用してください。
- **絶対パス**: ファイル操作ツールを使用する際は、常に絶対パスを使用してください。

## 4. フォルダ構成と命名規則
- **命名**: `PascalCase` (Class/Comp) / `snake_case` (Python変数・関数) / `camelCase` (JS変数・関数) / `kebab-case` (ファイル名)
- **構造**:
  - `Application/backend`: Python FastAPI サーバー
  - `Application/extension`: Chrome 拡張機能ソース
  - `Documents/`: 仕様書、設計書
  - `Phase/`: 開発計画、タスク
  - `LandingPage/`: (Optional) 製品紹介ページ
