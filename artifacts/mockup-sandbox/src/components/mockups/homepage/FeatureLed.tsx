import React, { useEffect, useState } from 'react';
import { Play, Database, Github, Zap, Shield, Wand2, Activity, AlertTriangle, Stethoscope, ShoppingBag } from 'lucide-react';

export function FeatureLed() {
  const [activeNode, setActiveNode] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveNode((prev) => (prev + 1) % 5);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const agents = [
    { icon: '🧲', name: 'Harvester', desc: 'Reads graphs' },
    { icon: '🔍', name: 'Detector', desc: 'Finds semantic drift' },
    { icon: '💥', name: 'Blast Radius', desc: 'Measures impact' },
    { icon: '🤝', name: 'Broker', desc: 'Proposes canonical fix' },
    { icon: '✅', name: 'Writer', desc: 'Syncs back to DataHub' },
  ];

  return (
    <div className="min-h-screen bg-[#0d1117] text-slate-200 font-sans selection:bg-cyan-500/30 overflow-hidden">
      <style>{`
        @keyframes flow {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        .animate-flow {
          background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.8), transparent);
          background-size: 200% 100%;
          animation: flow 2s infinite linear;
        }
      `}</style>

      {/* Nav */}
      <nav className="border-b border-slate-800/80 bg-[#0d1117]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl text-white tracking-tight">
            <span>🪨</span>
            <span>Rosetta</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#" className="hover:text-white transition-colors">How it works</a>
            <a href="#" className="hover:text-white transition-colors">Features</a>
            <a href="#" className="hover:text-white transition-colors">DataHub</a>
          </div>
          <div>
            <button className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition-colors shadow-[0_0_15px_rgba(8,145,178,0.4)]">
              <Play className="w-4 h-4 fill-current" /> Run Demo
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <header className="pt-24 pb-20 px-6 text-center max-w-5xl mx-auto relative">
        {/* Abstract background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-cyan-900/20 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 text-slate-300 text-xs font-semibold tracking-wide uppercase mb-8 relative z-10">
          <Database className="w-3.5 h-3.5 text-cyan-400" />
          DataHub Agent Hackathon 2026
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6 text-balance leading-[1.1] relative z-10">
          Rosetta is a semantic linter for your <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">DataHub graph.</span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto text-balance leading-relaxed mb-10 relative z-10">
          Five agents scan your metadata, detect where teams define the same metric differently, measure the downstream blast radius, and write canonical fixes back to DataHub.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 relative z-10">
          <button className="bg-white text-slate-900 hover:bg-slate-100 px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-lg">
            <Play className="w-4 h-4 fill-current" /> Run Demo
          </button>
          <button className="border border-slate-700 bg-slate-800/30 hover:bg-slate-800 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors">
            <Database className="w-4 h-4" /> Connect to DataHub
          </button>
          <button className="text-slate-400 hover:text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors">
            <Github className="w-4 h-4" /> View on GitHub
          </button>
        </div>
      </header>

      {/* Agent Pipeline Visual */}
      <section className="py-12 px-6 max-w-6xl mx-auto relative z-10">
        <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-8 backdrop-blur-sm overflow-hidden relative shadow-2xl">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-0 relative z-10">
            {agents.map((agent, i) => (
              <React.Fragment key={agent.name}>
                <div className={`flex flex-col items-center gap-3 relative transition-all duration-700 ${activeNode === i ? 'scale-110' : 'scale-100 opacity-60'}`}>
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-3xl border shadow-lg transition-all duration-700 ${
                    activeNode === i 
                      ? 'bg-cyan-950/60 border-cyan-400/80 shadow-[0_0_30px_rgba(34,211,238,0.5)] z-20' 
                      : 'bg-slate-800 border-slate-700 z-10'
                  }`}>
                    {agent.icon}
                  </div>
                  <div className="text-center">
                    <div className={`font-semibold text-sm mb-1 transition-colors duration-700 ${activeNode === i ? 'text-cyan-400' : 'text-slate-300'}`}>{agent.name}</div>
                    <div className="text-xs text-slate-500 hidden md:block w-24 text-balance">{agent.desc}</div>
                  </div>
                </div>
                {i < agents.length - 1 && (
                  <div className="hidden md:flex flex-1 items-center justify-center px-2">
                    <div className="h-0.5 w-full bg-slate-800 relative overflow-hidden rounded-full">
                      <div className={`absolute inset-0 transition-opacity duration-300 ${activeNode === i ? 'opacity-100 animate-flow' : 'opacity-0'}`} />
                    </div>
                  </div>
                )}
                {i < agents.length - 1 && (
                  <div className="md:hidden flex h-8 w-0.5 bg-slate-800 relative overflow-hidden">
                     <div className={`absolute inset-0 bg-cyan-400 transition-opacity duration-300 ${activeNode === i ? 'opacity-100' : 'opacity-0'}`} />
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </section>

      {/* Try It Live */}
      <section className="py-24 px-6 bg-[#0a0e17] border-y border-slate-800/80">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">No DataHub? No problem.</h2>
            <p className="text-slate-400 max-w-2xl mx-auto text-lg">Run the agents against one of our pre-configured local SQLite datasets to see how Rosetta catches semantic drift.</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {/* Healthcare */}
            <div className="bg-slate-900/60 border border-slate-700/60 hover:border-cyan-500/50 transition-all rounded-2xl p-8 group shadow-xl">
              <div className="w-14 h-14 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-6 text-cyan-400 group-hover:bg-cyan-950/50 group-hover:border-cyan-800/50 transition-colors">
                <Stethoscope className="w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Healthcare Network</h3>
              <p className="text-base text-slate-400 mb-8 leading-relaxed h-20">A simulated hospital system with disparate definitions of "patient encounter" and "billing_amount" across clinical and financial systems.</p>
              
              <div className="flex flex-col gap-3 mb-8 text-sm">
                <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
                  <span className="text-slate-500">Dataset Size</span>
                  <div className="flex items-center gap-1.5 text-slate-300 font-medium">
                    <Database className="w-4 h-4 text-slate-500" /> 55,500 records
                  </div>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <span className="text-slate-500">Semantic Drift</span>
                  <div className="flex items-center gap-1.5 text-amber-400 font-medium">
                    <AlertTriangle className="w-4 h-4" /> 4 conflicts injected
                  </div>
                </div>
              </div>
              
              <button className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium flex items-center justify-center gap-2 transition-colors border border-slate-700 group-hover:bg-cyan-600 group-hover:border-cyan-500 group-hover:text-white group-hover:shadow-[0_0_20px_rgba(8,145,178,0.4)]">
                <Play className="w-4 h-4 fill-current" /> Scan Healthcare Data
              </button>
            </div>

            {/* Retail */}
            <div className="bg-slate-900/60 border border-slate-700/60 hover:border-purple-500/50 transition-all rounded-2xl p-8 group shadow-xl">
              <div className="w-14 h-14 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-6 text-purple-400 group-hover:bg-purple-950/50 group-hover:border-purple-800/50 transition-colors">
                <ShoppingBag className="w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Fiction Retail Co.</h3>
              <p className="text-base text-slate-400 mb-8 leading-relaxed h-20">An e-commerce dataset where marketing and logistics teams have conflicting ideas on what constitutes an "active_order".</p>
              
              <div className="flex flex-col gap-3 mb-8 text-sm">
                <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
                  <span className="text-slate-500">Dataset Size</span>
                  <div className="flex items-center gap-1.5 text-slate-300 font-medium">
                    <Database className="w-4 h-4 text-slate-500" /> 150,000 orders
                  </div>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <span className="text-slate-500">Semantic Drift</span>
                  <div className="flex items-center gap-1.5 text-amber-400 font-medium">
                    <AlertTriangle className="w-4 h-4" /> 2 conflicts injected
                  </div>
                </div>
              </div>
              
              <button className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium flex items-center justify-center gap-2 transition-colors border border-slate-700 group-hover:bg-purple-600 group-hover:border-purple-500 group-hover:text-white group-hover:shadow-[0_0_20px_rgba(147,51,234,0.4)]">
                <Play className="w-4 h-4 fill-current" /> Scan Retail Data
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features & Conflict Card */}
      <section className="py-24 px-6 max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          
          {/* Features Left */}
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight">Catch semantic drift before it impacts reporting.</h2>
            <p className="text-slate-400 text-lg mb-10 leading-relaxed">
              Data pipelines break silently when different teams use the same column name but mean different things. Rosetta parses definitions, analyzes lineage, and computes the financial risk of these misunderstandings.
            </p>
            
            <div className="grid sm:grid-cols-2 gap-8">
              <div className="flex flex-col gap-3">
                <div className="w-12 h-12 rounded-xl bg-cyan-950 border border-cyan-800/50 flex items-center justify-center text-cyan-400 mb-1">
                  <Zap className="w-5 h-5" />
                </div>
                <h4 className="font-semibold text-white text-lg">Zero-config demo</h4>
                <p className="text-sm text-slate-400 leading-relaxed">Run against local SQLite mock data immediately. No DataHub setup required for the hackathon demo.</p>
              </div>
              
              <div className="flex flex-col gap-3">
                <div className="w-12 h-12 rounded-xl bg-blue-950 border border-blue-800/50 flex items-center justify-center text-blue-400 mb-1">
                  <Database className="w-5 h-5" />
                </div>
                <h4 className="font-semibold text-white text-lg">DataHub-native</h4>
                <p className="text-sm text-slate-400 leading-relaxed">Connects directly to your DataHub instance via GraphQL to analyze metadata, lineage, and schemas.</p>
              </div>
              
              <div className="flex flex-col gap-3">
                <div className="w-12 h-12 rounded-xl bg-rose-950 border border-rose-800/50 flex items-center justify-center text-rose-400 mb-1">
                  <Activity className="w-5 h-5" />
                </div>
                <h4 className="font-semibold text-white text-lg">Blast-radius severity</h4>
                <p className="text-sm text-slate-400 leading-relaxed">Calculates exact downstream row impact and estimates dollar-value risk based on connected tables.</p>
              </div>
              
              <div className="flex flex-col gap-3">
                <div className="w-12 h-12 rounded-xl bg-emerald-950 border border-emerald-800/50 flex items-center justify-center text-emerald-400 mb-1">
                  <Wand2 className="w-5 h-5" />
                </div>
                <h4 className="font-semibold text-white text-lg">One-click fixes</h4>
                <p className="text-sm text-slate-400 leading-relaxed">Agentic resolution engine proposes canonical definitions and can push updates directly to DataHub.</p>
              </div>
            </div>
          </div>

          {/* Sample Conflict Card Right */}
          <div className="relative mt-8 lg:mt-0">
            {/* Glow behind card */}
            <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/20 to-rose-500/20 blur-[80px] transform -rotate-3 pointer-events-none" />
            
            <div className="relative bg-[#111827] border border-slate-700/80 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden font-mono text-sm">
              {/* Header */}
              <div className="border-b border-slate-800 bg-[#1f2937]/50 px-5 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-rose-500" />
                  <span className="font-semibold text-white font-sans text-base">Semantic Conflict Detected</span>
                </div>
                <div className="bg-rose-950/60 text-rose-400 border border-rose-500/30 px-2.5 py-1 rounded text-xs font-bold tracking-wide shadow-[0_0_10px_rgba(244,63,94,0.2)]">
                  CRITICAL
                </div>
              </div>
              
              {/* Metric Context */}
              <div className="p-5 border-b border-slate-800">
                <div className="text-slate-500 text-xs uppercase tracking-wider mb-2 font-sans font-semibold">Target Metric</div>
                <div className="flex items-center gap-2 text-cyan-300 bg-cyan-950/40 w-fit px-3 py-1.5 rounded-md border border-cyan-800/60 font-medium text-base">
                  <Database className="w-4 h-4" /> billing_amount
                </div>
              </div>
              
              {/* The Conflict */}
              <div className="grid grid-cols-2 divide-x divide-slate-800 border-b border-slate-800">
                <div className="p-5 bg-[#1f2937]/20">
                  <div className="text-slate-500 text-xs mb-3 flex items-center gap-2 font-sans font-semibold tracking-wide">
                    <span className="w-2 h-2 rounded-full bg-slate-400" />
                    CLINICAL_TEAM
                  </div>
                  <p className="text-slate-300 leading-relaxed font-sans text-sm">
                    Includes all transactional items, <span className="text-rose-400 font-semibold bg-rose-950/60 px-1.5 py-0.5 rounded">including negatives</span> (credits/errors).
                  </p>
                </div>
                <div className="p-5 bg-[#1f2937]/20">
                  <div className="text-slate-500 text-xs mb-3 flex items-center gap-2 font-sans font-semibold tracking-wide">
                    <span className="w-2 h-2 rounded-full bg-slate-400" />
                    FINANCE_TEAM
                  </div>
                  <p className="text-slate-300 leading-relaxed font-sans text-sm">
                    Net positive revenue only. <span className="text-cyan-400 font-semibold bg-cyan-950/60 px-1.5 py-0.5 rounded">Must always be positive.</span>
                  </p>
                </div>
              </div>
              
              {/* Blast Radius */}
              <div className="p-5 border-b border-slate-800 bg-rose-950/10">
                <div className="text-slate-500 text-xs uppercase tracking-wider mb-4 font-sans font-semibold">Downstream Blast Radius</div>
                <div className="flex gap-12">
                  <div>
                    <div className="text-3xl font-bold text-white mb-1">1,215</div>
                    <div className="text-xs text-slate-400 font-sans font-medium">Silent mismatched rows</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-rose-400 mb-1">$28.5M</div>
                    <div className="text-xs text-rose-400/80 font-sans font-medium">Revenue at risk</div>
                  </div>
                </div>
              </div>
              
              {/* Resolution Proposal */}
              <div className="p-5 bg-emerald-950/20">
                <div className="text-emerald-500/90 text-xs uppercase tracking-wider mb-3 font-sans font-semibold flex items-center gap-2">
                  <Wand2 className="w-3.5 h-3.5" /> Proposed Canonical Definition
                </div>
                <div className="bg-[#0b1221] p-4 rounded-xl border border-emerald-900/40 text-emerald-300/90 font-sans leading-relaxed text-sm mb-5 shadow-inner">
                  "Total recognized revenue (always positive). For gross totals including credits/errors, use <code className="bg-emerald-950 px-1 py-0.5 rounded text-emerald-400 font-mono text-xs">gross_billing_amount</code>."
                </div>
                <div className="flex gap-3">
                  <button className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white py-2.5 rounded-lg font-sans font-semibold text-sm transition-colors shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                    Approve & Push to DataHub
                  </button>
                  <button className="px-5 bg-slate-800 hover:bg-slate-700 text-slate-300 py-2.5 rounded-lg font-sans font-semibold text-sm transition-colors border border-slate-700">
                    Edit
                  </button>
                </div>
              </div>
              
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-12 px-6 text-center text-slate-500 text-sm mt-12 bg-[#0d1117]">
        <div className="flex items-center justify-center gap-2 mb-4">
          <span className="text-xl">🪨</span>
          <span className="font-bold text-slate-300 tracking-wider">ROSETTA</span>
        </div>
        <p className="font-medium">Built for the DataHub Agent Hackathon &middot; Open Source</p>
      </footer>
    </div>
  );
}
