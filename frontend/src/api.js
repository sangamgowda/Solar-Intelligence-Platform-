import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
});

export const getPredictions = async (viewMode = 'forecast', rangeDays = 1, date = null) => {
    const params = { view_mode: viewMode, range_days: rangeDays };
    if (date) params.date = date;
    const response = await api.get('/predictions', { params });
    return response.data;
};

export const getCurrentWeather = async () => {
    const response = await api.get('/current-weather');
    return response.data;
};

export const triggerPrediction = async (date) => {
    const response = await api.post(`/trigger-day?date=${date}`);
    return response.data;
};

export const getStatus = async () => {
    const response = await api.get('/status');
    return response.data;
};

export const getModelPerformance = async () => {
    const response = await api.get('/analytics/model-performance');
    return response.data;
};

export default api;
