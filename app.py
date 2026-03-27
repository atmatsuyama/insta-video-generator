import streamlit as st
import pandas as pd
from storage import add_material_to_sheet
from brain import generate_video_scenario
from editor import create_video

# 基本設定
st.set_page_config(page_title="インスタ動画生成", layout="centered")
st.title("📸 素材ポイポイくん")

# ユーザー識別
email = st.sidebar.text_input("あなたのGmail", placeholder="example@gmail.com")

if not email:
    st.info("左上のメニュー（＞マーク）からGmailを入力してください")
else:
    tab1, tab2 = st.tabs(["📤 素材を登録", "🎬 動画を作る"])

    with tab1:
        st.header("スマホから素材をアップ")
        # フォームにせず、直接配置することで「ボタンがない」を防ぎます
        uploaded_file = st.file_uploader("写真や動画を選択", type=["mp4", "mov", "jpg", "png"])
        asset_name = st.text_input("これになまえを付ける（必須）", placeholder="例：サクサクのパイ")
        asset_desc = st.text_area("ひとことメモ（任意）", placeholder="例：断面がきれいなやつ")

        # ここが「アップするボタン」です
        if st.button("✨ この素材をプールに保存"):
            if uploaded_file and asset_name:
                with st.spinner("保存中..."):
                    # ※現在は見た目だけ動かしています。次にGoogleドライブ保存を繋ぎます。
                    st.success(f"OK！「{asset_name}」をあなたの専用シートに記録しました！")
                    st.balloons()
            else:
                st.warning("「ファイル選択」と「なまえ」の両方が必要だよ！")

    with tab2:
        st.header("動画を生成")
        user_input = st.text_input("きょうの動画のテーマは？", placeholder="例：新発売をアピールしたい")
        
        if st.button("🤖 AIに構成をまかせる"):
            if user_input:
                st.info("AIがあなたのシートを見て構成を考えています...")
                # 以降、brain.pyを呼び出す処理（前回同様）
            else:
                st.error("テーマを入力してね")
