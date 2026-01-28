# AI 開発標準 (Development Standards)

`Antigravity` プロジェクトにおける技術スタックとコーディング規約の標準です。

## 1. 推奨技術スタック
- **Frontend**: Vite + React + TypeScript
- **Styling**: TailwindCSS (プロジェクトによりVanilla CSSも検討)
- **State Management**: React Hooks (必要に応じて Context API や Zustand)
- **Build Tool**: npm / npx

## 2. Windows 環境での開発
- **ターミナル**: PowerShell を基本としますが、実行ポリシーや権限の問題でエラーが出る場合は、`cmd /c` をプリフィックスとして使用してください。
- **絶対パス**: ファイル操作ツールを使用する際は、常に絶対パスを使用してください。

## 3. フォルダ構成と命名規則
- **命名**: `PascalCase` (コンポーネント) / `camelCase` (関数・変数) / `kebab-case` (ファイル名・フォルダ名) を基本とします。
- **構造**:
  - `Application/`: メインソースコード（frontend / backend を含む）
  - `Documents/`: 要件定義、仕様書、設計書、進捗報告
  - `LandingPage/`: 製品紹介などのランディングページ
  - `Progress/`: 進捗管理・マイルストーン
  - `Project AI Rules/`: プロジェクト固有のAI指示
