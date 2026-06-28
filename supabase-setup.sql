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

create or replace function public.save_quiz_lead(payload jsonb)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if coalesce(payload->>'session_id', '') = '' then
    raise exception 'session_id é obrigatório';
  end if;

  insert into public.quiz_leads (
    session_id,
    status,
    ultima_pergunta,
    iniciou_em,
    concluido_em,
    checkout_em,
    genero,
    faixa_etaria,
    tempo_queda,
    padrao_queda,
    fios_por_dia,
    historico_familiar,
    eventos_ultimos_12_meses,
    frequencia_quimica,
    rotina_sono_alimentacao,
    tratamentos_tentados,
    diagnostico,
    nivel_risco,
    clicou_checkout,
    checkout_cta,
    checkout_link,
    page_url,
    referrer,
    user_agent,
    screen_width,
    screen_height,
    utm_source,
    utm_medium,
    utm_campaign,
    utm_content,
    utm_term,
    fbclid,
    gclid,
    respostas_json
  )
  values (
    payload->>'session_id',
    coalesce(nullif(payload->>'status', ''), 'iniciou'),
    nullif(payload->>'ultima_pergunta', '')::integer,
    nullif(payload->>'iniciou_em', '')::timestamptz,
    nullif(payload->>'concluido_em', '')::timestamptz,
    nullif(payload->>'checkout_em', '')::timestamptz,
    nullif(payload->>'genero', ''),
    nullif(payload->>'faixa_etaria', ''),
    nullif(payload->>'tempo_queda', ''),
    nullif(payload->>'padrao_queda', ''),
    nullif(payload->>'fios_por_dia', ''),
    nullif(payload->>'historico_familiar', ''),
    nullif(payload->>'eventos_ultimos_12_meses', ''),
    nullif(payload->>'frequencia_quimica', ''),
    nullif(payload->>'rotina_sono_alimentacao', ''),
    nullif(payload->>'tratamentos_tentados', ''),
    nullif(payload->>'diagnostico', ''),
    nullif(payload->>'nivel_risco', ''),
    coalesce(nullif(payload->>'clicou_checkout', '')::boolean, false),
    nullif(payload->>'checkout_cta', ''),
    nullif(payload->>'checkout_link', ''),
    nullif(payload->>'page_url', ''),
    nullif(payload->>'referrer', ''),
    nullif(payload->>'user_agent', ''),
    nullif(payload->>'screen_width', '')::integer,
    nullif(payload->>'screen_height', '')::integer,
    nullif(payload->>'utm_source', ''),
    nullif(payload->>'utm_medium', ''),
    nullif(payload->>'utm_campaign', ''),
    nullif(payload->>'utm_content', ''),
    nullif(payload->>'utm_term', ''),
    nullif(payload->>'fbclid', ''),
    nullif(payload->>'gclid', ''),
    coalesce(payload->'respostas_json', '{}'::jsonb)
  )
  on conflict (session_id) do update set
    updated_at = now(),
    status = coalesce(excluded.status, public.quiz_leads.status),
    ultima_pergunta = coalesce(excluded.ultima_pergunta, public.quiz_leads.ultima_pergunta),
    iniciou_em = coalesce(public.quiz_leads.iniciou_em, excluded.iniciou_em),
    concluido_em = coalesce(excluded.concluido_em, public.quiz_leads.concluido_em),
    checkout_em = coalesce(excluded.checkout_em, public.quiz_leads.checkout_em),
    genero = coalesce(excluded.genero, public.quiz_leads.genero),
    faixa_etaria = coalesce(excluded.faixa_etaria, public.quiz_leads.faixa_etaria),
    tempo_queda = coalesce(excluded.tempo_queda, public.quiz_leads.tempo_queda),
    padrao_queda = coalesce(excluded.padrao_queda, public.quiz_leads.padrao_queda),
    fios_por_dia = coalesce(excluded.fios_por_dia, public.quiz_leads.fios_por_dia),
    historico_familiar = coalesce(excluded.historico_familiar, public.quiz_leads.historico_familiar),
    eventos_ultimos_12_meses = coalesce(excluded.eventos_ultimos_12_meses, public.quiz_leads.eventos_ultimos_12_meses),
    frequencia_quimica = coalesce(excluded.frequencia_quimica, public.quiz_leads.frequencia_quimica),
    rotina_sono_alimentacao = coalesce(excluded.rotina_sono_alimentacao, public.quiz_leads.rotina_sono_alimentacao),
    tratamentos_tentados = coalesce(excluded.tratamentos_tentados, public.quiz_leads.tratamentos_tentados),
    diagnostico = coalesce(excluded.diagnostico, public.quiz_leads.diagnostico),
    nivel_risco = coalesce(excluded.nivel_risco, public.quiz_leads.nivel_risco),
    clicou_checkout = public.quiz_leads.clicou_checkout or excluded.clicou_checkout,
    checkout_cta = coalesce(excluded.checkout_cta, public.quiz_leads.checkout_cta),
    checkout_link = coalesce(excluded.checkout_link, public.quiz_leads.checkout_link),
    page_url = coalesce(excluded.page_url, public.quiz_leads.page_url),
    referrer = coalesce(excluded.referrer, public.quiz_leads.referrer),
    user_agent = coalesce(excluded.user_agent, public.quiz_leads.user_agent),
    screen_width = coalesce(excluded.screen_width, public.quiz_leads.screen_width),
    screen_height = coalesce(excluded.screen_height, public.quiz_leads.screen_height),
    utm_source = coalesce(excluded.utm_source, public.quiz_leads.utm_source),
    utm_medium = coalesce(excluded.utm_medium, public.quiz_leads.utm_medium),
    utm_campaign = coalesce(excluded.utm_campaign, public.quiz_leads.utm_campaign),
    utm_content = coalesce(excluded.utm_content, public.quiz_leads.utm_content),
    utm_term = coalesce(excluded.utm_term, public.quiz_leads.utm_term),
    fbclid = coalesce(excluded.fbclid, public.quiz_leads.fbclid),
    gclid = coalesce(excluded.gclid, public.quiz_leads.gclid),
    respostas_json = coalesce(excluded.respostas_json, public.quiz_leads.respostas_json);
