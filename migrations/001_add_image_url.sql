-- Adds a cover image to projects.
-- Run once in the Supabase dashboard: SQL Editor -> New query -> paste -> Run.
--
-- Safe to run on an existing table: the column is nullable, so every existing
-- row keeps working and simply falls back to a generated tile until you set an
-- image. Re-running is harmless thanks to IF NOT EXISTS.

alter table public.projects
  add column if not exists image_url text;

comment on column public.projects.image_url is
  'Absolute http(s) URL to the project cover image. NULL means "no image yet".';
