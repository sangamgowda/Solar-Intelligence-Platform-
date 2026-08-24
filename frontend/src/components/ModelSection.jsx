import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts';

const ModelSection = ({ title, data, formatDate, accentColor, type, timeRange }) => {
    const [view, setView] = useState('chart');

    useEffect(() => {
        if (type === 'comparison') setView('chart');
    }, [type]);

    return (
        <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-full">
            <div className="flex items-center justify-between p-4 border-b border-slate-800">
                <h2 className="text-[10px] font-black uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    {title}
                </h2>
                {type !== 'comparison' && (
                    <div className="flex bg-slate-800 p-1 rounded-lg">
                        {['chart', 'table'].map(v => (
                            <button
                                key={v}
                                onClick={() => setView(v)}
                                className={`px-3 py-1 rounded-md text-[9px] font-bold uppercase transition-all ${view === v ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
                            >
                                {v}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <div className="p-4 flex-1">
                {view === 'chart' ? (
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            {type === 'comparison' ? (
                                <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" vertical={false} />
                                    <XAxis
                                        dataKey="timestamp"
                                        label={{ value: 'Time (HH:mm)', position: 'insideBottom', offset: -15, fill: '#64748b', fontSize: 10, fontWeight: 800 }}
                                        tickFormatter={(tick) => {
                                            const date = new Date(tick);
                                            // 1 Day view: Show only every 3 hours 
                                            if (timeRange === 1) {
                                                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                                            }
                                            // 3+ Days: Show ONLY the date/day name when hour is 0
                                            return date.getHours() === 0
                                                ? date.toLocaleDateString([], { day: '2-digit', month: 'short' })
                                                : '';
                                        }}
                                        stroke="#94a3b8"
                                        fontSize={10}
                                        tick={{ fill: '#94a3b8', fontWeight: 600 }}
                                        interval={timeRange === 1 ? 2 : (timeRange === 3 ? 5 : 11)}
                                        minTickGap={30}
                                        height={50}
                                    />
                                    <YAxis
                                        stroke="#94a3b8"
                                        fontSize={11}
                                        tick={{ fill: '#94a3b8', fontWeight: 600 }}
                                        label={{ value: 'Power (MW)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10, fontWeight: 800 }}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                                        labelFormatter={formatDate}
                                    />
                                    <Legend verticalAlign="top" iconType="circle" />
                                    <Line name="DL Model Power (MW)" type="monotone" dataKey="lstmPower" stroke="#fbbf24" strokeWidth={1.5} dot={false} animationDuration={1100} />
                                    <Line name="ML Model Power (MW)" type="monotone" dataKey="lgbmPower" stroke="#3b82f6" strokeWidth={1.5} dot={false} animationDuration={1100} />
                                    {data[0]?.actualPower !== undefined && (
                                        <Line name="Actual Power (MW)" type="monotone" dataKey="actualPower" stroke="#10b981" strokeWidth={1.5} dot={false} animationDuration={1100} />
                                    )}
                                </LineChart>
                            ) : (
                                <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
                                    <defs>
                                        <linearGradient id={`color${title.replace(/\s+/g, '')}`} x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor={accentColor} stopOpacity={0.2} />
                                            <stop offset="95%" stopColor={accentColor} stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" vertical={false} />
                                    <XAxis
                                        dataKey="timestamp"
                                        label={{ value: 'Time (HH:mm)', position: 'insideBottom', offset: -15, fill: '#64748b', fontSize: 10, fontWeight: 800 }}
                                        tickFormatter={(tick) => {
                                            const date = new Date(tick);
                                            if (timeRange === 1) {
                                                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                                            }
                                            return date.getHours() === 0
                                                ? date.toLocaleDateString([], { day: '2-digit', month: 'short' })
                                                : '';
                                        }}
                                        stroke="#94a3b8"
                                        fontSize={10}
                                        tick={{ fill: '#94a3b8', fontWeight: 600 }}
                                        interval={timeRange === 1 ? 2 : (timeRange === 3 ? 5 : 11)}
                                        minTickGap={30}
                                        height={50}
                                    />
                                    <YAxis
                                        stroke="#94a3b8"
                                        fontSize={11}
                                        tick={{ fill: '#94a3b8', fontWeight: 600 }}
                                        tickFormatter={(v) => Number(v).toFixed(4)}
                                        label={{ value: 'Power (MW)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10, fontWeight: 800 }}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                                        labelFormatter={formatDate}
                                        formatter={(value) => Number(value).toFixed(4)}
                                    />
                                    <Area name="Power (MW)" type="monotone" dataKey="power" stroke={accentColor} strokeWidth={1.5} fill={`url(#color${title.replace(/\s+/g, '')})`} animationDuration={1100} />
                                </AreaChart>
                            )}
                        </ResponsiveContainer>
                    </div>
                ) : (
                    <div className="overflow-x-auto overflow-y-auto max-h-[300px]">
                        <table className="w-full text-left border-collapse">
                            <thead className="sticky top-0 bg-slate-900 z-10">
                                <tr>
                                    {['Time', 'T', 'H', 'W', 'GHI', 'P'].map(h => (
                                        <th key={h} className="px-2 py-2 border-b border-slate-800 text-slate-500 font-bold text-[9px] uppercase tracking-widest">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/30">
                                {[...data].reverse().map((item, idx) => (
                                    <tr key={idx} className="hover:bg-slate-800/20 text-[10px] transition-colors">
                                        <td className="px-2 py-2 text-slate-400 font-mono whitespace-nowrap">{formatDate(item.timestamp)}</td>
                                        <td className="px-2 py-2">{(item.temperature || 0).toFixed(0)}</td>
                                        <td className="px-2 py-2">{(item.humidity || 0).toFixed(0)}</td>
                                        <td className="px-2 py-2">{(item.wind_speed || 0).toFixed(0)}</td>
                                        <td className="px-2 py-2 text-amber-500/80">{(item.ghi || 0).toFixed(0)}</td>
                                        <td className="px-2 py-2">
                                            <span className={`px-1 rounded font-mono font-bold ${accentColor === '#3b82f6' ? 'text-blue-500' : (accentColor === '#10b981' ? 'text-emerald-500' : 'text-amber-500')}`}>
                                                {(item.power || 0).toFixed(3)}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ModelSection;
