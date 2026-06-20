# Silence Remover Video Editor 
  
  
A simple web app that removes silent sections from videos using MoviePy and pydub.  
  
## Quick Start  
  
1. Make sure you have Python 3.10+ and Node.js 18+ installed.  
2. Install ffmpeg and add it to your PATH.  
3. Double-click start.bat. It will:  
  
   - Create a virtual environment  
   - Install backend Python dependencies  
   - Install frontend npm dependencies  
   - Start the backend at http://localhost:8000  
   - Start the frontend at http://localhost:5173  
  
4. Open http://localhost:5173 in your browser.  
  
## Manual Setup  
  
### Backend  
  
```  
python -m venv venv  
venv\Scripts\activate  
pip install -r requirements.txt  
cd backend  
python main.py  
```  
  
  
### Frontend  
  
```  
cd frontend  
npm install  
npm run dev  
```  
  
## Project Structure  
  
backend/  
  main.py        - FastAPI server and API endpoints  
  processor.py   - MoviePy + pydub silence detection and removal  
  uploads/       - uploaded videos  
  outputs/       - processed videos  
  
frontend/  
  src/App.jsx    - main React component  
  src/main.jsx   - React entry point  
  src/index.css  - Tailwind CSS  
  index.html     - HTML shell  
  
start.bat       - one-click setup and start  
requirements.txt - Python dependencies  
README.md       - this file  
  
  
## API Endpoints  
  
- POST /upload - upload a video, returns video_id  
- GET  /original/VIDEO_ID - stream the original video  
- POST /analyze/VIDEO_ID - detect speech segments, returns duration and segments  
- POST /process/VIDEO_ID - remove silence, returns output URL  
- GET  /download/VIDEO_ID - download processed video  
  
## How It Works  
  
The same algorithm from your original script:  
  
1. Upload a video file (mp4, mov, avi, mkv).  
2. Backend extracts the audio using MoviePy.  
3. pydub.detect_nonsilent finds the speech regions.  
4. A 50ms buffer is added around each cut to smooth transitions.  
5. MoviePy concatenates the non-silent video segments.  
6. The final video is encoded with libx264 + aac audio.  
  
## Configuration  
  
In backend/processor.py you can adjust:  
  
- silence_thresh (default -50.0 dB) - lower = stricter silence detection  
- min_silence_len (default 500 ms) - shorter segments are kept as speech  
- BUFFER_TIME (default 0.05 s) - smoothing around cuts  
