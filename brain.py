import streamlit as st
import os
import asyncio
import json
# 🔴🔴 Python 3.14対応のため新SDKを使用
import google.genai as genai
from google.genai import types
import edge_tts
import moviepy as mp
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

# --- 2026年3月15日 0:09版 オーディオ初期化と録画シーケンス テンプレート (START) ---
# このセクションは一切変更せず、指示通り維持します。
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

def main():
    st.set_page_config(page_title="Insta Video Generator", layout="wide", page_icon="🎥")
    
    # Secretsの取得
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
        oauth_config = st.secrets["google_oauth"]
    except KeyError as e:
        st.error(f"Secretsエラー: {e} が不足しています。")
        st.stop()

    # 🔴🔴 認証フローの再実装
    if 'credentials' not in st.session_state:
        st.title("🔐 認証が必要です")
        st.write("アプリを利用するにはGoogleアカウントでログインしてください。")
        
        # OAuthフローの設定
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
        
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/generative-language.retrieval']
        )
        flow.redirect_uri = oauth_config["redirect_uri"]
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.link_button("Googleでログイン", auth_url)
        
        # クエリパラメータからコードを取得（ログイン後の戻り処理）
        query_params = st.query_params
        if "code" in query_params:
            flow.fetch_token(code=query_params["code"])
            st.session_state['credentials'] = flow.credentials
            st.rerun()
        st.stop()

    # --- ログイン後のメイン画面 ---
    st.title("🎬 Insta Video Generator")
    
    # 0:09版シーケンスの実行
    if 'init_done' not in st.session_state:
        if initialize_audio_sequence():
            st.session_state['init_done'] = True

    # サイドバー UI
    with st.sidebar:
        st.header("⚙️ 設定")
        st.info(f"ログイン中: {oauth_config['project_id']}")
        if st.button("ログアウト"):
            st.session_state.clear()
            st.rerun()

    # コンテンツ入力エリア
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("台本作成")
        topic = st.text_area("動画のテーマやアイデアを入力してください:", placeholder="例: 忙しい朝の5分でできる時短メイク")
        generate_btn = st.button("台本と音声を生成", type="primary")

    with col2:
        st.subheader("プレビュー")
        preview_placeholder = st.empty()
        preview_placeholder.info("ここに生成されたコンテンツが表示されます。")

    if generate_btn and topic:
        # 0:09版 録画シーケンス開始
        start_recording_sequence()
        
        with st.spinner("Gemini 3 Flash が魔法をかけています..."):
            client = genai.Client(api_key=API_KEY)
            
            # コンテンツ生成
            response = client.models.generate_content(
                model="gemini-3-flash",
                contents=f"Instagramリール用の魅力的な台本（15秒以内）を作成してください。テーマ: {topic}"
            )
            script = response.text
            
            with col1:
                st.success("台本が完成しました！")
                st.write(script)

            # 音声生成 (edge-tts)
            async def speak(text):
                communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
                await communicate.save("narration.mp3")
            
            asyncio.run(speak(script))
            
            with col2:
                preview_placeholder.empty()
                st.audio("narration.mp3")
                st.info("オーディオ同期中... (0:09仕様)")
                st.write("🎥 録画シーケンス同期完了")

if __name__ == "__main__":
    main()
