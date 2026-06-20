from moviepy.editor import VideoFileClip, concatenate_videoclips 
from pydub import AudioSegment  
from pydub.silence import detect_nonsilent  
import tempfile, os  
  
BUFFER_TIME = 0.05  
  
def _extract_audio_path(clip):  
    fd, temp_filename = tempfile.mkstemp(suffix='.wav')  
    os.close(fd)  
    clip.audio.write_audiofile(temp_filename, codec='pcm_s16le', verbose=False, logger=None)  
    return temp_filename  
  
  
def detect_speech_segments(input_file, silence_thresh=-50.0, min_silence_len=500):  
    clip = VideoFileClip(input_file)  
    try:  
        temp_filename = _extract_audio_path(clip)  
        try:  
            audio = AudioSegment.from_wav(temp_filename)  
        finally:  
            if os.path.exists(temp_filename):  
                os.remove(temp_filename)  
    finally:  
        clip.close()  
  
    nonsilent_ranges = detect_nonsilent(audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)  
  
    segments = [[round(start / 1000.0, 3), round(end / 1000.0, 3)] for start, end in nonsilent_ranges]  
    duration = round(len(audio) / 1000.0, 3)  
    return duration, segments  
  
def remove_silence_from_video(input_file, output_file, silence_thresh=-50.0, min_silence_len=500):  
    clip = VideoFileClip(input_file)  
    try:  
        temp_filename = _extract_audio_path(clip)  
        try:  
            audio = AudioSegment.from_wav(temp_filename)  
        finally:  
            if os.path.exists(temp_filename):  
                os.remove(temp_filename)  
  
        nonsilent_ranges = detect_nonsilent(audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)  
  
        nonsilent_times = [(max(0, start / 1000.0 - BUFFER_TIME), min(clip.duration, end / 1000.0 + BUFFER_TIME)) for start, end in nonsilent_ranges]  
  
        if not nonsilent_times:  
            raise ValueError('No non-silent segments detected in the input video.')  
  
        subclips = [clip.subclip(start, end) for start, end in nonsilent_times]  
        final_clip = concatenate_videoclips(subclips)  
        try:  
            final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', audio_bitrate='256k', verbose=False, logger=None)  
        finally:  
            final_clip.close()  
            for sub in subclips:  
                try:  
                    sub.close()  
                except Exception:  
                    pass  
    finally:  
        try:  
            clip.close()  
        except Exception:  
            pass  
