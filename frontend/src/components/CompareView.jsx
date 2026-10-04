import React, { useState } from 'react';
import { Sparkles, Image as ImageIcon, Activity } from 'lucide-react';

export default function CompareView({ API_URL }) {
  const [comparePrompt, setComparePrompt] = useState('generate an image of naruto, myart');
  const [comparing, setComparing] = useState(false);
  const [compareResults, setCompareResults] = useState(null);
  const [compareError, setCompareError] = useState(null);

  const handleCompare = async () => {
    if (!comparePrompt) return;
    setComparing(true);
    setCompareError(null);
    setCompareResults(null);
    try {
      const response = await fetch(`${API_URL}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: comparePrompt })
      });
      if (!response.ok) throw new Error("Failed to generate comparison. Ensure backend is running and diffusers is installed.");
      const data = await response.json();
      setCompareResults(data);
    } catch (err) {
      setCompareError(err.message);
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-3xl p-8 shadow-2xl backdrop-blur-sm mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
          <Sparkles className="text-indigo-400 w-6 h-6" />
          Model Efficacy Evaluation
        </h2>
        <p className="text-gray-400">
          Compare generation results between the clean model and the protected (poisoned) model to visually verify that style extraction has been disrupted.
        </p>
      </div>

      <div className="space-y-8">
        <div className="bg-gray-950 p-6 rounded-2xl border border-gray-800">
          <label className="block text-sm font-medium text-gray-300 mb-2">Image Generation Prompt</label>
          <div className="flex gap-4">
            <input
              type="text"
              value={comparePrompt}
              onChange={(e) => setComparePrompt(e.target.value)}
              className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g. generate an image of naruto, myart"
            />
            <button
              onClick={handleCompare}
              disabled={!comparePrompt || comparing}
              className={`px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all ${
                !comparePrompt || comparing ? 'bg-indigo-600/50 text-white/50 cursor-not-allowed' : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-500/25'
              }`}
            >
              {comparing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Generate Comparison
                </>
              )}
            </button>
          </div>
          {compareError && (
            <p className="mt-4 text-red-400 text-sm bg-red-900/20 p-3 rounded-lg border border-red-900/50">
              Error: {compareError}
            </p>
          )}
        </div>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Clean Model Result */}
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-gray-900 p-4 rounded-xl border border-gray-800">
              <div>
                <h3 className="font-bold text-white text-lg">Clean Model (LoRA)</h3>
                <p className="text-xs text-gray-400">Trained on original unprotected images</p>
              </div>
              <div className="bg-red-500/10 text-red-400 px-3 py-1 rounded-full text-xs font-bold border border-red-500/20">
                Vulnerable
              </div>
            </div>
            
            <div className="aspect-square bg-gray-950 rounded-2xl border border-gray-800 overflow-hidden flex items-center justify-center relative shadow-inner">
              {comparing ? (
                <div className="text-gray-500 flex flex-col items-center animate-pulse">
                  <ImageIcon className="w-12 h-12 mb-2 opacity-50" />
                  <span>Generating clean image...</span>
                </div>
              ) : compareResults?.clean_url ? (
                <img src={compareResults.clean_url} alt="Clean Model Result" className="w-full h-full object-contain hover:scale-105 transition-transform duration-500" />
              ) : (
                <div className="text-gray-600 flex flex-col items-center">
                  <ImageIcon className="w-12 h-12 mb-2 opacity-20" />
                  <span className="text-sm">Awaiting generation</span>
                </div>
              )}
            </div>
          </div>

          {/* Poisoned Model Result */}
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-emerald-900/20 p-4 rounded-xl border border-emerald-900/50">
              <div>
                <h3 className="font-bold text-emerald-400 text-lg">Protected Model (Poisoned)</h3>
                <p className="text-xs text-gray-400">Trained on images processed by Shield</p>
              </div>
              <div className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-xs font-bold border border-emerald-500/30">
                Protected
              </div>
            </div>
            
            <div className="aspect-square bg-gray-950 rounded-2xl border border-gray-800 overflow-hidden flex items-center justify-center relative shadow-inner">
              {comparing ? (
                <div className="text-gray-500 flex flex-col items-center animate-pulse">
                  <ImageIcon className="w-12 h-12 mb-2 opacity-50" />
                  <span>Generating protected image...</span>
                </div>
              ) : compareResults?.poisoned_url ? (
                <img src={compareResults.poisoned_url} alt="Poisoned Model Result" className="w-full h-full object-contain hover:scale-105 transition-transform duration-500" />
              ) : (
                <div className="text-gray-600 flex flex-col items-center">
                  <ImageIcon className="w-12 h-12 mb-2 opacity-20" />
                  <span className="text-sm">Awaiting generation</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quantitative Metrics */}
        {compareResults?.ssim !== undefined && compareResults?.ssim !== null && (
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl mt-8">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" />
              Quantitative Metrics: Structural Similarity (SSIM)
            </h3>
            <div className="flex flex-col md:flex-row gap-6 items-center">
              <div className="flex-1 w-full">
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-400">Structural Similarity Index</span>
                  <span className="text-sm font-bold text-white">{(compareResults.ssim * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-4 overflow-hidden relative">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ${compareResults.ssim < 0.5 ? 'bg-emerald-500' : 'bg-red-500'}`} 
                    style={{ width: `${Math.max(0, compareResults.ssim * 100)}%` }}
                  ></div>
                  {/* Target Threshold Line */}
                  <div className="absolute top-0 bottom-0 left-[50%] w-0.5 bg-gray-400 border-l border-r border-gray-900 z-10"></div>
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500 font-medium">
                  <span>0% (Destroyed)</span>
                  <span>50% (Protection Target)</span>
                  <span>100% (Identical)</span>
                </div>
              </div>
              
              <div className="md:w-1/3 bg-gray-950 p-4 rounded-xl border border-gray-800">
                <p className="text-sm text-gray-300">
                  {compareResults.ssim < 0.5 ? (
                    <span className="text-emerald-400 font-bold block mb-1">✅ Excellent Protection</span>
                  ) : (
                    <span className="text-red-400 font-bold block mb-1">❌ Poor Protection</span>
                  )}
                  A lower score means the AI failed to replicate the original style. The protection successfully disrupted the latent space!
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
