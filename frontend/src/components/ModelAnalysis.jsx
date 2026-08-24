import React, { useState } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    AreaChart, Area
} from 'recharts';
import { ChevronLeft, Brain, Cpu, TrendingUp, AlertCircle, Calendar, ArrowRight } from 'lucide-react';
import { getPredictions } from '../api';

const HourlyCalibrationTable = ({ date, data, onBack }) => {
    return (
        <div className="animate-in fade-in slide-in-from-right duration-500">
            <div className="p-4 bg-slate-950/50 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <button
                        onClick={onBack}
                        className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
                    >
                        <ChevronLeft size={18} />
                    </button>
                    <h2 className="text-[12px] font-black uppercase tracking-[0.2em] text-amber-500 italic">
                        {new Date(date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })} Calibration
                    </h2>
                </div>
            </div>
            <div className="p-4 overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr>
                            {['Time', 'Actual', 'ML Out', 'DL Out'].map(h => (
                                <th key={h} className="px-3 py-3 border-b border-slate-800 text-slate-500 font-black text-[9px] uppercase tracking-widest text-center">{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/30">
                        {data.lstm.data.map((item, idx) => {
                            const lgbmItem = data.lgbm.data.find(d => d.timestamp === item.timestamp) || {};
                            const actualItem = data.actual.data.find(d => d.timestamp === item.timestamp) || {};
                            return (
                                <tr key={idx} className="hover:bg-slate-800/40 text-[12px] transition-colors font-mono font-bold text-center">
                                    <td className="px-3 py-2.5 text-slate-400">{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                                    <td className="px-3 py-2.5 text-emerald-400">{(actualItem.power || 0).toFixed(3)}</td>
                                    <td className="px-3 py-2.5 text-blue-400">{(lgbmItem.power || 0).toFixed(3)}</td>
                                    <td className="px-3 py-2.5 text-amber-500">{(item.power || 0).toFixed(3)}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const ModelAnalysis = ({ performanceData }) => {
    const [drilldownDate, setDrilldownDate] = useState(null);
    const [drilldownData, setDrilldownData] = useState(null);
    const [activeModel, setActiveModel] = useState(null); // 'lstm' or 'lgbm'
    const [loadingDrilldown, setLoadingDrilldown] = useState(false);

    const handleRowClick = async (date, modelType) => {
        setLoadingDrilldown(true);
        setActiveModel(modelType);
        try {
            const data = await getPredictions('past', 1, date);
            setDrilldownDate(date);
            setDrilldownData(data);
        } catch (error) {
            console.error("Error fetching drilldown data:", error);
            setActiveModel(null);
        } finally {
            setLoadingDrilldown(false);
        }
    };

    const handleBack = () => {
        setDrilldownDate(null);
        setDrilldownData(null);
        setActiveModel(null);
    };

    // Data Processing: Filter for last 30 days
    const allData = performanceData.table_data;
    const last30Days = allData.slice(-30);

    // Error data: Yesterday and before (exclude today/tomorrow)
    const todayStr = new Date().toISOString().split('T')[0];
    const historicalOnly = last30Days.filter(d => d.date < todayStr);

    const summary = performanceData.summary;

    return (
        <div className="space-y-10 animate-in fade-in duration-700 pb-20">
            {/* Model Descriptions - FIXED SKEW AND ALIGNMENT */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 items-stretch">
                {/* DL Box */}
                <div className="flex flex-col relative group h-full">
                    <div className="absolute -inset-1 bg-gradient-to-r from-amber-600 to-amber-400 rounded-2xl blur opacity-5 group-hover:opacity-10 transition duration-1000"></div>
                    <div className="relative flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl flex flex-col justify-between">
                        <div>
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-3 bg-amber-500/10 rounded-xl border border-amber-500/20">
                                    <Brain className="text-amber-500" size={24} />
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">Deep Learning Architecture</span>
                                    <h3 className="text-2xl font-black text-white italic">LSTM Engine</h3>
                                </div>
                            </div>
                            <p className="text-[13px] text-slate-400 leading-relaxed mb-6 font-medium italic border-l-2 border-amber-500/30 pl-4">
                                {summary.lstm.description}
                            </p>
                        </div>
                        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 shadow-inner">
                            <span className="text-[9px] font-black text-amber-500 uppercase tracking-widest block mb-1">Cumulative Accuracy Mean</span>
                            <div className="flex items-baseline gap-1">
                                <span className="text-3xl font-black text-white tabular-nums">{summary.lstm.overall_accuracy.toFixed(1)}</span>
                                <span className="text-[10px] font-bold text-slate-500">%</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ML Box */}
                <div className="flex flex-col relative group h-full">
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-blue-400 rounded-2xl blur opacity-5 group-hover:opacity-10 transition duration-1000"></div>
                    <div className="relative flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl flex flex-col justify-between">
                        <div>
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
                                    <Cpu className="text-blue-500" size={24} />
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">Gradient Boosting Core</span>
                                    <h3 className="text-2xl font-black text-white italic">LGBM Regressor</h3>
                                </div>
                            </div>
                            <p className="text-[13px] text-slate-400 leading-relaxed mb-6 font-medium italic border-l-2 border-blue-500/30 pl-4">
                                {summary.lgbm.description}
                            </p>
                        </div>
                        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 shadow-inner">
                            <span className="text-[9px] font-black text-blue-500 uppercase tracking-widest block mb-1">Cumulative Accuracy Mean</span>
                            <div className="flex items-baseline gap-1">
                                <span className="text-3xl font-black text-white tabular-nums">{summary.lgbm.overall_accuracy.toFixed(1)}</span>
                                <span className="text-[10px] font-bold text-slate-500">%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Graphs Section */}
            <div className="grid grid-cols-1 gap-8">
                {/* 30-Day Power Generation Review */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-6 relative">
                        <div className="p-2.5 bg-emerald-500/10 rounded-lg">
                            <TrendingUp className="text-emerald-500" size={20} />
                        </div>
                        <div>
                            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Historical Analysis Review</h3>
                            <p className="text-xl font-black text-white italic">30-Day Global Power Yield (MW)</p>
                        </div>
                    </div>
                    <div className="h-[380px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={last30Days} margin={{ top: 10, right: 20, left: 0, bottom: 30 }}>
                                <defs>
                                    <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorLSTM" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.15} />
                                        <stop offset="95%" stopColor="#fbbf24" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    tickFormatter={(str) => new Date(str).toLocaleDateString([], { day: '2-digit', month: 'short' })}
                                    stroke="#475569"
                                    fontSize={10}
                                    fontWeight={800}
                                    tickMargin={10}
                                />
                                <YAxis stroke="#475569" fontSize={10} fontWeight={800} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#020617', border: '1px solid #1e293b', borderRadius: '12px' }}
                                    labelStyle={{ fontSize: '12px', fontWeight: 'black', marginBottom: '8px' }}
                                />
                                <Legend verticalAlign="top" height={50} iconType="circle" wrapperStyle={{ fontSize: '10px', fontWeight: 'black', textTransform: 'uppercase' }} />
                                <Area name="Actual" type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorActual)" />
                                <Area name="DL (LSTM)" type="monotone" dataKey="lstm" stroke="#fbbf24" strokeWidth={1.5} strokeDasharray="5 5" fillOpacity={1} fill="url(#colorLSTM)" />
                                <Line name="ML (LGBM)" type="monotone" dataKey="lgbm" stroke="#3b82f6" strokeWidth={1.5} dot={{ r: 2.5 }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Model Error Monitoring - NOW LINE CHART FOR CLARITY */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-6 relative">
                        <div className="p-2.5 bg-rose-500/10 rounded-lg">
                            <AlertCircle className="text-rose-500" size={20} />
                        </div>
                        <div>
                            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Temporal Error Delta</h3>
                            <p className="text-xl font-black text-white italic">Daily MAPE Analysis (Till Yesterday)</p>
                        </div>
                    </div>
                    <div className="h-[380px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                                data={historicalOnly.map(d => ({
                                    ...d,
                                    error_lstm: Math.max(0, 100 - d.accuracy_lstm),
                                    error_lgbm: Math.max(0, 100 - d.accuracy_lgbm)
                                }))}
                                margin={{ top: 10, right: 20, left: 0, bottom: 30 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    tickFormatter={(str) => new Date(str).toLocaleDateString([], { day: '2-digit', month: 'short' })}
                                    stroke="#475569"
                                    fontSize={10}
                                    fontWeight={800}
                                    tickMargin={10}
                                />
                                <YAxis stroke="#475569" fontSize={10} fontWeight={800} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#020617', border: '1px solid #1e293b', borderRadius: '12px' }}
                                />
                                <Legend verticalAlign="top" height={50} iconType="line" wrapperStyle={{ fontSize: '10px', fontWeight: 'black', textTransform: 'uppercase' }} />
                                <Line name="DL Error (%)" type="monotone" dataKey="error_lstm" stroke="#fbbf24" strokeWidth={2} dot={{ r: 3 }} />
                                <Line name="ML Error (%)" type="monotone" dataKey="error_lgbm" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Split Tables */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                {/* DL Table */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl min-h-[400px]">
                    <div className="p-5 bg-amber-500/5 border-b border-slate-800 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Brain className="text-amber-500" size={18} />
                            <h2 className="text-[12px] font-black uppercase tracking-[0.15em] text-white">LSTM Performance Log</h2>
                        </div>
                    </div>

                    {activeModel === 'lstm' && drilldownData ? (
                        <HourlyCalibrationTable
                            date={drilldownDate}
                            data={drilldownData}
                            onBack={handleBack}
                        />
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-slate-950/30">
                                        {['Date Profile', 'Actual (MW)', 'DL Pred', 'Accuracy %'].map(h => (
                                            <th key={h} className="px-5 py-4 text-slate-500 font-black text-[9px] uppercase tracking-widest">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/20">
                                    {[...last30Days].reverse().map((day, idx) => (
                                        <tr key={idx} onClick={() => handleRowClick(day.date, 'lstm')} className="group hover:bg-amber-500/5 cursor-pointer transition-all duration-200">
                                            <td className="px-5 py-4 font-black text-[12px] text-slate-300 font-mono tracking-tight group-hover:text-amber-500 uppercase">{new Date(day.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}</td>
                                            <td className="px-5 py-4 text-[13px] font-bold text-emerald-400 font-mono">{(day.actual || 0).toFixed(3)}</td>
                                            <td className="px-5 py-4 text-[13px] font-bold text-amber-500 font-mono">{(day.lstm || 0).toFixed(3)}</td>
                                            <td className="px-5 py-4 flex items-center justify-between">
                                                <span className={`text-[13px] font-black tabular-nums ${day.accuracy_lstm > 90 ? 'text-emerald-500' : 'text-amber-500'}`}>
                                                    {day.accuracy_lstm.toFixed(1)}%
                                                </span>
                                                <ArrowRight size={12} className="text-slate-700 opacity-0 group-hover:opacity-100 transition-all" />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* ML Table */}
                <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl min-h-[400px]">
                    <div className="p-5 bg-blue-500/5 border-b border-slate-800 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Cpu className="text-blue-500" size={18} />
                            <h2 className="text-[12px] font-black uppercase tracking-[0.15em] text-white">LGBM Performance Log</h2>
                        </div>
                    </div>

                    {activeModel === 'lgbm' && drilldownData ? (
                        <HourlyCalibrationTable
                            date={drilldownDate}
                            data={drilldownData}
                            onBack={handleBack}
                        />
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-slate-950/30">
                                        {['Date Profile', 'Actual (MW)', 'ML Pred', 'Accuracy %'].map(h => (
                                            <th key={h} className="px-5 py-4 text-slate-500 font-black text-[9px] uppercase tracking-widest">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/20">
                                    {[...last30Days].reverse().map((day, idx) => (
                                        <tr key={idx} onClick={() => handleRowClick(day.date, 'lgbm')} className="group hover:bg-blue-500/5 cursor-pointer transition-all duration-200">
                                            <td className="px-5 py-4 font-black text-[12px] text-slate-300 font-mono tracking-tight group-hover:text-blue-500 uppercase">{new Date(day.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}</td>
                                            <td className="px-5 py-4 text-[13px] font-bold text-emerald-400 font-mono">{(day.actual || 0).toFixed(3)}</td>
                                            <td className="px-5 py-4 text-[13px] font-bold text-blue-400 font-mono">{(day.lgbm || 0).toFixed(3)}</td>
                                            <td className="px-5 py-4 flex items-center justify-between">
                                                <span className={`text-[13px] font-black tabular-nums ${day.accuracy_lgbm > 90 ? 'text-emerald-500' : 'text-blue-500'}`}>
                                                    {day.accuracy_lgbm.toFixed(1)}%
                                                </span>
                                                <ArrowRight size={12} className="text-slate-700 opacity-0 group-hover:opacity-100 transition-all" />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ModelAnalysis;
