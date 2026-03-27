import pandas as pd
import re
import json
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_gcp_service():
    """Secretsに貼ったJSONから認証情報を作成"""
    info = json.loads(st.secrets["GCP_JSON"])
    creds = service_account.Credentials.from_service_account_info(info)
    # ドライブ用とシート用のサービスを両方作る
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

def upload_to_drive(file, folder_id, filename):
    """Googleドライブの指定フォルダにファイルを保存"""
    drive_service, _ = get_gcp_service()
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaFileUpload(file, resumable=True)
    f = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webContentLink').execute()
    # 誰でも見れるように共有設定（これが必要）
    drive_service.permissions().create(fileId=f.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return f.get('webContentLink')

def add_material_to_sheet(sheet_id, name, url, desc):
    """シートに追記"""
    _, sheets_service = get_gcp_service()
    values = [[name, url, desc]]
    body = {'values': values}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range="A1",
        valueInputOption="USER_ENTERED", body=body).execute()
