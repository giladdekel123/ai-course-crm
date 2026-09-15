-- AI Course CRM schema
-- Run in the Supabase SQL editor (or `supabase db push`) against a fresh project.

create table if not exists courses (
  id bigint generated always as identity primary key,
  course_name text not null,
  description text,
  start_date date not null,
  duration text not null,
  price numeric(10, 2) not null check (price >= 0),
  capacity integer not null check (capacity > 0),
  delivery_format text not null check (delivery_format in ('In-person', 'Online', 'Hybrid')),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists leads (
  id bigint generated always as identity primary key,
  name text not null,
  phone text,
  email text,
  age integer check (age > 0),
  city text,
  occupation text,
  education text,
  technical_experience text,
  reason_for_interest text,
  source text,
  status text not null default 'New'
    check (status in ('New', 'Contacted', 'Follow-up', 'Interested', 'Converted', 'Not Interested')),
  -- Not in the original Data Model doc: added so a lead can record which course
  -- it's interested in before any Registration exists (needed by the Leads and
  -- ML Predictions screens' "Course Interest" column).
  course_interest_id bigint references courses (id),
  created_at timestamptz not null default now()
);

create table if not exists registrations (
  id bigint generated always as identity primary key,
  lead_id bigint not null references leads (id),
  course_id bigint not null references courses (id),
  enrollment_date date not null default current_date,
  amount_paid numeric(10, 2) not null check (amount_paid >= 0),
  payment_method text,
  created_at timestamptz not null default now()
);

create index if not exists leads_status_idx on leads (status);
create index if not exists leads_source_idx on leads (source);
create index if not exists leads_course_interest_id_idx on leads (course_interest_id);
create index if not exists registrations_lead_id_idx on registrations (lead_id);
create index if not exists registrations_course_id_idx on registrations (course_id);

-- No client ever talks to Supabase directly (Flask holds the service-role key
-- server-side), so RLS is enabled with no policies: this blocks the anon/
-- authenticated roles entirely while the service role still bypasses RLS.
alter table courses enable row level security;
alter table leads enable row level security;
alter table registrations enable row level security;
