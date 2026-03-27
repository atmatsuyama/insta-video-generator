import streamlit as st
import os
import asyncio
import json
from google import genai
from google.genai import types
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
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

# Google API 連携用の設定
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

def upload_to_drive(creds, file_path, folder_id=None):
    """Googleドライブにファイルをアップロード"""
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file.get('webViewLink')

def record_to_sheet(creds, spreadsheet_id, data_row):
    """スプレッドシートにデータを記録"""
    service = build('sheets', 'v4', credentials=creds)
    body = {'values': [data_row]}
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

def main():
    st.set_page_config(page_title="Insta Video Generator", layout="wide")
    
    try:
        oauth_config = st.secrets["google_oauth"]
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except KeyError as e:
        st.error(f"Secrets設定が不完全です: {e}")
        st.stop()

    # 認証フロー
    if 'credentials' not in st.session_state:
        client_config = {
            "web": {
                "client_id": oauth_config["client_id"],
                "project_id": oauth_config["project_id"],
                "auth_uri": oauth_config["auth_uri"],
                "token_uri": oauth_config["token_uri"],
                "client_secret": oauth_config["client_secret"],
                "redirect_uris": [oauth_config["redirect_uri"]]
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = oauth_config["redirect_uri"]
        
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        st.title("🎥 アプリ認証")
        st.link_button("Googleアカウントで認証", auth_url)
        
        if "code" in st.query_params:
            flow.fetch_token(code=st.query_params["code"])
            st.session_state['credentials'] = flow.credentials
            st.rerun()
        st.stop()

    # メインUI
    st.title("🎬 素材・動画管理 Generator")
    creds = st.session_state['credentials']

    # 0:09版シーケンス
    if 'init_done' not in st.session_state:
        if initialize_audio_sequence():
            st.session_state['init_done'] = True

    with st.sidebar:
        st.header("⚙️ 設定情報")
        sheet_id = st.text_input("記録先スプレッドシートID", placeholder="シートのURLにある長い文字列")
        if st.button("ログアウト"):
            st.session_state.clear()
            st.rerun()

    topic = st.text_area("生成する動画のテーマ:")
    
    if st.button("生成 & ドライブ保存", type="primary"):
        start_recording_sequence()
        
        with st.spinner("AI生成とドライブ同期を実行中..."):
            # 1. Geminiで台本生成
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(model="gemini-3-flash", contents=topic)
            script = response.text
            
            # 2. 音声生成
            output_audio = "narration.mp3"
            async def generate_voice():
                communicate = edge_tts.Communicate(script, "ja-JP-NanamiNeural")
                await communicate.save(output_audio)
            asyncio.run(generate_voice())
            
            # 3. ドライブにアップロード
            drive_link = upload_to_drive(creds, output_audio)
            
            # 4. シートに記録
            if sheet_id:
                record_to_sheet(creds, sheet_id, [topic, script, drive_link])
                st.success(f"ドライブに保存し、シートに記録しました: {drive_link}")
            else:
                st.warning("スプレッドシートIDが未設定のため、ログ記録をスキップしました。")
            
            st.audio(output_audio)
            st.write(script)

if __name__ == "__main__":
    main()
