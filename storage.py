import pandas as pd
import re
from googleapiclient.discovery import build

def get_direct_url(url):
    """Googleドライブの共有URLを直通リンクに変換"""
    if 'drive.google.com' in str(url):
        match = re.search(r'd/([^/]+)', url)
        if match:
            return f'https://drive.google.com/uc?export=download&id={match.group(1)}'
    return url

def add_material_to_sheet(service, sheet_id, name, url, desc):
    """スプレッドシートの末尾にデータを1行追加"""
    direct_url = get_direct_url(url)
    values = [[name, direct_url, desc]]
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range="A1",
        valueInputOption="USER_ENTERED", body=body).execute()
