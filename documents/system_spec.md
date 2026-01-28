# Camera-EMR Linkage System Specification （電子カルテ連携システム仕様書）

## 概要 (Overview)
Webカメラでのスキャンと画像解析を行うローカルPythonサーバーと、ブラウザ操作およびファイルアップロードを行うChrome拡張機能を使用し、既存の電子カルテ（Chrome上で動作するWebアプリケーション）へのファイルアップロードを自動化するシステムです。

## ユーザーと前提 (User Role & Assumption)
- **ユーザー**: 医療スタッフ
- **環境**: Chromeブラウザ（電子カルテにログイン済みであること）
- **制約**: ログインの自動化は行わない。既存のセッションを利用する。

## システムワークフロー (System Workflow)
1.  **スキャン (Python Backend)**
    - **トリガー**: Webカメラが書類を検知（動体検知 -> 1.5秒静止）
    - **アクション**: 画像キャプチャ
    - **解析**: Azure OpenAI (GPT-4o) を使用して「患者ID」を抽出
    - **保存**: メモリ内に {PatientID, Image(Base64)} を一時保存
2.  **ナビゲーション & アップロード (Chrome Extension)**
    - **トリガー**: `GET /check_new_scan` をポーリング
    - **アクション**: 
        - 新しいデータを受信
        - 現在または新しいタブで患者ファイルページへ遷移（URLパターン設定に基づく）
        - ページ読み込み待機
        - ドロップゾーンへ画像を自動アップロード
    - **完了**: `POST /mark_processed` を呼び出してサーバーデータをクリア

## 技術スタック (Technology Stack)

### Part 1: Python Backend
- **フレームワーク**: FastAPI, Uvicorn
- **画像処理**: OpenCV (動体検知, キャプチャ)
- **AI**: Azure OpenAI (GPT-4o), `python-dotenv`
- **セキュリティ**: CORS (`Access-Control-Allow-Origin: *`)
- **エンドポイント**:
    - `GET /check_new_scan`: JSON `{ patient_id: "...", image_b64: "..." }` または `null` を返す
    - `POST /mark_processed`: 現在のデータをクリアする

### Part 2: Chrome Extension
- **マニフェスト**: V3
- **権限**: `activeTab`, `scripting`, `host_permissions`
- **設定 (`content_script.js`)**:
    ```javascript
    const KARTE_CONFIG = {
        targetUrlPattern: "https://example-karte.com/patients/{{id}}/files",
        dropZoneSelector: "div.file-upload-area",
        submitButtonSelector: "button#upload-confirm" // 任意
    };
    ```

## 実装フェーズ (Implementation Phases)
1.  **バックエンド実装**: FastAPIセットアップ, OpenCVロジック, Azure統合
2.  **拡張機能実装**: Manifest設定, ポーリングロジック, DOM操作（ドラッグ＆ドロップのエミュレーション）
3.  **統合テスト**: モック電子カルテページを使用したEnd-to-Endフローの検証
