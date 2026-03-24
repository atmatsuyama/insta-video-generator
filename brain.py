import google.generativeai as genai
import json

def generate_video_scenario(api_key, user_input, df):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 素材リストを整形
    asset_list = ""
    for _, row in df.iterrows():
        asset_list += f"- 素材名: {row['素材名']} (説明: {row.get('説明', '')})\n"

    prompt = f"""
あなたは動画ディレクターです。以下の素材リストから3〜5つを選び、30秒の動画構成を作ってください。
【素材リスト】
{asset_list}
【ユーザーの今日の要望】
{user_input}
【ルール】
1. 素材名は人間が決めた「正解」です。1文字も変えずに出力してください。
2. 出力は以下のJSON形式のみ。
{{ "selected": ["素材名1", "素材名2"], "script": "ナレーション原稿" }}
"""
    response = model.generate_content(prompt)
    return json.loads(response.text.strip('`json\n '))
