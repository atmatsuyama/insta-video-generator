import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

def get_gcp_service(creds_data):
    """ログインしたユーザーの権限でサービスを作成"""
    creds = Credentials.from_authorized_user_info(creds_data)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

def upload_to_drive(uploaded_file, folder_id, creds_data):
    drive_service, _ = get_gcp_service(creds_data)
    file_metadata = {'name': uploaded_file.name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), 
                              mimetype=uploaded_file.type, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    # OAuthなら自分のドライブなので、この共有設定は不要な場合が多いですが念のため
    drive_service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return file.get('webViewLink')

def add_material_to_sheet(sheet_id, name, url, desc, creds_data):
    _, sheets_service = get_gcp_service(creds_data)
    values = [[name, url, desc]]
    body = {'values': values}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range="A1",
        valueInputOption="USER_ENTERED", body=body).execute()