end;
$$;

grant execute on function public.save_quiz_lead(jsonb) to anon;

create or replace function public.get_quiz_leads_dashboard()
returns jsonb
language sql
security definer
set search_path = public
as $$
with
base as (
  select *
  from public.quiz_leads
),
summary as (
  select
    count(*)::integer as total_leads,
    count(*) filter (where status in ('respondendo', 'concluiu', 'checkout'))::integer as leads_iniciados,
    count(*) filter (where status in ('concluiu', 'checkout'))::integer as leads_concluidos,
    count(*) filter (where clicou_checkout = true)::integer as leads_checkout,
    count(*) filter (where created_at >= date_trunc('day', now()))::integer as leads_hoje,
    count(*) filter (where created_at >= now() - interval '7 days')::integer as leads_7_dias,
    max(updated_at) as ultimo_evento
  from base
),
rates as (
  select
    *,
    case
      when leads_iniciados = 0 then 0
      else round((leads_concluidos::numeric / leads_iniciados::numeric) * 100, 1)
    end as taxa_conclusao,
    case
      when leads_concluidos = 0 then 0
      else round((leads_checkout::numeric / leads_concluidos::numeric) * 100, 1)
    end as taxa_checkout
  from summary
),
diagnosticos as (
  select
    coalesce(nullif(diagnostico, ''), 'Sem diagnóstico') as nome,
    coalesce(nullif(nivel_risco, ''), 'Sem risco') as risco,
    count(*)::integer as total
  from base
  group by 1, 2
  order by total desc, nome asc
),
origens as (
  select
    coalesce(nullif(utm_source, ''), 'sem_utm') as origem,
    coalesce(nullif(utm_campaign, ''), 'sem_campanha') as campanha,
    count(*)::integer as total,
    count(*) filter (where clicou_checkout = true)::integer as checkouts
  from base
  group by 1, 2
  order by total desc
  limit 20
),
status_funil as (
  select
    status as nome,
    count(*)::integer as total
  from base
  group by 1
  order by total desc
),
respostas as (
  select 'Gênero' as pergunta, genero as resposta, count(*)::integer as total from base where genero is not null group by genero
  union all
  select 'Faixa etária', faixa_etaria, count(*)::integer from base where faixa_etaria is not null group by faixa_etaria
  union all
  select 'Tempo de queda', tempo_queda, count(*)::integer from base where tempo_queda is not null group by tempo_queda
  union all
  select 'Padrão da queda', padrao_queda, count(*)::integer from base where padrao_queda is not null group by padrao_queda
  union all
  select 'Fios por dia', fios_por_dia, count(*)::integer from base where fios_por_dia is not null group by fios_por_dia
  union all
  select 'Histórico familiar', historico_familiar, count(*)::integer from base where historico_familiar is not null group by historico_familiar
  union all
  select 'Eventos 12 meses', eventos_ultimos_12_meses, count(*)::integer from base where eventos_ultimos_12_meses is not null group by eventos_ultimos_12_meses
  union all
  select 'Química', frequencia_quimica, count(*)::integer from base where frequencia_quimica is not null group by frequencia_quimica
  union all
  select 'Sono/alimentação', rotina_sono_alimentacao, count(*)::integer from base where rotina_sono_alimentacao is not null group by rotina_sono_alimentacao
  union all
  select 'Tratamentos', tratamentos_tentados, count(*)::integer from base where tratamentos_tentados is not null group by tratamentos_tentados
),
respostas_top as (
  select *
  from respostas
  order by pergunta asc, total desc
),
recentes as (
  select
    created_at,
    updated_at,
    status,
    genero,
    faixa_etaria,
    tempo_queda,
    padrao_queda,
    fios_por_dia,
    eventos_ultimos_12_meses,
    diagnostico,
    nivel_risco,
    clicou_checkout,
    coalesce(nullif(utm_source, ''), 'sem_utm') as utm_source,
    coalesce(nullif(utm_campaign, ''), 'sem_campanha') as utm_campaign,
    left(session_id, 8) as sessao
  from base
  order by updated_at desc
  limit 80
)
select jsonb_build_object(
  'generated_at', now(),
  'summary', (
    select jsonb_build_object(
      'total_leads', total_leads,
      'leads_iniciados', leads_iniciados,
      'leads_concluidos', leads_concluidos,
      'leads_checkout', leads_checkout,
      'leads_hoje', leads_hoje,
      'leads_7_dias', leads_7_dias,
      'taxa_conclusao', taxa_conclusao,
      'taxa_checkout', taxa_checkout,
      'ultimo_evento', ultimo_evento
    )
    from rates
  ),
  'funil', (
    select jsonb_build_array(
      jsonb_build_object('nome', 'Iniciaram', 'total', leads_iniciados),
      jsonb_build_object('nome', 'Concluíram', 'total', leads_concluidos),
      jsonb_build_object('nome', 'Checkout', 'total', leads_checkout)
    )
    from rates
  ),
  'diagnosticos', coalesce((
    select jsonb_agg(jsonb_build_object('nome', nome, 'risco', risco, 'total', total))
    from diagnosticos
  ), '[]'::jsonb),
  'origens', coalesce((
    select jsonb_agg(jsonb_build_object('origem', origem, 'campanha', campanha, 'total', total, 'checkouts', checkouts))
    from origens
  ), '[]'::jsonb),
  'status_funil', coalesce((
    select jsonb_agg(jsonb_build_object('nome', nome, 'total', total))
    from status_funil
  ), '[]'::jsonb),
  'respostas_top', coalesce((
    select jsonb_agg(jsonb_build_object('pergunta', pergunta, 'resposta', resposta, 'total', total))
    from respostas_top
  ), '[]'::jsonb),
  'recentes', coalesce((
    select jsonb_agg(jsonb_build_object(
      'created_at', created_at,
      'updated_at', updated_at,
      'status', status,
      'genero', genero,
      'faixa_etaria', faixa_etaria,
      'tempo_queda', tempo_queda,
      'padrao_queda', padrao_queda,
      'fios_por_dia', fios_por_dia,
      'eventos_ultimos_12_meses', eventos_ultimos_12_meses,
      'diagnostico', diagnostico,
      'nivel_risco', nivel_risco,
      'clicou_checkout', clicou_checkout,
      'utm_source', utm_source,
      'utm_campaign', utm_campaign,
      'sessao', sessao
    ))
    from recentes
  ), '[]'::jsonb)
);
$$;

