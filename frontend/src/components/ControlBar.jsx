import React from 'react';
import { Calendar, Activity } from 'lucide-react';

const ControlBar = ({
    viewMode,
    timeRange,
    setTimeRange,
    data,
    showComparison,
    setShowComparison
}) => {
    return (
        <div className="flex flex-col lg:flex-row justify-between items-center mb-6 gap-4 bg-slate-900/40 p-3 rounded-2xl border border-slate-800/60 backdrop-blur-sm">
            <div className="flex flex-wrap items-center gap-4">
                {viewMode === 'past' && (
                    <div className="flex items-center gap-3">
                        <div className="flex bg-slate-800/80 p-1 rounded-lg border border-slate-700">
                            {[1, 3, 7].map(r => (
                                <button
                                    key={r}
                                    onClick={() => setTimeRange(r)}
                                    className={`px-4 py-1.5 rounded-md text-[10px] font-black uppercase transition-all ${timeRange === r ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    {r} Day
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {viewMode === 'forecast' && (
                    <div className="flex items-center gap-3 bg-slate-800/80 px-5 py-2.5 rounded-lg border border-slate-700 animate-in fade-in slide-in-from-left duration-500">
                        <Calendar size={22} className="text-amber-500" />
                        <div className="flex flex-col leading-tight">
                            <span className="text-[10px] font-black text-amber-500/80 uppercase tracking-[0.2em] italic">Forecast Target</span>
                            <span className="text-lg font-black text-white uppercase tracking-tight">{data.target_date_label}</span>
                        </div>
                    </div>
                )}

                <button
                    onClick={() => setShowComparison(!showComparison)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all text-[10px] font-black uppercase tracking-widest ${showComparison ? 'bg-amber-500/10 border-amber-500 text-amber-500' : 'bg-slate-800/80 border-slate-700 text-slate-500 hover:text-slate-300'}`}
                >
                    <Activity size={14} />
                    {showComparison ? "Comparative ON" : "Normal View"}
                </button>
            </div>

            <div className="hidden lg:block text-[12px] font-bold text-slate-600 uppercase tracking-[0.2em]">
                {viewMode === 'forecast' ? `Plant Operational Forecast` : `Historical Performance Review`}
            </div>
        </div>
    );
};

export default ControlBar;
