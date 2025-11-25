import React, { useState } from 'react';
import { Play, RotateCcw, ChevronDown, Activity, AlertCircle } from 'lucide-react';

export default function App() {
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('LSTM (Bidirectional)');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  const models = [
    "LSTM (Bidirectional)",
    "Logistic Regression",
    "Random Forest",
    "Support Vector Machine (SVM)",
    "XGBoost",
    "Multilayer Perceptron (MLP)"
  ];

  const runInference = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    const startTime = performance.now();

    setLogs(prev => [`[INFO] Sending request to model: ${selectedModel}...`, ...prev]);

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lyrics: input,
          model_name: selectedModel
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();
      const endTime = performance.now();
      const timeTaken = (endTime - startTime).toFixed(2);

      setResult({
        ...data,
        processing_time: `${timeTaken}ms`
      });

      setLogs(prev => [
        `[SUCCESS] Received response in ${timeTaken}ms`, 
        `[RESULT] Prediction: ${data.prediction} (${(data.confidence * 100).toFixed(1)}%)`,
        ...prev
      ]);

    } catch (err) {
      console.error(err);
      setError("Failed to connect to backend. Is main.py running?");
      setLogs(prev => [`[ERROR] ${err.message}`, ...prev]);
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setInput('');
    setResult(null);
    setLogs([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans flex flex-col selection:bg-emerald-500/30">
      
      <header className="border-b border-slate-800 bg-slate-900/50 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-medium text-emerald-400 tracking-wide">
            ECS 171 Group 7
          </h1>
          <p className="text-xs text-slate-500 font-mono mt-1">
            Sentiment Analysis Targeting Music Lyrics
          </p>
        </div>
        
      </header>
      <main className="flex-1 flex overflow-hidden">
        
        <div className="w-1/2 flex flex-col border-r border-slate-800">
          <div className="flex-1 p-6 flex flex-col">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">
              Input Lyrics
            </label>
            <textarea 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-transparent border-none resize-none focus:outline-none text-slate-200 placeholder:text-slate-700 font-mono text-sm leading-relaxed"
              placeholder="Paste song lyrics here for classification..."
              spellCheck="false"
            />
          </div>
          
          <div className="p-4 border-t border-slate-800 bg-slate-900/30 flex justify-between items-center">
            <button 
              onClick={clearAll}
              className="text-slate-500 hover:text-slate-300 text-xs font-mono flex items-center gap-2 transition-colors"
            >
              <RotateCcw className="w-3 h-3" /> RESET
            </button>
            <button 
              onClick={runInference}
              disabled={loading || !input}
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-emerald-900/20"
            >
              {loading ? (
                <span className="animate-pulse">Processing...</span>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" /> Classify
                </>
              )}
            </button>
          </div>
        </div>

        <div className="w-1/2 flex flex-col bg-slate-900/20">
          
          <div className="flex-1 p-8 flex flex-col justify-center items-center border-b border-slate-800 relative overflow-hidden">
            {error && (
              <div className="absolute top-4 bg-red-900/50 text-red-200 px-4 py-2 rounded border border-red-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4" /> {error}
              </div>
            )}

            {result ? (
              <div className="w-full max-w-sm animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="text-center mb-8">
                  <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Prediction</div>
                  <div className={`text-3xl font-light ${result.prediction === "Age Appropriate" ? "text-emerald-400" : "text-rose-400"}`}>
                    {result.prediction}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="bg-slate-900 p-4 rounded border border-slate-800">
                    <div className="text-xs text-slate-500 mb-1">Score</div>
                    <div className="text-xl font-mono text-slate-200">{result.score.toFixed(2)}</div>
                  </div>
                  <div className="bg-slate-900 p-4 rounded border border-slate-800">
                    <div className="text-xs text-slate-500 mb-1">Time</div>
                    <div className="text-xl font-mono text-slate-200">{result.processing_time}</div>
                  </div>
                </div>
                
                <div className="mt-6 text-center">
                  <span className="text-xs font-mono text-slate-600 bg-slate-950 px-3 py-1 rounded-full border border-slate-800">
                    Model: {result.model}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-slate-700 text-sm font-mono flex flex-col items-center gap-4">
                <Activity className="w-12 h-12 opacity-20" />
                <span>Waiting for input...</span>
              </div>
            )}
          </div>

          <div className="h-1/3 bg-slate-950 flex flex-col">
            <div className="px-6 py-3 border-b border-slate-800 text-xs font-bold text-slate-600 uppercase tracking-wider">
              Execution Log
            </div>
            <div className="flex-1 overflow-auto p-6 font-mono text-xs space-y-2">
              {logs.length === 0 && <span className="text-slate-800">System ready.</span>}
              {logs.map((log, i) => (
                <div key={i} className="text-slate-400 border-l border-slate-800 pl-3">
                  {log}
                </div>
              ))}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}