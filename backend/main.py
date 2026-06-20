import os  
import uuid  
from pathlib import Path  
  
from fastapi import FastAPI, File, HTTPException, UploadFile, Request  
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import FileResponse, JSONResponse  
  
from processor import detect_speech_segments, remove_silence_from_video  
  
BASE_DIR = Path(__file__).resolve().parent  
UPLOAD_DIR = BASE_DIR / 'uploads'  
OUTPUT_DIR = BASE_DIR / 'outputs'  
UPLOAD_DIR.mkdir(exist_ok=True)  
OUTPUT_DIR.mkdir(exist_ok=True)  
  
ALLOWED_EXT = {'.mp4', '.mov', '.avi', '.mkv'}  
CHUNK_SIZE = 1024 * 1024   
  
app = FastAPI(title='Silence Remover API')  
  
app.add_middleware(  
    CORSMiddleware,  
    allow_origins=['*'],  
    allow_credentials=True,  
    allow_methods=['*'],  
    allow_headers=['*'],  
)  
  
def _ext(name: str) -> str:  
    return os.path.splitext(name)[1].lower()  
  
@app.exception_handler(Exception)  
async def global_exception_handler(request: Request, exc: Exception):  
    return JSONResponse(status_code=500, content={"detail": str(exc)})  
  
@app.get('/')  
def root():  
    return {'status': 'ok', 'message': 'Silence Remover API'}  
  
@app.post('/upload')  
async def upload_video(file: UploadFile = File(...)):  
    if _ext(file.filename or '') not in ALLOWED_EXT:  
        raise HTTPException(status_code=400, detail='Unsupported file type. Use mp4, mov, avi, mkv.')  
  
    video_id = uuid.uuid4().hex[:12]  
    ext = _ext(file.filename or '.mp4')  
    dest = UPLOAD_DIR / f'{video_id}{ext}'  
  
    try:  
        with open(dest, 'wb') as out:  
            while True:  
                chunk = await file.read(CHUNK_SIZE)  
                if not chunk:  
                    break  
                out.write(chunk)  
    except Exception as e:  
        if dest.exists():  
            try: dest.unlink()  
            except Exception: pass  
        raise HTTPException(status_code=500, detail=f'Upload failed: {e}')  
  
    return {'video_id': video_id, 'filename': dest.name, 'size': dest.stat().st_size}  
  
def _find_upload(video_id: str) -> Path:  
    for ext in ALLOWED_EXT:  
        candidate = UPLOAD_DIR / f'{video_id}{ext}'  
        if candidate.exists():  
            return candidate  
    raise HTTPException(status_code=404, detail='Video not found.')  
  
@app.get('/original/{video_id}')  
def get_original(video_id: str):  
    path = _find_upload(video_id)  
    return FileResponse(path)  
  
@app.post('/analyze/{video_id}')  
def analyze_video(video_id: str):  
    path = _find_upload(video_id)  
    try:  
        duration, segments = detect_speech_segments(str(path))  
    except Exception as e:  
        raise HTTPException(status_code=500, detail=f'Analysis failed: {e}')  
    return {'video_id': video_id, 'duration': duration, 'segments': segments}  
  
@app.post('/process/{video_id}')  
def process_video(video_id: str):  
    path = _find_upload(video_id)  
    output_path = OUTPUT_DIR / f'{video_id}.mp4'  
    if output_path.exists():  
        output_path.unlink()  
    try:  
        remove_silence_from_video(str(path), str(output_path))  
    except ValueError as e:  
        raise HTTPException(status_code=400, detail=str(e))  
    except Exception as e:  
        raise HTTPException(status_code=500, detail=f'Processing failed: {e}')  
    if not output_path.exists():  
        raise HTTPException(status_code=500, detail='Processing failed: output file not produced.')  
    return {'status': 'completed', 'video_id': video_id, 'output_url': f'/download/{video_id}'}  
  
@app.get('/download/{video_id}')  
def download_video(video_id: str):  
    output_path = OUTPUT_DIR / f'{video_id}.mp4'  
    if not output_path.exists():  
        raise HTTPException(status_code=404, detail='Processed video not found. Run /process first.')  
    return FileResponse(path=output_path, filename=f'silence_removed_{video_id}.mp4', media_type='video/mp4')  
  
if __name__ == '__main__':  
    import uvicorn  
    uvicorn.run(  
        app,  
        host='0.0.0.0',  
        port=8000,  
        timeout_keep_alive=300,  
        h11_max_incomplete_event_size=1024 * 1024,  
    )  
