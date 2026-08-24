import React from 'react';
import StatCard from './StatCard';
import { Wind, Thermometer, Droplets } from 'lucide-react';

const WeatherOverview = ({ liveWeather }) => {
    return (
        <div className="mb-10 relative">
            <div className="absolute inset-0 bg-amber-500/5 rounded-3xl blur-3xl opacity-20 animate-pulse" />
            <div className="relative bg-slate-900/60 border-2 border-amber-500/20 rounded-3xl p-6 shadow-2xl backdrop-blur-md">
                <div className="flex items-center gap-4 mb-6">
                    <div className="h-2 w-2 rounded-full bg-amber-500 animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.8)]" />
                    <span className="text-[12px] font-black text-amber-500 uppercase tracking-[0.4em] italic">Current Weather Metrics (Live)</span>
                    <div className="h-[1px] flex-1 bg-gradient-to-r from-amber-500/20 to-transparent" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <StatCard
                        title="Real-Time Wind"
                        value={liveWeather ? `${liveWeather.wind_speed.toFixed(1)}` : '--'}
                        unit="km/h"
                        icon={<Wind size={20} className="text-amber-500" />}
                        small={true}
                        highlight={true}
                    />
                    <StatCard
                        title="Real-Time Temp"
                        value={liveWeather ? `${liveWeather.temperature.toFixed(1)}` : '--'}
                        unit="°C"
                        icon={<Thermometer size={20} className="text-amber-500" />}
                        small={true}
                        highlight={true}
                    />
                    <StatCard
                        title="Real-Time Humidity"
                        value={liveWeather ? `${liveWeather.humidity.toFixed(0)}` : '--'}
                        unit="%"
                        icon={<Droplets size={20} className="text-amber-500" />}
                        small={true}
                        highlight={true}
                    />
                </div>
            </div>
        </div>
    );
};

export default WeatherOverview;
