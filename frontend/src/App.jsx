import React, { useState, useEffect } from 'react';
import { getPredictions, getCurrentWeather, getModelPerformance } from './api';
import ModelSection from './components/ModelSection';
import ModelAnalysis from './components/ModelAnalysis';
import Header from './components/Header';
import WeatherOverview from './components/WeatherOverview';
import PerformanceOverview from './components/PerformanceOverview';
import ControlBar from './components/ControlBar';
import { RefreshCw } from 'lucide-react';

const App = () => {
  const [data, setData] = useState({
    lstm: { data: [] },
    lgbm: { data: [] },
    actual: { data: [] },
    is_today: true
  });
  const [viewMode, setViewMode] = useState('forecast');
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [timeRange, setTimeRange] = useState(1); // 1, 3, 7 days
  const [selectedDate, setSelectedDate] = useState('');
  const [liveWeather, setLiveWeather] = useState(null);
  const [showComparison, setShowComparison] = useState(false);
  const [performanceData, setPerformanceData] = useState(null);

  const fetchLiveWeather = async () => {
    try {
      const weather = await getCurrentWeather();
      setLiveWeather(weather);
    } catch (err) {
      console.error("Live weather error:", err);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      if (viewMode === 'model') {
        const perf = await getModelPerformance();
        setPerformanceData(perf);
      } else {
        const response = await getPredictions(viewMode, timeRange, viewMode === 'past' ? selectedDate : null);
        setData(response);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const MIN_DATE = "2026-01-01";
  const MAX_DATE = new Date().toISOString().split('T')[0];

  const handleCustomDateChange = (e) => {
    const newDate = e.target.value;
    if (newDate < MIN_DATE || newDate > MAX_DATE) {
      return;
    }
    setSelectedDate(newDate);
    setTimeRange(1);
  };

  useEffect(() => {
    fetchLiveWeather();
    const interval = setInterval(fetchLiveWeather, 600000); // 10 mins
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchData();
  }, [viewMode, timeRange, selectedDate]);

  const handleSync = async () => {
    setSyncing(true);
    await fetchData();
    setTimeout(() => setSyncing(false), 1000);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
    });
  };

  const getComparisonData = () => {
    const lstmFiltered = data.lstm?.data || [];
    const lgbmFiltered = data.lgbm?.data || [];
    const actualFiltered = data.actual?.data || [];

    const map = new Map();
    lstmFiltered.forEach(item => {
      map.set(item.timestamp, { timestamp: item.timestamp, lstmPower: item.power });
    });
    lgbmFiltered.forEach(item => {
      if (map.has(item.timestamp)) {
        map.get(item.timestamp).lgbmPower = item.power;
      } else {
        map.set(item.timestamp, { timestamp: item.timestamp, lgbmPower: item.power });
      }
    });

    if (viewMode === 'past') {
      actualFiltered.forEach(item => {
        if (map.has(item.timestamp)) {
          map.get(item.timestamp).actualPower = item.power;
        } else {
          map.set(item.timestamp, { timestamp: item.timestamp, actualPower: item.power });
        }
      });
    }

    return Array.from(map.values()).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  };

  if (loading && !data.lstm.data.length) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw size={40} className="text-amber-500 animate-spin" />
          <p className="text-slate-400 font-black uppercase tracking-widest text-[10px]">Loading Analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 font-sans selection:bg-amber-500/30">
      <Header
        viewMode={viewMode}
        setViewMode={setViewMode}
        syncing={syncing}
        handleSync={handleSync}
        data={data}
        selectedDate={selectedDate}
        handleCustomDateChange={handleCustomDateChange}
        MIN_DATE={MIN_DATE}
        MAX_DATE={MAX_DATE}
      />

      {viewMode !== 'model' && (
        <WeatherOverview liveWeather={liveWeather} />
      )}

      {/* Section Divider with Label */}
      <div className="flex items-center gap-4 mb-6 opacity-80">
        <span className="text-[14px] font-black text-slate-100 uppercase tracking-[0.2em] whitespace-nowrap">
          {viewMode === 'forecast' ? 'Plant Operational Forecast' : (viewMode === 'past' ? 'Historical Performance Review' : 'Deep Analytics & Model Analysis')}
        </span>
        <div className="h-[2px] flex-1 bg-slate-800" />
      </div>

      {viewMode === 'model' && performanceData ? (
        <ModelAnalysis
          performanceData={performanceData}
          formatDate={formatDate}
        />
      ) : (
        <>
          <PerformanceOverview
            viewMode={viewMode}
            timeRange={timeRange}
            data={data}
          />

          <ControlBar
            viewMode={viewMode}
            timeRange={timeRange}
            setTimeRange={setTimeRange}
            data={data}
            showComparison={showComparison}
            setShowComparison={setShowComparison}
          />

          {showComparison ? (
            <div className="space-y-8">
              <ModelSection
                key={`comparison-${viewMode}`}
                title={viewMode === 'forecast' ? "FORECAST COMPARISON: DL vs ML " : "PERFORMANCE REVIEW: ACTUAL vs DL vs ML"}
                data={getComparisonData()}
                type="comparison"
                formatDate={formatDate}
                timeRange={timeRange}
              />
            </div>
          ) : (
            <div className={`grid grid-cols-1 ${viewMode === 'past' ? 'lg:grid-cols-3' : 'lg:grid-cols-2'} gap-6`}>
              {viewMode === 'past' && (
                <ModelSection
                  key="actual-view"
                  title="MEASURED GENERATION (ARCHIVAL GHI)"
                  data={data.actual.data}
                  formatDate={formatDate}
                  accentColor="#10b981"
                  timeRange={timeRange}
                />
              )}
              <ModelSection
                key="lstm-view"
                title={viewMode === 'forecast' ? "DL Model(LSTM) FORECAST" : "DL Model(LSTM) INFERENCE"}
                data={data.lstm.data}
                formatDate={formatDate}
                accentColor="#fbbf24"
                timeRange={timeRange}
              />
              <ModelSection
                key="lgbm-view"
                title={viewMode === 'forecast' ? "ML Model(LGBM) FORECAST" : "ML Model(LGBM) INFERENCE"}
                data={data.lgbm.data}
                formatDate={formatDate}
                accentColor="#3b82f6"
                timeRange={timeRange}
              />
            </div>
          )}
        </>
      )}
      

      <footer className="mt-8 text-center text-slate-600 text-[10px] uppercase tracking-widest font-bold">
        <p>© 2026 eAge Solar Analytics • Dual-Model Analysis LSTM & LGBM • Grid Management</p>
      </footer>
    </div>
  );
};

export default App;
