-- Storage bucket for project cover images.
-- Run once in the Supabase dashboard: SQL Editor -> New query -> paste -> Run.
--
-- Creates a public-read bucket that only signed-in users can write to. The
-- admin uploads from the browser with their own session, so no service_role key
-- is ever exposed client-side.

-- 1. The bucket. `public = true` means files are readable by URL, which is what
--    lets the portfolio show them to anonymous visitors.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'project-images',
  'project-images',
  true,
  5242880,                                   -- 5 MB per file
  array['image/png', 'image/jpeg', 'image/webp', 'image/avif', 'image/gif']
)
on conflict (id) do update
  set public             = excluded.public,
      file_size_limit    = excluded.file_size_limit,
      allowed_mime_types = excluded.allowed_mime_types;

-- 2. Anyone may read. Without this, visitors get 400s for every image.
drop policy if exists "Public read project images" on storage.objects;
create policy "Public read project images"
  on storage.objects
  for select
  using (bucket_id = 'project-images');

-- 3. Only signed-in users may add or change files. Anonymous visitors cannot
--    upload, so the bucket cannot be used as free file hosting.
drop policy if exists "Signed-in users upload project images" on storage.objects;
create policy "Signed-in users upload project images"
  on storage.objects
  for insert
  to authenticated
  with check (bucket_id = 'project-images');

drop policy if exists "Signed-in users update project images" on storage.objects;
create policy "Signed-in users update project images"
  on storage.objects
  for update
  to authenticated
  using (bucket_id = 'project-images');

drop policy if exists "Signed-in users delete project images" on storage.objects;
create policy "Signed-in users delete project images"
  on storage.objects
  for delete
  to authenticated
  using (bucket_id = 'project-images');
