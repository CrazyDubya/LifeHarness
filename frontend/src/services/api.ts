import axios from 'axios';
import type {
  User,
  Profile,
  Thread,
  StepResponse,
  Answer,
  LifeEntry,
  CoverageCell,
  AutobiographyRequest,
  Autobiography,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const authApi = {
  register: async (email: string, password: string) => {
    const response = await api.post('/auth/register', { email, password });
    return response.data;
  },
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
};

// Profile
export const profileApi = {
  get: async (): Promise<Profile> => {
    const response = await api.get('/profile');
    return response.data;
  },
  upsert: async (data: Partial<Profile>): Promise<Profile> => {
    const response = await api.post('/profile', data);
    return response.data;
  },
};

// Threads
export const threadsApi = {
  list: async (): Promise<Thread[]> => {
    const response = await api.get('/threads');
    return response.data;
  },
  create: async (data: {
    title: string;
    root_prompt: string;
    time_focus?: string[];
    topic_focus?: string[];
  }): Promise<Thread> => {
    const response = await api.post('/threads', data);
    return response.data;
  },
  get: async (id: string): Promise<Thread> => {
    const response = await api.get(`/threads/${id}`);
    return response.data;
  },
  step: async (id: string, data: {
    last_answer?: Answer;
    control: 'continue' | 'stop';
  }): Promise<StepResponse> => {
    const response = await api.post(`/threads/${id}/step`, data);
    return response.data;
  },
};

// Entries
export const entriesApi = {
  list: async (filters?: {
    time_bucket?: string;
    topic_bucket?: string;
  }): Promise<LifeEntry[]> => {
    const response = await api.get('/entries', { params: filters });
    return response.data;
  },
  get: async (id: string): Promise<LifeEntry> => {
    const response = await api.get(`/entries/${id}`);
    return response.data;
  },
  updateSeal: async (id: string, data: any): Promise<LifeEntry> => {
    const response = await api.patch(`/entries/${id}/seal`, data);
    return response.data;
  },
  getCoverage: async (): Promise<CoverageCell[]> => {
    const response = await api.get('/entries/coverage/grid');
    return response.data;
  },
};

// Autobiography
export const autobiographyApi = {
  generate: async (data: AutobiographyRequest): Promise<Autobiography> => {
    const response = await api.post('/autobiography/generate', data);
    return response.data;
  },
};

export default api;
