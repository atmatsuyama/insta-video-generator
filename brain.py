import streamlit as st
import os
import asyncio
import json
# 🔴🔴 インポートエラー回避のため形式を変更
import google.genai as genai
from google.genai import types
import edge_tts
# 🔴🔴 moviepy.editor は 2.x系で廃止されたため改変
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

def main():
    st.set_page_config(page_title="Insta Video Gen", layout="wide")
    st.title("🎥 AI Video Generator")

    # Secretsの安全な取得
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
        oauth = st.secrets["google_oauth"]
    except KeyError as e:
        st.error(f"Secrets設定エラー: {e} が見つかりません。Streamlit CloudのSettings > Secrets を確認してください。")
        st.stop()

    # Geminiクライアント初期化
    client = genai.Client(api_key=API_KEY)

    # 0:09版シーケンス
    if 'init_done' not in st.session_state:
        if initialize_audio_sequence():
            st.session_state['init_done'] = True

    user_input = st.text_area("動画のテーマ:", "最新のガジェット紹介")

    if st.button("生成開始"):
        # 0:09版 録画開始シーケンス
        start_recording_sequence()
        
        with st.spinner("AIが処理中..."):
            # Gemini 3 Flash 呼び出し
            response = client.models.generate_content(
                model="gemini-3-flash",
                contents=f"Instagramリール用の台本を作ってください: {user_input}"
            )
            script = response.text
            st.success("台本完成")
            st.write(script)

            # 音声合成
            async def generate_voice(text):
                communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
                await communicate.save("output.mp3")
            
            asyncio.run(generate_voice(script))
            st.audio("output.mp3")
            st.info("オーディオ同期中... (0:09仕様)")

if __name__ == "__main__":
    main()
