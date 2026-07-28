import React from 'react';
import { 
  Play, 
  Database, 
  ShoppingBag, 
  ShieldAlert, 
  GitMerge, 
  FileCheck, 
  Search, 
  Activity, 
  ArrowRight, 
  Zap, 
  CheckCircle2,
  AlertOctagon,
  TrendingDown
} from 'lucide-react';

export default function ValueLed() {
  return (
    <div className="min-h-screen bg-[#0a0e1a] text-slate-200 font-sans selection:bg-cyan-500/30 overflow-x-hidden relative">
      {/* Background glow effects */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-900/20 blur-[120px] pointer-events-none" />
      <div className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-900/20 blur-[120px] pointer-events-none" />
      
      {/* 1. Nav */}
      <header className="container mx-auto px-6 py-6 flex items-center justify-between relative z-10 border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🪨</span>
          <span className="text-xl font-bold tracking-tight text-white">Rosetta</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          <a href="#how-it-works" className="hover:text-white transition-colors">How it works</a>
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#datahub" className="hover:text-white transition-colors">Connect to DataHub</a>
        </nav>
        <button className="hidden md:flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2 rounded-md transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)]">
          <Play className="w-4 h-4 fill-current" />
          Run Demo
        </button>
      </header>

      <main className="container mx-auto px-6 relative z-10 pt-20 pb-24">
        
        {/* Hero Section */}
        <div className="flex flex-col items-center text-center max-w-4xl mx-auto space-y-8">
          {/* 2. Badge pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-semibold tracking-wide uppercase">
            <Zap className="w-3 h-3" />
            DataHub Agent Hackathon 2026
          </div>
          
          {/* 3. Hero headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight leading-[1.1]">
            Your teams define the same metric differently.<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              Rosetta finds where — before it costs you.
            </span>
          </h1>
          
          {/* 4. Sub-headline */}
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl leading-relaxed">
            Five AI agents run on your DataHub metadata graph to detect semantic conflicts. Stop silent disagreements from reaching your revenue reports.
          </p>
          
          {/* 5. CTA row */}
          <div className="flex flex-col sm:flex-row items-center gap-4 pt-4">
            <button className="flex items-center justify-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-8 py-3 rounded-md transition-all shadow-[0_0_20px_rgba(6,182,212,0.4)] w-full sm:w-auto text-lg">
              <Play className="w-5 h-5 fill-current" />
              Run Demo
            </button>
            <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium px-6 py-3 rounded-md transition-all w-full sm:w-auto">
              <Activity className="w-5 h-5 text-rose-400" />
              Scan Healthcare Data
            </button>
            <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium px-6 py-3 rounded-md transition-all w-full sm:w-auto">
              <ShoppingBag className="w-5 h-5 text-amber-400" />
              Scan Retail Data
            </button>
          </div>
        </div>

        {/* 6. Product preview card */}
        <div className="mt-20 max-w-5xl mx-auto rounded-2xl bg-white p-6 md:p-8 shadow-2xl shadow-cyan-900/20 transform md:-rotate-1 hover:rotate-0 transition-transform duration-500 relative">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-cyan-50/50 to-transparent rounded-2xl pointer-events-none" />
          
          <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-rose-500" />
              <h3 className="text-slate-800 font-bold text-lg">Conflict Detected: <code className="bg-slate-100 px-2 py-1 rounded text-cyan-700 font-mono text-sm ml-1">billing_amount</code></h3>
            </div>
            <div className="bg-rose-100 text-rose-700 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
              <AlertOctagon className="w-3 h-3" />
              CRITICAL
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Team 1 */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 relative">
              <div className="absolute top-4 right-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Clinical Team</div>
              <h4 className="text-slate-900 font-bold mb-3 flex items-center gap-2">
                <Database className="w-4 h-4 text-indigo-500" />
                Raw Encounter Data
              </h4>
              <p className="text-sm text-slate-600 mb-4">
                "Total billed for the encounter, <span className="font-semibold text-slate-900">including negative values</span> for credits, adjustments, and billing errors."
              </p>
              <div className="bg-white border border-slate-100 rounded-md p-3 font-mono text-xs text-slate-700 overflow-x-auto shadow-sm whitespace-pre">
                SELECT SUM(amount) AS billing_amount{"\n"}FROM encounters
              </div>
            </div>

            {/* Team 2 */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 relative">
              <div className="absolute top-4 right-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Finance Team</div>
              <h4 className="text-slate-900 font-bold mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-500" />
                Revenue Mart
              </h4>
              <p className="text-sm text-slate-600 mb-4">
                "Recognized revenue for the period. <span className="font-semibold text-slate-900">Must always be strictly positive.</span> Negative values invalidate the report."
              </p>
              <div className="bg-white border border-slate-100 rounded-md p-3 font-mono text-xs text-slate-700 overflow-x-auto shadow-sm whitespace-pre">
                SELECT SUM(amount) AS billing_amount{"\n"}FROM revenue_events{"\n"}WHERE amount {'>'} 0
              </div>
            </div>
          </div>

          <div className="flex flex-col md:flex-row items-center gap-6 mb-6">
            <div className="flex-1 bg-amber-50 border border-amber-200 rounded-xl p-5 w-full">
              <h4 className="text-amber-800 font-bold text-sm uppercase tracking-wide mb-1 flex items-center gap-2">
                <TrendingDown className="w-4 h-4" /> Blast Radius
              </h4>
              <p className="text-amber-900 text-lg font-medium">
                1,215 negative rows silently reached the revenue mart
              </p>
              <p className="text-amber-700 text-sm mt-1">
                <strong>$28.5M</strong> in potentially misreported revenue at risk.
              </p>
            </div>
          </div>

          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-5">
            <h4 className="text-indigo-900 font-bold text-sm uppercase tracking-wide mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> Proposed Fix by Rosetta
            </h4>
            <div className="text-sm text-indigo-800 space-y-2">
              <p>1. Standardize <code>billing_amount</code> definition across both domains.</p>
              <p>2. Create a new metric <code>net_recognized_revenue</code> for the Finance Team that explicitly handles credits.</p>
              <p>3. Add data contract to Clinical Team's pipeline: <code>assert billing_amount {'>='} 0</code>.</p>
            </div>
            <div className="mt-4 flex gap-3">
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm">
                Apply Fixes to DataHub
              </button>
              <button className="bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-50 px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm">
                View Full Audit Trace
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* 7. How it works strip */}
      <section id="how-it-works" className="py-24 bg-[#050813] border-y border-white/5 relative z-10">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Five Agents. Zero Blind Spots.</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">Rosetta orchestrates a crew of specialized AI agents that autonomously crawl your metadata graph to find semantic conflicts.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {[
              { num: "01", icon: <Search className="w-6 h-6 text-cyan-400" />, title: "Harvester", desc: "Crawls DataHub to build a semantic map of metrics." },
              { num: "02", icon: <ShieldAlert className="w-6 h-6 text-rose-400" />, title: "Conflict Detector", desc: "Identifies contradictions in human-written definitions." },
              { num: "03", icon: <Activity className="w-6 h-6 text-amber-400" />, title: "Blast-Radius", desc: "Traces lineage to calculate the business impact." },
              { num: "04", icon: <GitMerge className="w-6 h-6 text-indigo-400" />, title: "Broker", desc: "Negotiates a canonical definition between teams." },
              { num: "05", icon: <FileCheck className="w-6 h-6 text-emerald-400" />, title: "Writer", desc: "Commits standardized metadata back to DataHub." }
            ].map((step, i) => (
              <div key={i} className="bg-white/5 border border-white/5 rounded-xl p-6 hover:bg-white/10 transition-colors group">
                <div className="text-slate-600 font-mono text-sm font-bold mb-4">{step.num}</div>
                <div className="mb-4 p-3 bg-white/5 rounded-lg inline-block group-hover:scale-110 transition-transform">
                  {step.icon}
                </div>
                <h3 className="text-white font-bold text-lg mb-2">{step.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 8. Features grid */}
      <section id="features" className="py-24 relative z-10">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center">
                <Database className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white">Connects to DataHub</h3>
              <p className="text-slate-400 leading-relaxed">
                Native integration with LinkedIn's open-source metadata catalog. Rosetta reads your existing lineage and writes back standardized glossary terms.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="w-12 h-12 bg-cyan-500/10 border border-cyan-500/20 rounded-xl flex items-center justify-center">
                <Search className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="text-xl font-bold text-white">Evidence-Driven</h3>
              <p className="text-slate-400 leading-relaxed">
                Conflicts aren't guessed. Rosetta analyzes actual dbt models, SQL queries, and textual descriptions to prove exactly where definitions diverge.
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="text-xl font-bold text-white">Instant Fix Proposals</h3>
              <p className="text-slate-400 leading-relaxed">
                Don't just find problems. Rosetta generates ready-to-merge data contracts and glossary updates to resolve conflicts permanently.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 9. DataHub callout */}
      <section id="datahub" className="py-24 bg-gradient-to-b from-[#0a0e1a] to-[#050813] relative z-10 border-t border-white/5">
        <div className="container mx-auto px-6 max-w-5xl">
          <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-500/20 rounded-3xl p-8 md:p-12 flex flex-col md:flex-row items-center gap-10 shadow-2xl">
            <div className="flex-1 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-400/30 bg-blue-500/10 text-blue-300 text-xs font-semibold tracking-wide uppercase">
                Native Integration
              </div>
              <h2 className="text-3xl md:text-4xl font-bold text-white">Bring your own graph.</h2>
              <p className="text-slate-300 text-lg">
                Rosetta talks directly to your live DataHub instance via GraphQL and REST APIs. Point it at your host, provide a token, and let the agents loose on your metadata.
              </p>
              <button className="flex items-center gap-2 text-cyan-400 font-semibold hover:text-cyan-300 transition-colors group">
                View Documentation <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
            <div className="flex-1 w-full bg-[#0a0e1a] rounded-xl border border-white/10 p-4 font-mono text-sm text-slate-300 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-500" />
              <div className="flex gap-2 mb-4 mt-2">
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
              </div>
              <div className="space-y-2">
                <div className="text-slate-500"># Connect Rosetta to DataHub</div>
                <div><span className="text-cyan-400">export</span> DATAHUB_GMS_URL=<span className="text-emerald-400">"http://localhost:8080"</span></div>
                <div><span className="text-cyan-400">export</span> DATAHUB_TOKEN=<span className="text-emerald-400">"eyJhbG..."</span></div>
                <br/>
                <div className="text-slate-500"># Run the semantic conflict scanner</div>
                <div><span className="text-blue-400">rosetta</span> scan --domain healthcare --auto-fix</div>
                <br/>
                <div className="text-slate-400">✨ Initializing Harvester Agent...</div>
                <div className="text-slate-400">🔍 Analyzing 1,420 dataset entities...</div>
                <div className="text-rose-400">⚠️ Found 3 high-severity semantic conflicts.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 10. Footer */}
      <footer className="py-12 border-t border-white/5 bg-[#050813] relative z-10 text-center">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="text-xl">🪨</span>
            <span className="text-lg font-bold tracking-tight text-white">Rosetta</span>
          </div>
          <p className="text-slate-500 text-sm">Built for the DataHub Agent Hackathon 2026 · Open Source</p>
        </div>
      </footer>
    </div>
  );
}
