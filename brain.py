import streamlit as st
import os
import asyncio
import json
# 🔴🔴 廃止された旧ライブラリがPython 3.14でクラッシュするため、新ライブラリへ改変しました
from google import genai
from google.genai import types
import edge_tts
from moviepy.editor import *

# --- 2026年3月15日 0:09版 オーディオ初期化と録画シーケンス テンプレート (START) ---
# このセクションは指示通り1文字も変更・削除せず維持します
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

# Secretsの読み込み
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
oauth_config = st.secrets["google_oauth"]

# クライアントの初期化
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_narration(text, output_file="narration.mp3"):
    async def _speak():
        communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
        await communicate.save(output_file)
    asyncio.run(_speak())

def main():
    st.set_page_config(page_title="Insta Video Generator", layout="wide")
    st.title("🎥 Insta Video Generator")

    # テンプレートの実行
    if not st.session_state.get('initialized'):
        if initialize_audio_sequence():
            st.session_state['initialized'] = True

    with st.sidebar:
        st.header("Settings")
        st.write(f"Project ID: {oauth_config['project_id']}")
        
    prompt = st.text_area("動画の台本やアイデアを入力してください:", placeholder="例: 週末に行きたいカフェ3選")

    if st.button("動画を生成"):
        if prompt:
            with st.spinner("AIがコンテンツを構成中..."):
                # シーケンス開始
                start_recording_sequence()
                
                # Gemini 3 Flash を使用した構成生成
                response = client.models.generate_content(
                    model="gemini-3-flash",
                    contents=f"以下のテーマでInstagramリール用の短い台本を作成してください: {prompt}"
                )
                script = response.text
                st.subheader("生成された台本")
                st.write(script)

                # 音声生成
                generate_narration(script)
                st.audio("narration.mp3")
                
                st.success("音声の生成が完了しました。")
        else:
            st.warning("プロンプトを入力してください。")

if __name__ == "__main__":
    main()
