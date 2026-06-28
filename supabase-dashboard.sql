-- Dashboard agregado para a rota /dados.
-- Como usar:
-- 1) Abra o painel do Supabase.
-- 2) Vá em SQL Editor.
-- 3) Cole este arquivo inteiro e execute.
--
-- Importante:
-- Esta função libera somente dados agregados/resumidos para o painel.
-- Não cria policy de SELECT direto na tabela quiz_events.

create or replace function public.get_quiz_dashboard_data()
returns jsonb
language sql
security definer
set search_path = public
as $$
with
base as (
  select *
  from public.quiz_events
),
summary as (
  select
    count(*)::integer as total_events,
    count(distinct session_id)::integer as total_sessions,
    count(distinct session_id) filter (where event_name = 'quiz_started')::integer as started_sessions,
    count(distinct session_id) filter (where event_name = 'quiz_completed')::integer as completed_sessions,
    count(distinct session_id) filter (where event_name = 'checkout_clicked')::integer as checkout_sessions,
    count(*) filter (where created_at >= date_trunc('day', now()))::integer as events_today,
    max(created_at) as last_event_at
  from base
),
rates as (
  select
    *,
    case
      when started_sessions = 0 then 0
      else round((completed_sessions::numeric / started_sessions::numeric) * 100, 1)
    end as completion_rate,
    case
      when completed_sessions = 0 then 0
      else round((checkout_sessions::numeric / completed_sessions::numeric) * 100, 1)
    end as checkout_rate
  from summary
),
results as (
  select
    coalesce(nullif(event_data->>'result_title', ''), 'Sem diagnóstico') as result_title,
    coalesce(nullif(event_data->>'risk_level', ''), 'Sem nível') as risk_level,
    count(*)::integer as total
  from base
  where event_name = 'quiz_completed'
  group by 1, 2
  order by total desc, result_title asc
),
questions as (
  select *
  from (
    select
      coalesce(event_data->>'question_number', '?') as question_number,
      coalesce(nullif(event_data->>'question_title', ''), 'Pergunta sem título') as question_title,
      coalesce(nullif(event_data->>'answer_label', ''), 'Resposta sem texto') as answer_label,
      count(*)::integer as total
    from base
    where event_name = 'question_answered'
    group by 1, 2, 3
  ) grouped_questions
  order by
    case when question_number ~ '^[0-9]+$'
      then question_number::integer
      else 999
    end,
    total desc
),
sources as (
  select
    coalesce(nullif(utm_source, ''), 'sem_utm') as source,
    count(distinct session_id)::integer as sessions,
    count(*)::integer as events
  from base
  group by 1
  order by sessions desc, events desc
  limit 12
),
recent_events as (
  select
    created_at,
    session_id,
    event_name,
    coalesce(event_data->>'question_number', '') as question_number,
    coalesce(event_data->>'answer_label', '') as answer_label,
    coalesce(event_data->>'result_title', '') as result_title,
    coalesce(event_data->>'risk_level', '') as risk_level,
    coalesce(event_data->>'cta', '') as cta,
    coalesce(nullif(utm_source, ''), 'sem_utm') as utm_source,
    page_url
  from base
  order by created_at desc
  limit 80
)
select jsonb_build_object(
  'generated_at', now(),
  'summary', (
    select jsonb_build_object(
      'total_events', total_events,
      'total_sessions', total_sessions,
      'started_sessions', started_sessions,
      'completed_sessions', completed_sessions,
      'checkout_sessions', checkout_sessions,
      'events_today', events_today,
      'completion_rate', completion_rate,
      'checkout_rate', checkout_rate,
      'last_event_at', last_event_at
    )
    from rates
  ),
  'funnel', (
    select jsonb_build_array(
      jsonb_build_object('label', 'Iniciaram', 'value', started_sessions),
      jsonb_build_object('label', 'Concluíram', 'value', completed_sessions),
      jsonb_build_object('label', 'Checkout', 'value', checkout_sessions)
    )
    from rates
  ),
  'results', coalesce((
    select jsonb_agg(jsonb_build_object(
      'result_title', result_title,
      'risk_level', risk_level,
      'total', total
    ))
    from results
  ), '[]'::jsonb),
  'questions', coalesce((
    select jsonb_agg(jsonb_build_object(
      'question_number', question_number,
      'question_title', question_title,
      'answer_label', answer_label,
      'total', total
    ))
    from questions
  ), '[]'::jsonb),
  'sources', coalesce((
    select jsonb_agg(jsonb_build_object(
      'source', source,
      'sessions', sessions,
      'events', events
    ))
    from sources
  ), '[]'::jsonb),
  'recent_events', coalesce((
    select jsonb_agg(jsonb_build_object(
      'created_at', created_at,
      'session_id', session_id,
      'event_name', event_name,
      'question_number', question_number,
      'answer_label', answer_label,
      'result_title', result_title,
      'risk_level', risk_level,
      'cta', cta,
      'utm_source', utm_source,
      'page_url', page_url
    ))
    from recent_events
  ), '[]'::jsonb)
);
$$;

grant execute on function public.get_quiz_dashboard_data() to anon;
