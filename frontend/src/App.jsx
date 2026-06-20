import { useState, useRef } from 'react'  
import axios from 'axios'  
  
const API = ''

const AUDIO_EXTS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']

function isAudioFile(filename) {
  const ext = '.' + filename.split('.').pop().toLowerCase()
  return AUDIO_EXTS.includes(ext)
}  
  
function formatTime(s) {  
  const m = Math.floor(s / 60)  
  const sec = (s % 60).toFixed(1)  
  return m + ':' + String(sec).padStart(4, '0')  
}  
  
function Timeline({ duration, segments }) {  
  if (!duration) return null  
  const width = 60  
  const bars = []  
  for (let i = 0; i < width; i++) {  
    const t = (i / width) * duration  
    const kept = segments.some(([s, e]) => t >= s && t <= e)  
    bars.push(kept ? '█' : '░')  
  }  
  return (  
    <div className="my-4">  
      <pre className="text-2xl font-mono tracking-wider text-emerald-400">{bars.join('')}</pre>  
      <div className="flex gap-4 text-sm text-slate-400 mt-2">  
        <span>█ Kept</span>  
        <span>░ Removed</span>  
      </div>  
    </div>  
  )  
}  
  
export default function App() {
  const [file, setFile] = useState(null)
  const [videoId, setVideoId] = useState(null)
  const [originalUrl, setOriginalUrl] = useState(null)
  const [outputUrl, setOutputUrl] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)
  const [isAudio, setIsAudio] = useState(false)
  const originalRef = useRef(null)
  const outputRef = useRef(null)
  
  const onUpload = async (e) => {
    const f = e.target.files[0]
    if (!f) return
    setFile(f)
    setIsAudio(isAudioFile(f.name))
    setOutputUrl(null)
    setAnalysis(null)
    setError(null)
    setStatus('uploading')
    const fd = new FormData()
    fd.append('file', f)
    try {
      const r = await axios.post(API + '/upload', fd)
      setVideoId(r.data.video_id)
      setOriginalUrl(API + '/original/' + r.data.video_id)
      setStatus('uploaded')
    } catch (err) {
      setError(err.response && err.response.data ? err.response.data.detail : err.message)
      setStatus('idle')
    }
  }
  
  const onAnalyze = async () => {  
    if (!videoId) return  
    setStatus('analyzing')  
    setError(null)  
    try {  
      const r = await axios.post(API + '/analyze/' + videoId)  
      setAnalysis(r.data)  
      setStatus('analyzed')  
    } catch (err) {  
      setError(err.response && err.response.data ? err.response.data.detail : err.message)  
      setStatus('uploaded')  
    }  
  }  
  
  const onProcess = async () => {  
    if (!videoId) return  
    setStatus('processing')  
    setError(null)  
    try {  
      const r = await axios.post(API + '/process/' + videoId)  
      setOutputUrl(API + r.data.output_url)  
      setStatus('done')  
    } catch (err) {  
      setError(err.response && err.response.data ? err.response.data.detail : err.message)  
      setStatus('analyzed')  
    }  
  }  
  
  return (  
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6">  
      <div className="max-w-5xl mx-auto">  
        <h1 className="text-3xl font-bold mb-6">Silence Remover</h1>  
  
        {error && (<div className="bg-red-900 border border-red-700 p-3 rounded mb-4">{error}</div>)}  
  
        <div className="mb-6">
          <label className="block mb-2 text-sm font-medium">Choose a video or audio file</label>
          <p className="text-xs text-slate-400 mb-2">Video: mp4, mov, avi, mkv | Audio: mp3, wav, flac, aac, ogg, wma, m4a, opus</p>
          <input type="file" accept="video/*,audio/*" onChange={onUpload} className="block w-full text-sm file:mr-3 file:py-2 file:px-4 file:rounded file:border-0 file:bg-slate-700 file:text-slate-100" />
        </div>  
  
        {originalUrl && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Original</h2>
            {isAudio ? (
              <audio ref={originalRef} src={originalUrl} controls className="w-full" />
            ) : (
              <video ref={originalRef} src={originalUrl} controls className="w-full rounded bg-black" />
            )}
            <div className="mt-3 flex gap-3">
              <button onClick={onAnalyze} disabled={!videoId} className="px-4 py-2 rounded bg-sky-600">{isAudio ? 'Analyze Audio' : 'Analyze Video'}</button>
              <button onClick={onProcess} disabled={!analysis} className="px-4 py-2 rounded bg-emerald-600">Remove Silence</button>
            </div>
          </div>
        )}  
  
        {analysis && (  
          <div className="mb-6 p-4 bg-slate-800 rounded">  
            <h2 className="text-xl font-semibold mb-2">Detected Speech Segments</h2>  
            <p className="text-slate-300 mb-2">Original duration: {formatTime(analysis.duration)}</p>  
            <p className="text-slate-300 mb-3">Kept segments: {analysis.segments.length}</p>  
            <Timeline duration={analysis.duration} segments={analysis.segments} />  
            <div className="text-sm text-slate-400 max-h-40 overflow-y-auto">  
              {analysis.segments.map((seg, i) => (  
                <div key={i} className="font-mono">  
                  Segment {i + 1}: {formatTime(seg[0])} - {formatTime(seg[1])}  
                </div>  
              ))}  
            </div>  
          </div>  
        )}  
  
        {outputUrl && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Processed (silence removed)</h2>
            {isAudio ? (
              <audio ref={outputRef} src={outputUrl} controls className="w-full" />
            ) : (
              <video ref={outputRef} src={outputUrl} controls className="w-full rounded bg-black" />
            )}
            <a href={outputUrl} download className="inline-block mt-3 px-4 py-2 rounded bg-amber-600 hover:bg-amber-500">Download Output</a>
          </div>
        )}  
  
        {status === 'processing' && <p className="text-amber-400">Processing... this may take a while.</p>}  
        {status === 'analyzing' && <p className="text-sky-400">Analyzing...</p>}  
      </div>  
    </div>  
  )  
}  
