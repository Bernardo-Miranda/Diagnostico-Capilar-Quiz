-- Configuração organizada para registrar leads anônimos do quiz no Supabase.
-- Como usar:
-- 1) Abra o painel do Supabase.
-- 2) Vá em SQL Editor.
-- 3) Cole este arquivo inteiro e execute.
--
-- Resultado:
-- Será criada a tabela public.quiz_leads.
-- Nela, cada linha representa uma pessoa/sessão do quiz, com colunas fáceis de entender.

create extension if not exists pgcrypto;

create table if not exists public.quiz_leads (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  -- Identificação da sessão anônima
  session_id text not null unique,
  status text not null default 'iniciou',
  ultima_pergunta integer,

  -- Datas importantes do funil
  iniciou_em timestamptz,
  concluido_em timestamptz,
  checkout_em timestamptz,

  -- Respostas principais, já organizadas em colunas
  genero text,
  faixa_etaria text,
  tempo_queda text,
  padrao_queda text,
  fios_por_dia text,
  historico_familiar text,
  eventos_ultimos_12_meses text,
  frequencia_quimica text,
  rotina_sono_alimentacao text,
  tratamentos_tentados text,

  -- Resultado final do diagnóstico
  diagnostico text,
  nivel_risco text,

  -- Checkout
  clicou_checkout boolean not null default false,
  checkout_cta text,
  checkout_link text,

  -- Origem e rastreamento
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
  gclid text,

  -- Backup técnico das respostas, caso queira auditar depois
  respostas_json jsonb not null default '{}'::jsonb
);

create index if not exists quiz_leads_created_at_idx
  on public.quiz_leads (created_at desc);

create index if not exists quiz_leads_status_idx
  on public.quiz_leads (status);

create index if not exists quiz_leads_diagnostico_idx
  on public.quiz_leads (diagnostico);

create index if not exists quiz_leads_utm_source_idx
  on public.quiz_leads (utm_source);

alter table public.quiz_leads enable row level security;

drop policy if exists "Permitir inserir leads anonimos do quiz" on public.quiz_leads;
drop policy if exists "Permitir atualizar leads anonimos do quiz" on public.quiz_leads;

create policy "Permitir inserir leads anonimos do quiz"
  on public.quiz_leads
  for insert
  to anon
  with check (true);

create policy "Permitir atualizar leads anonimos do quiz"
  on public.quiz_leads
  for update
  to anon
  using (true)
  with check (true);

-- Segurança:
-- Não criamos policy de SELECT para anon.
-- Visitantes conseguem enviar/atualizar dados do lead, mas não conseguem ler sua tabela.
--
-- A tabela antiga public.quiz_events pode ficar como histórico bruto.
-- A tabela que você deve olhar no dia a dia agora é public.quiz_leads.
