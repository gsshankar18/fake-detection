import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, Moon, Sun, Search, ArrowRight, FileText, Link as LinkIcon, Image as ImageIcon, UploadCloud, Activity, AlertTriangle
} from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default function Home({ darkMode, setDarkMode }) {
  const [activeTab, setActiveTab] = useState('text');
  const [inputText, setInputText] = useState('');
  const [inputUrl, setInputUrl] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [showAnalyzer, setShowAnalyzer] = useState(false);

  const validateInput = () => {
    if (activeTab === 'text') {
      const text = inputText.trim();
      if (text.length < 10) return 'Please enter at least 10 characters of text.';
      if (text.split(/\s+/).length < 3) return 'Please enter a complete sentence (at least 3 words).';
      if (/(.)\1{10,}/.test(text)) return 'Input contains excessive repetitive characters. Please enter valid text.';
    }
    if (activeTab === 'url') {
      const url = inputUrl.trim();
      if (!url) return 'Please enter a valid URL.';
      try {
        new URL(url);
      } catch (_) {
        return 'Please enter a valid URL format (e.g., https://example.com).';
      }
    }
    if (activeTab === 'image' && !imageFile) {
      return 'Please upload a screenshot or image first.';
    }
    return null;
  };

  const handleAnalyze = async () => {
    const validationError = validateInput();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      if (activeTab === 'image') {
        const formData = new FormData();
        formData.append('file', imageFile);

        const res = await axios.post(`${API_BASE_URL}/analyze-image`, formData);
        setResult(res.data);
      } else {
        const endpoint = activeTab === 'text' ? '/analyze-text' : '/analyze-url';
        const payload = activeTab === 'text' ? { text: inputText } : { url: inputUrl };

        const res = await axios.post(`${API_BASE_URL}${endpoint}`, payload);
        setResult(res.data);
      }
    } catch (err) {
      let errorMsg = 'An error occurred while analyzing the content.';
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail[0]?.msg || JSON.stringify(err.response.data.detail);
        } else if (typeof err.response.data.detail === 'string') {
          errorMsg = err.response.data.detail;
        }
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const scrollToAnalyzer = () => {
    setShowAnalyzer(true);
    setTimeout(() => {
      document.getElementById('analyzer-section')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleTabSwitch = (tab) => {
    setActiveTab(tab);
    setResult(null);
    setError('');
  };

  return (
    <div className="min-h-screen transition-colors duration-300 bg-slate-50 dark:bg-slate-900">
      <nav className="fixed w-full z-50 glass-card border-b-0 rounded-none bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link to="/" className="flex items-center space-x-2">
              <ShieldCheck className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
                TruthGuard AI
              </span>
            </Link>
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </nav>

      <main className="pt-24 pb-16">
        <section className="relative px-6 lg:px-8 py-14">
          <div className="mx-auto max-w-5xl text-center">
            <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl mb-6">
              Detect <span className="text-gradient">Fake Content</span> with Precision
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              Protect yourself from misinformation. Paste text or a URL and let our advanced detection engine analyze the truthfulness of the content.
            </p>
            <div className="mt-10 flex justify-center gap-x-4">
              <button
                onClick={scrollToAnalyzer}
                className="inline-flex items-center rounded-full bg-indigo-600 px-8 py-4 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
              >
                Try Now <ArrowRight className="ml-2 h-4 w-4" />
              </button>
            </div>
          </div>
        </section>

        <section id="analyzer-section" className="mx-auto max-w-6xl px-6 lg:px-8">
          <div className="grid gap-8 lg:grid-cols-2">
            <div className="glass-card rounded-3xl p-8 shadow-lg bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800">
              <div className="flex gap-3 mb-6">
                <button
                  onClick={() => handleTabSwitch('text')}
                  className={`flex-1 rounded-2xl px-4 py-3 text-sm font-semibold ${activeTab === 'text' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200'}`}
                >
                  <FileText className="inline h-4 w-4 mr-2" /> Text
                </button>
                <button
                  onClick={() => handleTabSwitch('url')}
                  className={`flex-1 rounded-2xl px-4 py-3 text-sm font-semibold ${activeTab === 'url' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200'}`}
                >
                  <LinkIcon className="inline h-4 w-4 mr-2" /> URL
                </button>
                <button
                  onClick={() => handleTabSwitch('image')}
                  className={`flex-1 rounded-2xl px-4 py-3 text-sm font-semibold ${activeTab === 'image' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200'}`}
                >
                  <ImageIcon className="inline h-4 w-4 mr-2" /> Image
                </button>
              </div>

              <div className="space-y-4">
                {activeTab === 'text' && (
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Paste your text here..."
                    className="w-full min-h-[180px] rounded-3xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 p-4 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                )}

                {activeTab === 'url' && (
                  <input
                    type="url"
                    value={inputUrl}
                    onChange={(e) => setInputUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="w-full rounded-3xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 p-4 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                )}

                {activeTab === 'image' && (
                  <div className="rounded-3xl border border-dashed border-slate-300 dark:border-slate-700 p-6 text-center bg-slate-50 dark:bg-slate-900">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                          setImageFile(file);
                          const reader = new FileReader();
                          reader.onload = (event) => setImagePreview(event.target.result);
                          reader.readAsDataURL(file);
                        }
                      }}
                      className="hidden"
                      id="image-upload"
                    />
                    <label htmlFor="image-upload" className="cursor-pointer inline-flex flex-col items-center gap-3 text-slate-500 dark:text-slate-400">
                      <UploadCloud className="h-10 w-10" />
                      <span>Upload image</span>
                      <span className="text-sm">PNG, JPG, GIF</span>
                    </label>
                    {imagePreview && <img src={imagePreview} alt="Preview" className="mx-auto mt-4 max-h-48 rounded-2xl" />}
                  </div>
                )}

                {error && (
                  <div className="rounded-3xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 text-red-700 dark:text-red-200">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5" />
                      <span>{error}</span>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-3xl bg-indigo-600 px-6 py-4 text-sm font-semibold text-white hover:bg-indigo-500 disabled:bg-slate-400 transition"
                >
                  {loading ? 'Analyzing...' : 'Analyze Content'}
                </button>
              </div>
            </div>

            <div className="glass-card rounded-3xl p-8 shadow-lg bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800">
              <h2 className="text-xl font-semibold mb-4">Results</h2>
              {result ? (
                <div className="space-y-5">
                  <div className={`rounded-3xl p-5 ${result.prediction === 'FAKE' ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' : 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800'} border`}>
                    <h3 className="text-lg font-bold">Prediction: {result.prediction}</h3>
                    <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                  </div>

                  <div className="rounded-3xl bg-slate-50 dark:bg-slate-950 p-5">
                    <h3 className="font-semibold mb-3">Explanation</h3>
                    <div className="space-y-2 text-sm text-slate-700 dark:text-slate-300">
                      {result.explanation.map((line, idx) => (
                        <p key={idx}>{line}</p>
                      ))}
                    </div>
                  </div>

                  {result.highlighted_text && (
                    <div className="rounded-3xl bg-slate-50 dark:bg-slate-950 p-5">
                      <h3 className="font-semibold mb-3">Highlighted Text</h3>
                      <div className="prose prose-sm dark:prose-invert text-slate-700 dark:text-slate-200" dangerouslySetInnerHTML={{ __html: result.highlighted_text }} />
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 p-6 text-slate-600 dark:text-slate-400">
                  <p>Submit text, a URL, or an image to see the analysis results here.</p>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
