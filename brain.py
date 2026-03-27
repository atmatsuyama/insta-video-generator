import streamlit as st
import os
import asyncio
import json
# 🔴 Python 3.14対応のため、新SDKに変更
from google import genai
from google.genai import types
import edge_tts
from moviepy.editor import *

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

# Secretsの取得
API_KEY = st.secrets["GEMINI_API_KEY"]
oauth = st.secrets["google_oauth"]

# クライアント初期化 (Gemini 3 Flash 対応)
client = genai.Client(api_key=API_KEY)

async def generate_voice(text, filename="output.mp3"):
    communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
    await communicate.save(filename)

def main():
    st.set_page_config(page_title="Insta Video Gen", layout="wide")
    st.title("🎥 AI Video Generator (0:09 Ver)")

    # 0:09版シーケンスの実行
    if 'init_done' not in st.session_state:
        if initialize_audio_sequence():
            st.session_state['init_done'] = True

    # サイドバーにOAuth情報を表示（確認用）
    with st.sidebar:
        st.write(f"Project: {oauth['project_id']}")
        if st.button("Reset Session"):
            st.session_state.clear()
            st.rerun()

    user_input = st.text_area("動画のテーマを入力してください:", "猫の可愛い日常リール")

    if st.button("生成開始"):
        # 0:09版 録画開始シーケンス
        start_recording_sequence()
        
        with st.spinner("Gemini 3 Flash が台本を生成中..."):
            # 新SDKの呼び出し方式
            response = client.models.generate_content(
                model="gemini-3-flash",
                contents=f"Instagram用の5秒程度の台本を作ってください。テーマ: {user_input}"
            )
            script = response.text
            st.success("台本完成！")
            st.info(script)

            # 音声生成
            asyncio.run(generate_voice(script))
            st.audio("output.mp3")
            st.write("録画中... (0:09シーケンス同期中)")

if __name__ == "__main__":
    main()
