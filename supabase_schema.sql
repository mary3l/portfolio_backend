-- Run this once in the Supabase dashboard: SQL Editor -> New query -> paste -> Run.

create table if not exists public.projects (
  id bigint generated always as identity primary key,
  title text not null,
  problem text not null,
  solution text not null,
  contribution text not null,
  type text not null,
  tools_used text not null,
  created_at timestamptz not null default now()
);

-- Lock the table down; the backend uses the service_role key which bypasses RLS.
alter table public.projects enable row level security;

-- Allow anyone to read projects (for the public portfolio page).
create policy "Public read access"
  on public.projects
  for select
  using (true);
