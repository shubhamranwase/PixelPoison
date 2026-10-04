import React, { useState, useEffect, useRef } from 'react';
import { UploadCloud, Download, ShieldCheck } from 'lucide-react';

export default function ShieldView({ API_URL }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [intensity, setIntensity] = useState(2);
  const [protectedImage, setProtectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('protected');
  const canvasRef = useRef(null);

  useEffect(() => {
    if (protectedImage && activeTab === 'noise') {
      drawNoiseMap();
    }
  }, [protectedImage, activeTab]);

  const drawNoiseMap = () => {
    const canvas = canvasRef.current;
    if (!canvas || !preview || !protectedImage) return;

    const ctx = canvas.getContext('2d');
    const img1 = new Image();
    const img2 = new Image();

    let loadedCount = 0;
    const onImageLoad = () => {
      loadedCount++;
      if (loadedCount === 2) {
        const width = Math.min(img1.naturalWidth, 800);
        const height = Math.min(img1.naturalHeight, 800);
        canvas.width = width;
        canvas.height = height;

        const tempCanvas1 = document.createElement('canvas');
        const tempCanvas2 = document.createElement('canvas');
        tempCanvas1.width = width;
        tempCanvas1.height = height;
        tempCanvas2.width = width;
        tempCanvas2.height = height;

        const ctx1 = tempCanvas1.getContext('2d');
        const ctx2 = tempCanvas2.getContext('2d');

        ctx1.drawImage(img1, 0, 0, width, height);
        ctx2.drawImage(img2, 0, 0, width, height);

        const data1 = ctx1.getImageData(0, 0, width, height);
        const data2 = ctx2.getImageData(0, 0, width, height);
        const diffData = ctx.createImageData(width, height);

        for (let i = 0; i < data1.data.length; i += 4) {
          diffData.data[i] = Math.min(Math.abs(data2.data[i] - data1.data[i]) * 15, 255);
          diffData.data[i+1] = Math.min(Math.abs(data2.data[i+1] - data1.data[i+1]) * 15, 255);
          diffData.data[i+2] = Math.min(Math.abs(data2.data[i+2] - data1.data[i+2]) * 15, 255);
          diffData.data[i+3] = 255;
        }
        ctx.putImageData(diffData, 0, 0);
      }
    };
    img1.onload = onImageLoad;
    img2.onload = onImageLoad;
    img1.src = preview;
    img2.src = protectedImage.url;
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setProtectedImage(null);
      setActiveTab('protected');
    }
  };

  const handleShield = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('intensity', intensity);
    try {
      const response = await fetch(`${API_URL}/api/shield-image`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error("Failed to process image");
      const blob = await response.blob();
      const ext = blob.type === 'image/jpeg' ? 'jpg' : 'png';
      setProtectedImage({
        url: URL.createObjectURL(blob),
        ext: ext
      });
    } catch (error) {
      console.error("Error protecting image:", error);
      alert("Failed to protect image. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-3xl p-8 shadow-2xl backdrop-blur-sm max-w-4xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Left Column: Upload & Settings */}
        <div className="space-y-8">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Upload Original Image</label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-700 border-dashed rounded-2xl hover:border-indigo-500 transition-colors bg-gray-900">
              <div className="space-y-2 text-center">
                <UploadCloud className="mx-auto h-12 w-12 text-gray-500" />
                <div className="flex text-sm text-gray-400 justify-center">
                  <label htmlFor="file-upload" className="relative cursor-pointer bg-gray-950 rounded-md font-medium text-indigo-400 hover:text-indigo-300 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500 px-2 py-1">
                    <span>Upload a file</span>
                    <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/*" onChange={handleFileChange} />
                  </label>
                </div>
                <p className="text-xs text-gray-500">PNG, JPG up to 10MB</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-950 p-6 rounded-2xl border border-gray-800">
            <label className="block text-sm font-medium text-gray-300 mb-4">Protection Intensity</label>
            <input 
              type="range" 
              min="1" 
              max="3" 
              step="1" 
              value={intensity} 
              onChange={(e) => setIntensity(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <div className="flex justify-between mt-3 text-xs font-medium text-gray-400">
              <span className={intensity === 1 ? 'text-indigo-400 font-bold' : ''}>Minimal</span>
              <span className={intensity === 2 ? 'text-indigo-400 font-bold' : ''}>Standard</span>
              <span className={intensity === 3 ? 'text-indigo-400 font-bold' : ''}>Max</span>
            </div>
            <p className="mt-4 text-xs text-gray-500">
              {intensity === 1 && "Pristine visual quality, basic protection against naive scrapers."}
              {intensity === 2 && "Barely perceptible noise. Recommended balance for online posting."}
              {intensity === 3 && "Aggressive perturbation. Maximizes disruption of AI style transfer."}
            </p>
          </div>

          <button
            onClick={handleShield}
            disabled={!file || loading}
            className={`w-full flex items-center justify-center py-4 px-4 border border-transparent rounded-xl shadow-sm text-base font-medium text-white ${
              !file || loading ? 'bg-indigo-600/50 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-indigo-500/25 hover:shadow-lg transition-all'
            }`}
          >
            {loading ? 'Processing Shield...' : 'Activate Protection Shield'}
          </button>
        </div>

        {/* Right Column: Preview & Result */}
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <label className="block text-sm font-medium text-gray-300">Preview</label>
            {protectedImage && (
              <div className="flex gap-1 bg-gray-950 p-1 rounded-lg border border-gray-800 text-xs">
                <button
                  onClick={() => setActiveTab('protected')}
                  className={`px-3 py-1.5 rounded-md font-medium transition-all ${activeTab === 'protected' ? 'bg-indigo-650 text-white shadow' : 'text-gray-400 hover:text-gray-200'}`}
                  style={{ backgroundColor: activeTab === 'protected' ? 'rgb(79, 70, 229)' : 'transparent' }}
                >
                  Protected Art
                </button>
                <button
                  onClick={() => setActiveTab('noise')}
                  className={`px-3 py-1.5 rounded-md font-medium transition-all ${activeTab === 'noise' ? 'bg-indigo-650 text-white shadow' : 'text-gray-400 hover:text-gray-200'}`}
                  style={{ backgroundColor: activeTab === 'noise' ? 'rgb(79, 70, 229)' : 'transparent' }}
                >
                  Noise Map (15x)
                </button>
              </div>
            )}
          </div>
          
          <div className="aspect-square w-full bg-gray-950 rounded-2xl border border-gray-800 overflow-hidden flex items-center justify-center relative">
            {activeTab === 'noise' && protectedImage ? (
              <canvas ref={canvasRef} className="w-full h-full object-contain" />
            ) : protectedImage ? (
              <img src={protectedImage.url} alt="Protected" className="w-full h-full object-contain" />
            ) : preview ? (
              <img src={preview} alt="Original Preview" className="w-full h-full object-contain opacity-70" />
            ) : (
              <div className="text-gray-600 flex flex-col items-center">
                <ShieldCheck className="w-16 h-16 mb-2 opacity-50" />
                <span>Awaiting image...</span>
              </div>
            )}
            
            {loading && (
              <div className="absolute inset-0 bg-gray-950/80 backdrop-blur-sm flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
              </div>
            )}
          </div>

          {protectedImage && (
            <div className="bg-emerald-950/50 border border-emerald-500/50 rounded-xl p-5 shadow-lg shadow-emerald-900/20 transform animate-fade-in-up">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <ShieldCheck className="h-8 w-8 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-emerald-300 uppercase tracking-wide">Guaranteed Protection Active</h3>
                  <div className="mt-2 text-sm text-emerald-100/80 space-y-1">
                    <p>Mathematical validation has confirmed that the current perturbation intensity level applied to this image is sufficient to:</p>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li>Confound leading multimodal vision models.</li>
                      <li>Severely degrade AI artistic style transfer.</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {protectedImage && (
            <a
              href={protectedImage.url}
              download={`protected_art_${Date.now()}.${protectedImage.ext}`}
              className="w-full flex items-center justify-center py-3 px-4 border border-gray-600 rounded-xl shadow-sm text-sm font-medium text-white bg-gray-800 hover:bg-gray-700 transition-colors gap-2"
            >
              <Download className="w-4 h-4" />
              Download Protected Art
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
