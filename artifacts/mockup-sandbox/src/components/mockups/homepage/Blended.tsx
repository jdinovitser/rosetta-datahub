import React, { useState, useEffect } from 'react';
import { Database, Play, Github, Stethoscope, ShoppingBag, Terminal, CheckCircle2, AlertTriangle, AlertCircle, Sparkles, Activity, FileJson, ArrowRight, BookOpen, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Blended() {
  const [activeNode, setActiveNode] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveNode((prev) => (prev + 1) % 5);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const agents = [
    { name: "Harvester", icon: Database, emoji: "🧲" },
    { name: "Detector", icon: Search, emoji: "🔍" },
    { name: "Blast Radius", icon: Activity, emoji: "💥" },
    { name: "Broker", icon: FileJson, emoji: "🤝" },
    { name: "Writer", icon: CheckCircle2, emoji: "✅" },
  ];

  return (
    <div className="min-h-screen bg-[#06080c] text-slate-200 font-sans selection:bg-cyan-900/50">
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes flow {
          0% { transform: translateX(-100%); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateX(100%); opacity: 0; }
        }
        .animate-flow {
          animation: flow 2s infinite linear;
        }
      `}} />

      {/* Nav */}
      <nav className="sticky top-0 z-50 bg-[#0d1117]/80 backdrop-blur border-b border-slate-800/80">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl text-white">
            <img src="/__mockup/images/mascot-circle.png" alt="Rosetta" className="w-9 h-9 rounded-full" />
            Rosetta
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#how-it-works" className="hover:text-white transition-colors">How it works</a>
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#datahub" className="hover:text-white transition-colors">DataHub</a>
          </div>
          <Button className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-full px-6">
            <Play className="w-4 h-4 mr-2 fill-current" /> Run Demo
          </Button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-24 pb-20 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-cyan-900/20 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="max-w-6xl mx-auto px-6 relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 text-sm font-medium text-slate-300 mb-8">
            <Database className="w-4 h-4 text-cyan-400" />
            DataHub Agent Hackathon 2026
          </div>
          
          <div className="flex justify-center mb-6">
            <img
              src="/__mockup/images/mascot-sticker.png"
              alt="Rosetta mascot"
              className="w-40 h-40 object-contain drop-shadow-[0_0_40px_rgba(34,211,238,0.35)]"
              style={{ mixBlendMode: 'screen' }}
            />
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold text-balance tracking-tight text-white mb-6 leading-tight">
            Your teams define the same metric differently.<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              Rosetta finds where — before it costs you.
            </span>
          </h1>
          
          <p className="max-w-3xl mx-auto text-lg md:text-xl text-slate-400 mb-12 leading-relaxed">
            Five agents scan your metadata, detect where teams define the same metric differently, measure the downstream blast radius, and write canonical fixes back to DataHub.
          </p>
          
          <div className="flex flex-wrap items-center justify-center gap-4 mb-24">
            <Button size="lg" className="bg-white hover:bg-slate-200 text-slate-900 font-bold rounded-full px-8 h-12 text-base">
              <Play className="w-4 h-4 mr-2 fill-current" /> Run Demo
            </Button>
            <Button size="lg" variant="outline" className="border-slate-800 hover:bg-slate-800 text-white rounded-full px-8 h-12 text-base bg-transparent">
              Connect to DataHub
            </Button>
            <Button size="lg" variant="ghost" className="hover:bg-slate-800/50 text-slate-400 hover:text-white rounded-full px-6 h-12 text-base">
              <Github className="w-5 h-5 mr-2" /> View on GitHub
            </Button>
          </div>

          {/* Animated Agent Pipeline */}
          <div className="max-w-4xl mx-auto bg-slate-900/50 border border-slate-800/80 rounded-2xl p-8 backdrop-blur-sm">
            <div className="flex items-center justify-between relative">
              {agents.map((agent, i) => (
                <React.Fragment key={agent.name}>
                  {/* Node */}
                  <div className="relative z-10 flex flex-col items-center gap-3">
                    <div className={`w-16 h-16 rounded-xl flex items-center justify-center text-2xl transition-all duration-500 ${activeNode === i ? 'bg-cyan-900/40 border-2 border-cyan-400 shadow-[0_0_30px_rgba(34,211,238,0.2)] scale-110' : 'bg-slate-800 border border-slate-700'}`}>
                      {agent.emoji}
                    </div>
                    <span className={`text-sm font-medium transition-colors duration-500 ${activeNode === i ? 'text-cyan-400' : 'text-slate-400'}`}>
                      {agent.name}
                    </span>
                  </div>

                  {/* Connector */}
                  {i < agents.length - 1 && (
                    <div className="flex-1 h-0.5 mx-4 bg-slate-800 relative overflow-hidden">
                      <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400 to-transparent transition-opacity duration-300 ${activeNode === i ? 'opacity-100 animate-flow' : 'opacity-0'}`} />
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* "No DataHub? No problem." section */}
      <section className="bg-[#0a0e17] border-y border-slate-800/80 py-24">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">No DataHub? No problem.</h2>
          <p className="text-slate-400 max-w-2xl mx-auto mb-12">
            Run the agents against one of our pre-configured local SQLite datasets to see how Rosetta catches semantic drift.
          </p>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {/* Healthcare Card */}
            <div className="group text-left p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-cyan-500/50 hover:bg-cyan-950/20 transition-all duration-300 cursor-pointer">
              <div className="w-12 h-12 rounded-xl bg-slate-800 group-hover:bg-cyan-900/50 flex items-center justify-center mb-6 transition-colors">
                <Stethoscope className="w-6 h-6 text-slate-400 group-hover:text-cyan-400 transition-colors" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Healthcare Dataset</h3>
              <p className="text-slate-400 text-sm mb-6">Patient records, diagnosis codes, and billing anomalies.</p>
              <div className="flex items-center justify-between">
                <div className="text-xs font-mono text-slate-500">
                  <span className="text-slate-300">55,500</span> records<br/>
                  <span className="text-amber-400">4</span> conflicts injected
                </div>
                <Button size="sm" className="bg-slate-800 hover:bg-cyan-500 group-hover:bg-cyan-500 text-white group-hover:text-cyan-950 transition-all group-hover:shadow-[0_0_15px_rgba(34,211,238,0.4)]">
                  Load Demo
                </Button>
              </div>
            </div>

            {/* Retail Card */}
            <div className="group text-left p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-purple-500/50 hover:bg-purple-950/20 transition-all duration-300 cursor-pointer">
              <div className="w-12 h-12 rounded-xl bg-slate-800 group-hover:bg-purple-900/50 flex items-center justify-center mb-6 transition-colors">
                <ShoppingBag className="w-6 h-6 text-slate-400 group-hover:text-purple-400 transition-colors" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Retail Dataset</h3>
              <p className="text-slate-400 text-sm mb-6">E-commerce orders, inventory levels, and revenue discrepancies.</p>
              <div className="flex items-center justify-between">
                <div className="text-xs font-mono text-slate-500">
                  <span className="text-slate-300">150,000</span> orders<br/>
                  <span className="text-amber-400">2</span> conflicts injected
                </div>
                <Button size="sm" className="bg-slate-800 hover:bg-purple-500 group-hover:bg-purple-500 text-white group-hover:text-purple-950 transition-all group-hover:shadow-[0_0_15px_rgba(168,85,247,0.4)]">
                  Load Demo
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features + Sample Conflict Card */}
      <section className="py-24 max-w-6xl mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Catch semantic drift before it impacts reporting.</h2>
            
            <div className="grid sm:grid-cols-2 gap-8 mt-12">
              <div>
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mb-4 text-cyan-400">
                  <Play className="w-5 h-5 fill-current" />
                </div>
                <h4 className="font-bold text-white mb-2">Zero-config demo</h4>
                <p className="text-sm text-slate-400">Run entirely in your browser with bundled SQLite data. No setup required to see the agents in action.</p>
              </div>
              <div>
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mb-4 text-blue-400">
                  <Database className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white mb-2">DataHub-native</h4>
                <p className="text-sm text-slate-400">Connects directly to your DataHub instance via GraphQL to analyze real metadata relationships.</p>
              </div>
              <div>
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mb-4 text-amber-400">
                  <AlertCircle className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white mb-2">Blast-radius severity</h4>
                <p className="text-sm text-slate-400">Automatically traces downstream dashboards to score the business impact of each definition conflict.</p>
              </div>
              <div>
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mb-4 text-emerald-400">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white mb-2">One-click fixes</h4>
                <p className="text-sm text-slate-400">Broker agent proposes a canonical definition and writes it back to DataHub metadata automatically.</p>
              </div>
            </div>
          </div>

          {/* Terminal Card */}
          <div className="bg-[#0d1117] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden font-mono text-sm relative group">
            <div className="flex items-center px-4 py-3 bg-[#161b22] border-b border-slate-800">
              <div className="flex gap-2 mr-4">
                <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
              </div>
              <div className="text-slate-500 text-xs">rosetta-scan-results.json</div>
            </div>
            
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-rose-500" />
                  <span className="text-rose-500 font-bold">CRITICAL CONFLICT DETECTED</span>
                </div>
                <span className="text-slate-500">ID: CNFL-892</span>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-3 border-b border-slate-800 pb-4">
                  <div className="text-slate-500">Metric</div>
                  <div className="col-span-2 text-cyan-400">billing_amount</div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 pb-4 border-b border-slate-800">
                  <div className="bg-rose-950/20 p-4 rounded-xl border border-rose-900/30">
                    <div className="text-slate-500 text-xs mb-2">CLINICAL_TEAM</div>
                    <div className="text-rose-200">SUM(base_charge) + SUM(medication)</div>
                  </div>
                  <div className="bg-rose-950/20 p-4 rounded-xl border border-rose-900/30">
                    <div className="text-slate-500 text-xs mb-2">FINANCE_TEAM</div>
                    <div className="text-rose-200">SUM(base_charge) - SUM(discounts)</div>
                  </div>
                </div>

                <div className="grid grid-cols-3 py-2">
                  <div className="text-slate-500">Downstream Impact</div>
                  <div className="col-span-2 text-amber-400">1,215 rows / $28.5M variance</div>
                </div>

                <div className="bg-[#161b22] p-4 rounded-xl border border-slate-800 mt-6 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button size="sm" className="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 h-7 text-xs">
                      Approve Fix
                    </Button>
                  </div>
                  <div className="text-slate-500 text-xs mb-2 flex items-center gap-2">
                    <Sparkles className="w-3 h-3 text-emerald-400" /> Proposed Canonical Definition
                  </div>
                  <div className="text-emerald-400">
                    SUM(base_charge) + SUM(medication) - SUM(discounts)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* DataHub callout */}
      <section className="py-24 max-w-6xl mx-auto px-6">
        <div className="bg-gradient-to-br from-blue-900/40 to-indigo-900/40 border border-blue-500/20 rounded-3xl p-8 lg:p-12">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-block px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-sm font-medium mb-6">
                Native Integration
              </div>
              <h2 className="text-3xl font-bold text-white mb-4">Bring your own graph.</h2>
              <p className="text-blue-200/80 mb-8 leading-relaxed">
                Running DataHub in production? Point Rosetta at your GMS endpoint and let it trace lineage automatically. It uses your existing metadata graph to score downstream impact without needing access to underlying data.
              </p>
              <a href="#" className="inline-flex items-center text-blue-400 hover:text-blue-300 font-medium transition-colors">
                View Documentation <ArrowRight className="w-4 h-4 ml-2" />
              </a>
            </div>
            
            <div className="bg-[#0a0e17] rounded-xl border border-slate-800 p-4 font-mono text-sm shadow-xl">
              <div className="flex gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
              </div>
              <div className="text-slate-400 mb-2">$ export DATAHUB_GMS_URL="http://localhost:8080"</div>
              <div className="text-slate-400 mb-4">$ export DATAHUB_TOKEN="your_token_here"</div>
              <div className="text-slate-300 mb-4">$ rosetta scan --mode=datahub --full</div>
              <div className="text-slate-500 mb-1">&gt; Initializing Harvester Agent...</div>
              <div className="text-slate-500 mb-1">&gt; Connected to DataHub v0.12.1</div>
              <div className="text-blue-400 mb-1">&gt; Discovered 4,192 datasets</div>
              <div className="text-cyan-400 mb-1">&gt; Building lineage graph...</div>
              <div className="text-slate-500 animate-pulse">&gt; Scanning for semantic drift _</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-12 text-center text-slate-500 text-sm">
        <p>🪨 ROSETTA · Built for the DataHub Agent Hackathon · Open Source</p>
      </footer>
    </div>
  );
}
