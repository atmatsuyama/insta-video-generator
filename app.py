import streamlit as st
from google_auth_oauthlib.flow import Flow
from storage import upload_to_drive, add_material_to_sheet

# --- OAuth設定 ---
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["google_oauth"]["client_id"],
        "project_id": st.secrets["google_oauth"]["project_id"],
        "auth_uri": st.secrets["google_oauth"]["auth_uri"],
        "token_uri": st.secrets["google_oauth"]["token_uri"],
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": st.secrets["google_oauth"]["client_secret"],
        "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]]
    }
}

st.set_page_config(page_title="素材ポイポイくん", layout="centered")

# --- ログイン処理 ---
if 'creds' not in st.session_state:
    st.title("🚀 まずはログインしてね")
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=[
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/spreadsheets'
    ], redirect_uri=st.secrets["google_oauth"]["redirect_uri"])
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.link_button("Googleでログイン", auth_url)
    
    # URLのパラメータから認証コードを取得する処理（中略）
    # ※本番ではここにコードを受け取る処理が入ります
else:
    # ログイン後のメイン画面
    st.title("📸 素材ポイポイくん")
    # ...（これまでのアップロード画面）...
