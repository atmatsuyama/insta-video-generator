import os
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips
import edge_tts
import asyncio

async def generate_voice(text, output_path):
    """高品質な音声を生成 (Microsoft Edge TTS使用)"""
    communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
    await communicate.save(output_path)

def process_material(file_path, duration=5):
    """素材を9:16の枠に収める（背景ぼかし等の処理）"""
    target_w, target_h = 720, 1280
    
    if file_path.endswith(('.jpg', '.png', '.jpeg')):
        clip = ImageClip(file_path).set_duration(duration)
    else:
        clip = VideoFileClip(file_path).subclip(0, min(duration, VideoFileClip(file_path).duration))
    
    # 9:16にリサイズ（アスペクト比維持）
    clip_w, clip_h = clip.size
    scale = min(target_w/clip_w, target_h/clip_h)
    new_w, new_h = int(clip_w * scale), int(clip_h * scale)
    resized_clip = clip.resize(newsize=(new_w, new_h))
    
    # 黒背景の中央に配置（パノラマや横長対策）
    final_clip = CompositeVideoClip([
        ColorClip(size=(target_w, target_h), color=(0,0,0)).set_duration(duration),
        resized_clip.set_position("center")
    ])
    
    return final_clip

def create_video(asset_files, script_text, output_filename="final_video.mp4"):
    """選ばれた素材と音声を合体させて動画を作る"""
    # 1. 音声生成
    voice_path = "temp_voice.mp3"
    asyncio.run(generate_voice(script_text, voice_path))
    audio = AudioFileClip(voice_path)
    
    # 2. 素材加工
    each_duration = audio.duration / len(asset_files)
    clips = [process_material(f, duration=each_duration) for f in asset_files]
    
    # 3. 結合
    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)
    
    # 4. 書き出し
    video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    return output_filename
