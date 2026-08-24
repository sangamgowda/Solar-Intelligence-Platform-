import React from 'react';
import { Sun, Calendar, Activity, Database, Layers, RefreshCw } from 'lucide-react';

const Header = ({
    viewMode,
    setViewMode,
    syncing,
    handleSync,
    data,
    selectedDate,
    handleCustomDateChange,
    MIN_DATE,
    MAX_DATE
}) => {
    return (
        <header className="flex flex-col lg:flex-row justify-between items-center mb-10 gap-6">
            <div className="flex items-center gap-6">
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-amber-600 to-amber-400 rounded-full blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                    <div className="relative bg-slate-900 p-4 rounded-full border border-slate-700/50 shadow-2xl">
                        <Sun className="text-amber-500" size={32} />
                    </div>
                </div>
                <div>
                    <h1 className="text-4xl font-black tracking-tighter text-white">
                        URJA <span className="text-amber-500">SETU</span>
                    </h1>
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.3em] mt-1 italic leading-tight">
                        Enterprise Solar Intelligence Platform
                    </p>
                </div>
            </div>

            <div className="flex flex-col md:flex-row items-center gap-4">
                <div className="flex flex-wrap items-center justify-center gap-4">
                    {viewMode === 'forecast' ? (
                        <div className="flex items-center gap-3 bg-slate-900/80 px-4 py-2.5 rounded-xl border border-slate-800 shadow-lg animate-in fade-in slide-in-from-right duration-500">
                            <Calendar size={20} className="text-amber-500" />
                            <div className="flex flex-col leading-tight">
                                <span className="text-[9px] font-black text-amber-500/60 uppercase tracking-widest italic">Forecast Target</span>
                                <span className="text-sm font-black text-white uppercase">{data.target_date_label}</span>
                            </div>
                        </div>
                    ) : viewMode === 'past' ? (
                        <div className="flex items-center gap-3 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800 shadow-lg">
                            <div className="pl-2 border-r border-slate-800 pr-2">
                                <Calendar size={18} className="text-slate-500" />
                            </div>
                            <input
                                type="date"
                                value={selectedDate || data.target_date_iso || ''}
                                min={MIN_DATE}
                                max={MAX_DATE}
                                onChange={handleCustomDateChange}
                                className="bg-transparent px-2 py-0.5 text-[18px] font-black text-slate-200 focus:outline-none focus:text-amber-500 transition-colors uppercase cursor-pointer"
                            />
                        </div>
                    ) : null}

                    <div className="relative flex bg-slate-900 border border-slate-800 p-1 rounded-xl w-[420px] h-[52px] shadow-inner">
                        <div
                            className="absolute top-1 bottom-1 transition-all duration-300 ease-in-out bg-amber-500 rounded-lg shadow-lg shadow-amber-500/30"
                            style={{
                                left: viewMode === 'forecast' ? '4px' : (viewMode === 'past' ? 'calc(33.33% + 2px)' : 'calc(66.66% + 2px)'),
                                width: 'calc(33.33% - 5px)'
                            }}
                        />
                        <button
                            onClick={() => setViewMode('forecast')}
                            className={`relative z-10 flex-1 text-[10px] font-black uppercase transition-colors duration-300 flex items-center justify-center gap-2 ${viewMode === 'forecast' ? 'text-slate-950' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            <Activity size={14} /> Forecast
                        </button>
                        <button
                            onClick={() => setViewMode('past')}
                            className={`relative z-10 flex-1 text-[10px] font-black uppercase transition-colors duration-300 flex items-center justify-center gap-2 ${viewMode === 'past' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            <Database size={14} /> Performance
                        </button>
                        <button
                            onClick={() => setViewMode('model')}
                            className={`relative z-10 flex-1 text-[10px] font-black uppercase transition-colors duration-300 flex items-center justify-center gap-2 ${viewMode === 'model' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            <Layers size={14} /> Model Analytics
                        </button>
                    </div>

                    <button
                        onClick={handleSync}
                        className="p-3 bg-slate-900 border border-slate-700 text-slate-400 hover:text-amber-500 hover:border-amber-500/50 rounded-xl transition-all active:scale-95 shadow-lg"
                    >
                        <RefreshCw size={18} className={syncing ? "animate-spin" : ""} />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
