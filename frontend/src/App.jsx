import React, { useState } from 'react';
import { ShieldAlert } from 'lucide-react';
import ShieldView from './components/ShieldView';
import CompareView from './components/CompareView';

function App() {
  const [view, setView] = useState('shield'); // 'shield' or 'compare'
  
  const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-6xl w-full space-y-12">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl flex items-center justify-center gap-4">
            <ShieldAlert className="w-12 h-12 text-indigo-500" />
            PixelPoison
          </h1>
          <p className="mt-4 text-xl text-gray-400">
            Protect your artwork from unauthorized AI training and style transfer.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex justify-center gap-4">
          <button 
            onClick={() => setView('shield')}
            className={`px-6 py-2 rounded-full font-bold transition-all ${view === 'shield' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'}`}
          >
            Protection Shield
          </button>
          <button 
            onClick={() => setView('compare')}
            className={`px-6 py-2 rounded-full font-bold transition-all ${view === 'compare' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'}`}
          >
            Model Evaluation
          </button>
        </div>

        {view === 'shield' && <ShieldView API_URL={API_URL} />}
        {view === 'compare' && <CompareView API_URL={API_URL} />}

      </div>
    </div>
  );
}

export default App;
