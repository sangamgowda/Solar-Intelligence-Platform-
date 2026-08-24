import React from 'react';
import StatCard from './StatCard';
import { Sun, Battery, Activity } from 'lucide-react';

const PerformanceOverview = ({ viewMode, timeRange, data }) => {
    return (
        <div className={`grid grid-cols-1 md:grid-cols-2 ${viewMode === 'past' ? 'lg:grid-cols-3' : 'lg:grid-cols-2'} gap-4 mb-8`}>
            {viewMode === 'past' && (
                <StatCard
                    title={timeRange === 1 ? `Actual Recorded Yield (${data.target_date_label})` : "Total Aggregated Yield"}
                    value={`${(data.actual.summary_mwh || 0).toFixed(3)} MWh`}
                    icon={<Sun className="text-emerald-400" />}
                    trend={timeRange === 1 ? "Archive Ground Truth" : `Performance over past ${timeRange} days`}
                    highlight={true}
                    variant="green"
                />
            )}
            <StatCard
                title={viewMode === 'forecast' ? "Deep Learning Model Prediction" : (timeRange === 1 ? `Deep Learning Model Prediction (${data.target_date_label})` : "Deep Learning Model Total Aggregated")}
                value={`${(data.lstm.summary_mwh || 0).toFixed(3)} MWh`}
                icon={<Battery className="text-amber-400" />}
                trend={viewMode === 'forecast' ? `Next 24h Prediction` : `Performance over past ${timeRange} days`}
                highlight={true}
            />
            <StatCard
                title={viewMode === 'forecast' ? "Machine Learning Model Prediction" : (timeRange === 1 ? `Machine Learning Model Prediction (${data.target_date_label})` : "Machine Learning Model Total Aggregated")}
                value={`${(data.lgbm.summary_mwh || 0).toFixed(3)} MWh`}
                icon={<Activity className="text-blue-400" />}
                trend={viewMode === 'forecast' ? `Next 24h Prediction` : `Performance over past ${timeRange} days`}
                highlight={true}
                variant="blue"
            />
        </div>
    );
};

export default PerformanceOverview;
