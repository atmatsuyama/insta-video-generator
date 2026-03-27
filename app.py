import streamlit as st
import pandas as pd
from storage import add_material_to_sheet
from brain import generate_video_scenario
from editor import create_video

# 1. 基本設定
st.set_page_config(page_title="インスタ動画自動生成", layout="centered")
st.title("🎥 素材ストック動画生成")

# 2. ユーザー識別（Gmailアドレス）
email = st.sidebar.text_input("Gmailアドレスを入力", placeholder="example@gmail.com")

if not email:
    st.info("左側のメニューにGmailアドレスを入力して始めてください。")
else:
    # ユーザー専用のスプレッドシートID（あなたが提示したものをデフォルトに設定）
    # ※本来はemailに応じて切り替えるロジックを入れる場所
    SHEET_ID = "142zeB7ZX7gKF8HYNROreaJ0BuSriAUOqvft7YlzY8nI"
    
    tab1, tab2 = st.tabs(["📤 素材をアップロード", "🎬 動画を作る"])

    # --- TAB 1: 素材アップロード ---
    with tab1:
        st.header("新しい素材をプールする")
        with st.form("upload_form"):
            name = st.text_input("素材名（必須）", placeholder="例：りんこパイ（新作）")
            url = st.text_input("Googleドライブの共有URL（必須）")
            desc = st.text_area("説明（任意）")
            
            if st.form_submit_button("素材リストに追加"):
                if name and url:
                    # 本来はここでGoogle APIの認証が必要ですが、
                    # まずはスプレッドシートに追記する関数を呼び出す準備
                    st.success(f"「{name}」をリストに登録しました！（※API設定後に反映されます）")
                else:
                    st.error("素材名とURLは必ず入力してください。")

    # --- TAB 2: 動画生成 ---
    with tab2:
        st.header("今日の動画を生成")
        user_input = st.text_input("きょう言いたいこと", placeholder="例：新作パイのサクサク感を伝えたい")
        
        if st.button("AIに構成を任せる"):
            if user_input:
                # 1. スプレッドシート読み込み
                sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
                df = pd.read_csv(sheet_url)
                
                # 2. Geminiでシナリオ生成
                api_key = st.secrets["GEMINI_API_KEY"]
                with st.spinner("AIが素材を選んで台本を書いています..."):
                    plan = generate_video_scenario(api_key, user_input, df)
                
                st.subheader("AIからの提案")
                st.write(f"**選んだ素材:** {', '.join(plan['selected'])}")
                
                # 3. 台本編集
                edited_script = st.text_area("ナレーション原稿（修正可）", value=plan['script'])
                
                if st.button("この内容で動画を書き出す"):
                    with st.spinner("動画を生成中...（約1分かかります）"):
                        # 本来はここでeditor.pyを回す
                        # output_file = create_video(selected_files, edited_script)
                        st.video("https://www.w3schools.com/html/mov_bbb.mp4") # デモ用
                        st.success("動画が完成しました！")
            else:
                st.error("「きょう言いたいこと」を入力してください。")
