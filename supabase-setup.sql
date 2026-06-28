-- Configuração inicial para registrar eventos anônimos do quiz no Supabase.
-- Como usar:
-- 1) Abra o painel do Supabase.
-- 2) Vá em SQL Editor.
-- 3) Cole este arquivo inteiro e execute.

create extension if not exists pgcrypto;

create table if not exists public.quiz_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  session_id text not null,
  event_name text not null,
  event_data jsonb not null default '{}'::jsonb,
  page_url text,
  referrer text,
  user_agent text,
  screen_width integer,
  screen_height integer,
  utm_source text,
  utm_medium text,
  utm_campaign text,
  utm_content text,
  utm_term text,
  fbclid text,
  gclid text
);

create index if not exists quiz_events_session_id_idx
  on public.quiz_events (session_id);

create index if not exists quiz_events_event_name_idx
  on public.quiz_events (event_name);

create index if not exists quiz_events_created_at_idx
  on public.quiz_events (created_at desc);

alter table public.quiz_events enable row level security;

drop policy if exists "Permitir insert anonimo de eventos do quiz" on public.quiz_events;

create policy "Permitir insert anonimo de eventos do quiz"
  on public.quiz_events
  for insert
  to anon
  with check (true);

-- Por segurança, não criamos policy de SELECT para anon.
-- Assim, visitantes conseguem enviar eventos, mas não conseguem ler dados do banco.
