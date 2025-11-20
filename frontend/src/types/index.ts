export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Profile {
  user_id: string;
  year_of_birth?: number;
  country?: string;
  primary_language?: string;
  relationship_status?: string;
  has_children?: boolean;
  children_count?: number;
  children_age_brackets?: string[];
  main_role?: string;
  field_or_industry?: string;
  avoid_topics?: string[];
  intensity?: 'light' | 'balanced' | 'deep';
  life_snapshot?: string;
  created_at: string;
  updated_at: string;
}

export interface Thread {
  id: string;
  user_id: string;
  title: string;
  root_prompt: string;
  time_focus?: string[];
  topic_focus?: string[];
  questions_asked: number;
  questions_since_last_freeform: number;
  created_at: string;
  last_activity_at: string;
}

export interface Question {
  id: string;
  type: 'multiple_choice' | 'short_answer';
  text: string;
  options?: Array<{ id: string; text: string }>;
}

export interface Answer {
  question_id: string;
  choice_id?: string;
  free_text?: string;
}

export interface StepResponse {
  done: boolean;
  question?: Question;
}

export interface LifeEntry {
  id: string;
  user_id: string;
  thread_id?: string;
  source_question_id?: string;
  time_bucket: string;
  approx_year_start?: number;
  approx_year_end?: number;
  timeframe_label: string;
  headline: string;
  raw_text: string;
  distilled: string;
  tags?: string[];
  topic_buckets?: string[];
  visibility: 'self' | 'trusted' | 'heirs' | 'public';
  seal_type: 'none' | 'until_date' | 'until_event' | 'until_manual';
  seal_release_at?: string;
  seal_event_key?: string;
  seal_audiences_blocked?: string[];
  emotional_tone?: string;
  people?: string[];
  locations?: string[];
  created_at: string;
  updated_at: string;
}

export interface CoverageCell {
  user_id: string;
  time_bucket: string;
  topic_bucket: string;
  score: number;
}

export interface AutobiographyRequest {
  audience: 'self' | 'trusted' | 'heirs' | 'public';
  date: string;
  include_placeholders: boolean;
  scope: {
    type: string;
    from?: number;
    to?: number;
  };
  tone: 'light' | 'balanced' | 'deep';
}

export interface Autobiography {
  outline: any;
  markdown: string;
}
