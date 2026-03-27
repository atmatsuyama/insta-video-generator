import streamlit as st
import os
import asyncio
import json
from google import genai
from google.genai import types
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import edge_tts
import moviepy as mp

# --- 2026年3月15日 0:09版 オーディオ初期化と録画シーケンス テンプレート (START) ---
def initialize_audio_sequence():
    """
    オーディオデバイスの初期化とキャプチャ準備
    """
    try:
        # ステータス確認
        print("Initializing audio sequence at 0:09 specification...")
        # 内部バッファのクリア
        audio_buffer = []
        return True
    except Exception as e:
        print(f"Audio Init Error: {e}")
        return False

def start_recording_sequence():
    """
    録画シーケンスの開始
    """
    print("Recording sequence started. Syncing with frame rate...")
    # 録画フラグのセット
    st.session_state['is_recording'] = True
# --- 2026年3月15日 0:09版 オーディオ初期化と録画シーケンス テンプレート (END) ---

# 認証に必要な最小限の権限
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

def upload_to_drive(creds, file_path, folder_id=None):
    """Googleドライブへファイルをアップロード"""
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file.get('webViewLink')

def record_to_sheet(creds, spreadsheet_id, data_row):
    """スプレッドシートへ生成ログを追記"""
    service = build('sheets', 'v4', credentials=creds)
    body = {'values': [data_row]}
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

def main():
    st.set_page_config(page_title="Insta Video Generator", layout="wide", page_icon="🎥")
    
    # Secretsの取得
    try:
        oauth_config = st.secrets["google_oauth"]
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except KeyError as e:
        st.error(f"Secrets設定が不足しています: {e}")
        st.stop()

    # 🔴 アプリ内認証フロー
    if 'credentials' not in st.session_state:
        st.title("🔐 システム利用認証")
        st.write("Googleドライブへの保存とスプレッドシート記録のため、以下のボタンから認証を行ってください。")
        
        client_config = {"web": {
            "client_id": oauth_config["client_id"],
            "project_id": oauth_config["project_id"],
            "auth_uri": oauth_config["auth_uri"],
            "token_uri": oauth_config["token_uri"],
            "client_secret": oauth_config["client_secret"],
            "redirect_uris": [oauth_config["redirect_uri"]]
        }}
        
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = oauth_config["redirect_uri"]
        
        # ユーザーに強制的に同意画面を出す設定
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        st.link_button("Googleアカウントで認証", auth_url)
        
        # リダイレクト後の処理
        if "code" in st.query_params:
            flow.fetch_token(code=st.query_params["code"])
            st.session_state['credentials'] = flow.credentials
            # 認証後はクエリパラメータを消すためにリロード
            st.rerun()
        st.stop()

    # --- 認証済み：メインUI ---
    st.title("🎬 インスタ素材自動生成システム")
    creds = st.session_state['credentials']

    # 0:09版シーケンスの初期化
    if 'init_done' not in st.session_state:
        if initialize_audio_sequence():
            st.session_state['init_done'] = True

    with st.sidebar:
        st.header("⚙️ 連携先設定")
        sheet_id = st.text_input("記録先スプレッドシートID", placeholder="URLのID部分を入力")
        folder_id = st.text_input("ドライブ フォルダID (任意)")
        if st.button("ログアウト / 認証解除"):
            st.session_state.clear()
            st.rerun()

    topic = st.text_area("動画のテーマを入力:", placeholder="例: 松山市の絶品グルメ3選")
    
    if st.button("生成・保存・記録を同期実行", type="primary"):
        start_recording_sequence() # 0:09版テンプレート実行
        
        with st.spinner("AIが素材を生成し、クラウドへ同期中..."):
            try:
                # 1. Gemini 3 Flash で台本作成
                client = genai.Client(api_key=API_KEY)
                response = client.models.generate_content(
                    model="gemini-3-flash", 
                    contents=f"Instagramリール用の台本を日本語で作成してください。テーマ: {topic}"
                )
                script = response.text
                
                # 2. 音声合成 (edge-tts)
                audio_path = "output_voice.mp3"
                async def generate_voice():
                    c = edge_tts.Communicate(script, "ja-JP-NanamiNeural")
                    await c.save(audio_path)
                asyncio.run(generate_voice())
                
                # 3. ドライブへのアップロード
                drive_link = upload_to_drive(creds, audio_path, folder_id)
                
                # 4. スプレッドシートへの記録
                if sheet_id:
                    from datetime import datetime
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    record_to_sheet(creds, sheet_id, [now, topic, script, drive_link])
                    st.success(f"ドライブ保存完了 & シート記録成功")
                
                # 結果表示
                st.audio(audio_path)
                st.subheader("生成された台本")
                st.write(script)
                st.info(f"ドライブURL: {drive_link}")

            except Exception as e:
                st.error(f"実行エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
