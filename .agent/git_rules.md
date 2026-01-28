# AI GITルール (Git Rules)

`Antigravity` プロジェクト共通のGit運用および変更履歴管理のルールです。

## 1. ユーザー設定 (Identity)
- **ユーザー名**: `TSUYOSHI OHNISHI`
- **メールアドレス**: `coin.or.hot.dish@gmail.com`
- **GitHub**: [ohnishi-med](https://github.com/ohnishi-med)

## 2. 管理対象 (Scope)
- **原則**: `Antigravity` 直下の各プロジェクトフォルダ（例: `ai-browser-agent`, `DialyReportPro`, `DocumentTool` など）を、それぞれ独立した1つのGitリポジトリとして管理します。
- **例外 (LandingPage)**: `LandingPage/` フォルダは、メインプロジェクトとは別のエンティティとして扱います。

## 2. LandingPage (LP) の運用
- LPに関する変更は、コミットメッセージの冒頭に `LP:` などのプレフィックスを付与するか、LP専用の単位で管理します。
- 必要に応じて、メインプロジェクトとは独立して Push を行います。

## 3. コミットメッセージ
- 日本語で記述し、変更内容を具体的かつ簡潔に伝えます。
- プレフィックス (feat:, fix:, docs:, chore:, LP: など) を適切に使用します。

## 4. バージョン管理ログ (Version Control Log)
- 重要な変更を行った際は、プロジェクトごとの `Project AI Rules/version_control.md` に以下の内容を記録します。
  - 日付
  - 変更内容の要約
  - 影響範囲
  - 重要な判断理由

## 5. ブランチ管理
- 開発用ブランチ、タスク用ブランチを適切に使い分け、メインブランチの安定性を保ちます。