revoke all on function public.get_quiz_leads_dashboard() from public;
revoke all on function public.get_quiz_leads_dashboard() from anon;
grant execute on function public.get_quiz_leads_dashboard() to authenticated;

-- Migração opcional:
-- Se você já tinha dados na tabela antiga quiz_events, este bloco tenta organizar
-- esses registros antigos dentro da nova tabela quiz_leads.
do $$
begin
  if to_regclass('public.quiz_events') is not null then
    insert into public.quiz_leads (
      created_at,
      updated_at,
      session_id,
      status,
      ultima_pergunta,
      iniciou_em,
      concluido_em,
      checkout_em,
      genero,
      faixa_etaria,
      tempo_queda,
      padrao_queda,
      fios_por_dia,
      historico_familiar,
      eventos_ultimos_12_meses,
      frequencia_quimica,
      rotina_sono_alimentacao,
      tratamentos_tentados,
      diagnostico,
      nivel_risco,
      clicou_checkout,
      checkout_cta,
      checkout_link,
      page_url,
      referrer,
      user_agent,
      screen_width,
      screen_height,
      utm_source,
      utm_medium,
      utm_campaign,
      utm_content,
      utm_term,
      fbclid,
      gclid,
      respostas_json
    )
    select
      min(e.created_at) as created_at,
      max(e.created_at) as updated_at,
      e.session_id,
      case
        when count(*) filter (where e.event_name = 'checkout_clicked') > 0 then 'checkout'
        when count(*) filter (where e.event_name = 'quiz_completed') > 0 then 'concluiu'
        when count(*) filter (where e.event_name = 'question_answered') > 0 then 'respondendo'
        when count(*) filter (where e.event_name = 'quiz_started') > 0 then 'iniciou'
        else 'visitou'
      end as status,
      max(
        case
          when e.event_name = 'question_answered'
            and coalesce(e.event_data->>'question_number', '') ~ '^[0-9]+$'
          then (e.event_data->>'question_number')::integer
          else null
        end
      ) as ultima_pergunta,
      min(e.created_at) filter (where e.event_name = 'quiz_started') as iniciou_em,
      max(e.created_at) filter (where e.event_name = 'quiz_completed') as concluido_em,
      max(e.created_at) filter (where e.event_name = 'checkout_clicked') as checkout_em,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '1') as genero,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '2') as faixa_etaria,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '3') as tempo_queda,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '4') as padrao_queda,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '5') as fios_por_dia,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '6') as historico_familiar,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '7') as eventos_ultimos_12_meses,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '8') as frequencia_quimica,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '9') as rotina_sono_alimentacao,
      max(e.event_data->>'answer_label') filter (where e.event_name = 'question_answered' and e.event_data->>'question_number' = '10') as tratamentos_tentados,
      max(e.event_data->>'result_title') filter (where e.event_name = 'quiz_completed') as diagnostico,
      max(e.event_data->>'risk_level') filter (where e.event_name = 'quiz_completed') as nivel_risco,
      (count(*) filter (where e.event_name = 'checkout_clicked') > 0) as clicou_checkout,
      max(e.event_data->>'cta') filter (where e.event_name = 'checkout_clicked') as checkout_cta,
      max(e.event_data->>'href') filter (where e.event_name = 'checkout_clicked') as checkout_link,
      max(e.page_url) as page_url,
      max(e.referrer) as referrer,
      max(e.user_agent) as user_agent,
      max(e.screen_width) as screen_width,
      max(e.screen_height) as screen_height,
      max(e.utm_source) as utm_source,
      max(e.utm_medium) as utm_medium,
      max(e.utm_campaign) as utm_campaign,
      max(e.utm_content) as utm_content,
      max(e.utm_term) as utm_term,
      max(e.fbclid) as fbclid,
      max(e.gclid) as gclid,
      jsonb_build_object('migrado_de', 'quiz_events') as respostas_json
    from public.quiz_events e
    group by e.session_id
    on conflict (session_id) do update set
      updated_at = greatest(public.quiz_leads.updated_at, excluded.updated_at),
      status = excluded.status,
      ultima_pergunta = coalesce(public.quiz_leads.ultima_pergunta, excluded.ultima_pergunta),
      iniciou_em = coalesce(public.quiz_leads.iniciou_em, excluded.iniciou_em),
      concluido_em = coalesce(public.quiz_leads.concluido_em, excluded.concluido_em),
      checkout_em = coalesce(public.quiz_leads.checkout_em, excluded.checkout_em),
      genero = coalesce(public.quiz_leads.genero, excluded.genero),
      faixa_etaria = coalesce(public.quiz_leads.faixa_etaria, excluded.faixa_etaria),
      tempo_queda = coalesce(public.quiz_leads.tempo_queda, excluded.tempo_queda),
      padrao_queda = coalesce(public.quiz_leads.padrao_queda, excluded.padrao_queda),
      fios_por_dia = coalesce(public.quiz_leads.fios_por_dia, excluded.fios_por_dia),
      historico_familiar = coalesce(public.quiz_leads.historico_familiar, excluded.historico_familiar),
      eventos_ultimos_12_meses = coalesce(public.quiz_leads.eventos_ultimos_12_meses, excluded.eventos_ultimos_12_meses),
      frequencia_quimica = coalesce(public.quiz_leads.frequencia_quimica, excluded.frequencia_quimica),
      rotina_sono_alimentacao = coalesce(public.quiz_leads.rotina_sono_alimentacao, excluded.rotina_sono_alimentacao),
      tratamentos_tentados = coalesce(public.quiz_leads.tratamentos_tentados, excluded.tratamentos_tentados),
      diagnostico = coalesce(public.quiz_leads.diagnostico, excluded.diagnostico),
      nivel_risco = coalesce(public.quiz_leads.nivel_risco, excluded.nivel_risco),
      clicou_checkout = public.quiz_leads.clicou_checkout or excluded.clicou_checkout,
      checkout_cta = coalesce(public.quiz_leads.checkout_cta, excluded.checkout_cta),
      checkout_link = coalesce(public.quiz_leads.checkout_link, excluded.checkout_link),
      page_url = coalesce(public.quiz_leads.page_url, excluded.page_url),
      referrer = coalesce(public.quiz_leads.referrer, excluded.referrer),
      user_agent = coalesce(public.quiz_leads.user_agent, excluded.user_agent),
      screen_width = coalesce(public.quiz_leads.screen_width, excluded.screen_width),
      screen_height = coalesce(public.quiz_leads.screen_height, excluded.screen_height),
      utm_source = coalesce(public.quiz_leads.utm_source, excluded.utm_source),
      utm_medium = coalesce(public.quiz_leads.utm_medium, excluded.utm_medium),
      utm_campaign = coalesce(public.quiz_leads.utm_campaign, excluded.utm_campaign),
      utm_content = coalesce(public.quiz_leads.utm_content, excluded.utm_content),
      utm_term = coalesce(public.quiz_leads.utm_term, excluded.utm_term),
      fbclid = coalesce(public.quiz_leads.fbclid, excluded.fbclid),
      gclid = coalesce(public.quiz_leads.gclid, excluded.gclid);
  end if;
end $$;

-- Segurança:
-- Não criamos policy de SELECT para anon.
-- Visitantes conseguem enviar/atualizar dados do lead, mas não conseguem ler sua tabela.
--
-- A tabela antiga public.quiz_events pode ficar como histórico bruto.
-- A tabela que você deve olhar no dia a dia agora é public.quiz_leads.
