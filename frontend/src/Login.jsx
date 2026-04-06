import React, { useState } from 'react';
import { ShieldCheck, Mail, Lock, ArrowRight, Smartphone, AlertCircle, User } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export default function Login() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    
    // Basic validation
    if (isSignUp && !name.trim()) {
      setError('Please enter your full name.');
      return;
    }
    if (!identifier.trim()) {
      setError('Please enter a mobile number or email ID.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    
    // Check if identifier is email or phone (simple check for at least a digit or @)
    const isEmail = identifier.includes('@');
    const isPhone = /^\d+$/.test(identifier.replace(/[\s\-\+]/g, ''));
    
    if (!isEmail && !isPhone) {
      setError('Please enter a valid email ID or mobile number.');
      return;
    }

    // Mock Login / Signup Success
    navigate('/');
  };

  const toggleMode = (e) => {
    e.preventDefault();
    setIsSignUp(!isSignUp);
    setError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-slate-50 dark:bg-slate-900 transition-colors duration-300 px-4">
      {/* Background blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 dark:opacity-20 animate-blob"></div>
      <div className="absolute top-[20%] right-[-10%] w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 dark:opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 dark:opacity-20 animate-blob animation-delay-4000"></div>

      <div className="w-full max-w-md z-10">
        {/* Logo */}
        <div className="flex justify-center mb-8 animate-in fade-in slide-in-from-top-4 duration-700">
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="bg-white dark:bg-slate-800 p-3 rounded-2xl shadow-lg group-hover:scale-110 transition-transform">
              <ShieldCheck className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
              TruthGuard AI
            </span>
          </Link>
        </div>

        {/* Auth Card */}
        <div className="glass-card bg-white/70 dark:bg-slate-900/70 p-8 rounded-3xl shadow-2xl backdrop-blur-xl border border-white/20 dark:border-slate-700/50 animate-in fade-in zoom-in-95 duration-500">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-slate-800 dark:text-white">
              {isSignUp ? 'Create an account' : 'Welcome back'}
            </h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-2">
              {isSignUp ? 'Join TruthGuard to analyze content and stay protected.' : 'Log in to your account using your mobile number or email ID.'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 p-3 rounded-xl text-sm flex items-start border border-red-100 dark:border-red-800/50">
                <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                {error}
              </div>
            )}

            {isSignUp && (
              <div className="space-y-2 animate-in slide-in-from-top-2 fade-in duration-300">
                <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Full Name
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-500 transition-colors">
                    <User className="h-5 w-5" />
                  </div>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="pl-10 w-full p-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all placeholder:text-slate-400"
                    placeholder="John Doe"
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Mobile Number or Email ID
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-500 transition-colors">
                  {identifier.includes('@') ? (
                    <Mail className="h-5 w-5" />
                  ) : (
                    <Smartphone className="h-5 w-5" />
                  )}
                </div>
                <input
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className="pl-10 w-full p-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all placeholder:text-slate-400"
                  placeholder="name@company.com or +1 234 567 890"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Password
                </label>
                {!isSignUp && (
                  <a href="#" className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500">
                    Forgot password?
                  </a>
                )}
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-500 transition-colors">
                  <Lock className="h-5 w-5" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 w-full p-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all placeholder:text-slate-400"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
               type="submit"
               className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center justify-center group"
            >
              {isSignUp ? 'Sign Up' : 'Sign In'}
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </button>
          </form>
          
          <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700 text-center">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
              <a href="#" onClick={toggleMode} className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 transition-colors">
                {isSignUp ? 'Sign in' : 'Sign up'}
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
