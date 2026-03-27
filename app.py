import streamlit as st
from storage import upload_to_drive, add_material_to_sheet

st.set_page_config(page_title="素材ポイポイくん", layout="centered")
st.title("📸 素材ポイポイくん")

# 設定情報（これらはAさん・Bさんごとに本来は入力してもらうもの）
# テスト用にあなたのIDをここに入れておくと楽です
SHEET_ID = st.sidebar.text_input("スプレッドシートID")
FOLDER_ID = st.sidebar.text_input("保存先フォルダID")

tab1, tab2 = st.tabs(["📤 素材を登録", "🎬 動画を作る"])

with tab1:
    uploaded_file = st.file_uploader("写真や動画を選択", type=["mp4", "mov", "jpg", "png"])
    asset_name = st.text_input("素材のなまえ")
    asset_desc = st.text_area("メモ")

    if st.button("✨ この素材をプールに保存"):
        if uploaded_file and asset_name and SHEET_ID and FOLDER_ID:
            with st.spinner("Googleドライブへ転送中..."):
                try:
                    # 1. ドライブにアップロード
                    file_url = upload_to_drive(uploaded_file, FOLDER_ID)
                    # 2. シートに追記
                    add_material_to_sheet(SHEET_ID, asset_name, file_url, asset_desc)
                    st.success(f"成功！「{asset_name}」を保存しました！")
                    st.balloons()
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("ファイル、なまえ、各IDをすべて入力してください。")
