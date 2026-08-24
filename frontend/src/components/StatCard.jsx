import React from 'react';

const StatCard = ({ title, value, unit, icon, trend, highlight, variant, extra, small }) => (
    <div className={`rounded-2xl border flex flex-col shadow-xl transition-all duration-300 ${small ? 'p-5 bg-slate-900/60 border-slate-800/80 justify-center h-full' : 'p-6 bg-slate-900/50 border-slate-800'} ${highlight ? (variant === 'blue' ? 'bg-blue-500/5 border-blue-500/20 ring-1 ring-blue-500/10' : (variant === 'green' ? 'bg-emerald-500/5 border-emerald-500/20 ring-1 ring-emerald-500/10' : 'bg-amber-500/5 border-amber-500/20 ring-1 ring-amber-500/10')) : ''}`}>
        <div className={`flex justify-between items-start ${small ? 'mb-2' : 'mb-2'}`}>
            <div className="flex flex-col">
                <span className={`font-black uppercase tracking-[0.2em] ${small ? 'text-[10px] text-slate-400' : 'text-[10px] ' + (variant === 'blue' ? 'text-blue-500' : (variant === 'green' ? 'text-emerald-500' : 'text-amber-500'))}`}>{title}</span>
                {!small && <span className="text-[10px] text-slate-500 uppercase font-black tracking-wider mt-2">{trend}</span>}
            </div>
            <div className={`rounded-xl ${small ? 'p-2 bg-slate-800/50 scale-110 shadow-inner' : 'p-2 ' + (variant === 'blue' ? 'bg-blue-500/10' : (variant === 'green' ? 'bg-emerald-500/10' : 'bg-amber-500/10'))}`}>{icon}</div>
        </div>
        <div className="flex flex-col">
            <div className="flex items-baseline gap-2">
                <span className={`${small ? 'text-3xl font-black' : 'text-3xl font-black'} font-mono tracking-tighter ${highlight ? (variant === 'blue' ? 'text-blue-500' : (variant === 'green' ? 'text-emerald-500' : 'text-amber-500')) : 'text-white'}`}>{value}</span>
                {small && <span className="text-[11px] font-bold text-slate-500 italic uppercase">{unit}</span>}
            </div>
        </div>
        {extra}
    </div>
);

export default StatCard;
