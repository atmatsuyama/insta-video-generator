import pandas as pd
import json
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

def get_gcp_service():
    """SecretsのGCP_JSONから認証情報を作成"""
    # '''で囲んで貼ったので、文字列として読み込んでJSONに戻す
    info = json.loads(st.secrets["GCP_JSON"])
    creds = service_account.Credentials.from_service_account_info(info)
    
    # ドライブとシートのサービスを起動
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

def upload_to_drive(uploaded_file, folder_id):
    """ファイルをドライブに保存して、直通URLを返す"""
    drive_service, _ = get_gcp_service()
    
    file_metadata = {
        'name': uploaded_file.name,
        'parents': [folder_id]
    }
    
    # Streamlitのアップローダーからバイナリデータを読み込む
    media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), 
                              mimetype=uploaded_file.type, 
                              resumable=True)
    
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id, webViewLink').execute()
    
    # 誰でも閲覧できるように権限を変更（動画生成に必要）
    drive_service.permissions().create(fileId=file.get('id'), 
                                        body={'type': 'anyone', 'role': 'reader'}).execute()
    
    return file.get('webViewLink')

def add_material_to_sheet(sheet_id, name, url, desc):
    """スプレッドシートの末尾に1行追加"""
    _, sheets_service = get_gcp_service()
    values = [[name, url, desc]]
    body = {'values': values}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range="A1",
        valueInputOption="USER_ENTERED", body=body).execute()
