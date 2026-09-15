# AI Course CRM

A CRM for an organization that sells AI courses. It tracks potential students ("leads") from first contact through enrollment and payment, and includes a machine learning component that predicts each lead's probability of purchasing and explains the factors behind that prediction.

Full functional specification: [`docs/`](docs/) (project definition, MVP/user flow, data model, UI spec).

## Contents

- [Screens](#screens)
- [Architecture](#architecture)
- [Data model & Supabase](#data-model--supabase)
- [ML model](#ml-model)
- [Setup](#setup)
- [Running locally](#running-locally)
- [Testing](#testing)
- [Project layout](#project-layout)

## Screens

| Screen | Route | What it shows |
|---|---|---|
| Dashboard | `/` | Pipeline KPIs, conversion rate, leads needing follow-up, course capacity vs. interest, revenue by course, lead sources |
| Leads | `/leads/` | Searchable/filterable lead directory, create/view/edit, status changes, convert-to-registration |
| Courses | `/courses/` | Course catalog with enrolled/interested counts and capacity fill %, create/edit/archive |
| ML Predictions | `/predictions/` | Purchase probability, priority tier, and top contributing factors for every active (non-terminal) lead |

The visual design follows a Google Stitch reference project ("AI Course Sales CRM") — its design tokens (colors, type scale, spacing, radii) and component patterns were carried over into the Jinja templates; fictional/decorative elements from the mockup (a fake persona, made-up stats) were dropped in favor of real data. See [UI Specification](docs/04%20-%20UI%20Specification.md) for the functional spec, which takes priority over the mockup wherever the two disagree.

## Architecture

Flask, server-rendered with Jinja2 (no separate frontend build) and Supabase as the datastore, accessed through `supabase-py` with the service-role key held server-side only.

```
Blueprint (routes.py)  ->  Service (business logic)  ->  Repository (supabase-py calls)
```

- **`app/blueprints/`** — one blueprint per screen (`dashboard`, `leads`, `courses`, `predictions`). Routes handle HTTP concerns only: parsing request args/forms, calling a service, rendering a template or redirecting.
- **`app/services/`** — business logic: status-transition rules, the convert-to-registration flow, dashboard aggregation math, and ML scoring/explanation. Depend on repositories, never on `supabase-py` directly.
- **`app/repositories/`** — thin one-call-per-function wrappers around `supabase-py` (`select`/`insert`/`update`). This is the seam the test suite monkeypatches, so service-level tests never touch a network or a real database.
- **`app/templates/`** — `base.html` carries the nav rail, header, and the Tailwind config (design tokens transcribed from the Stitch reference); each screen extends it.
- **`app/constants.py`** — the single source of truth for option lists (statuses, occupations, education levels, sources, etc.), shared by form dropdowns *and* the synthetic data generator, so they can't silently drift apart.
- **`app/extensions.py`** — builds the per-request Supabase client (`get_supabase_client`, cached on Flask's `g`) and lazily loads the trained ML pipeline / metrics once per process (cached on `current_app.extensions`).

## Data model & Supabase

Three tables, defined in [`supabase/schema.sql`](supabase/schema.sql) (source of truth) and tracked as a migration in `supabase/migrations/`:

- **`courses`** — `course_name`, `description`, `start_date`, `duration`, `price`, `capacity`, `delivery_format` (In-person/Online/Hybrid), `is_active` (archived instead of deleted once a course has registrations).
- **`leads`** — contact info, `age`, `city`, `occupation`, `education`, `technical_experience`, `reason_for_interest`, `source`, `status` (New → Contacted → Follow-up → Interested → Converted, or Not Interested), and `course_interest_id` (FK → `courses`).
  > `course_interest_id` is an addition beyond the original Data Model doc: the UI and ML specs both need a "Course Interest" per lead, and a lead can express interest before any registration exists.
- **`registrations`** — `lead_id` + `course_id` (FKs), `enrollment_date`, `amount_paid`, `payment_method`. Created only when a lead enrolls and pays; that's what flips the lead to `Converted`.

Conventions: `bigint identity` primary keys, `text` over `varchar`, `timestamptz`/`numeric` where appropriate, `check` constraints standing in for enums, an index on every FK/filter column. RLS is enabled on all three tables with **no** policies — nothing but the Flask backend (service-role key) ever talks to Supabase directly, so this blocks the `anon`/`authenticated` roles entirely while the service role still bypasses RLS as usual.

To apply the schema to a Supabase project:

```
supabase link --project-ref <your-project-ref>
supabase db push
```

(or paste `supabase/schema.sql` into the Supabase SQL editor for a one-off setup).

## ML model

`ml/train_model.py` pulls every historical lead with a **terminal** status (`Converted` / `Not Interested`) from Supabase, joined with its interested course's `delivery_format`, and trains a `scikit-learn` pipeline: `OneHotEncoder`/`StandardScaler` → `LogisticRegression`. Run it with `python -m ml.train_model`; it writes `ml/model.joblib` (the fitted pipeline) and `ml/metrics.json` (accuracy/precision/recall/F1/ROC-AUC computed on a held-out test split — real numbers, never placeholders).

**Feature choices, and why:**
- **`status` is deliberately excluded** as a model feature. For historical (training) leads, status is terminal — it *is* the label — so using it would leak the target and produce a fake near-100% accuracy. Active leads (the ones actually scored) never have a terminal status, so it wouldn't carry real signal at inference either. Current status is still shown next to each prediction in the UI, just not fed to the model.
- **"Course Interest"** is represented by the course's `delivery_format` rather than the specific course, since course identity carries no independent signal beyond its format in this dataset.

At inference time (`app/services/ml_service.py`), each active lead gets a `predict_proba` probability, a priority tier (`High` ≥ 66%, `Medium` ≥ 33%, else `Low`), and its top 3 contributing factors — computed as each encoded feature's signed contribution (`coefficient × encoded value`), mapped back to a human-readable label like `Technical Experience: Advanced`.

Current metrics (regenerate with `python -m ml.train_model`):

| Metric | Value |
|---|---|
| Accuracy | 60.0% |
| Precision | 56.3% |
| Recall | 43.5% |
| F1 | 49.1% |
| ROC-AUC | 0.654 |
| Train / test size | 560 / 140 |

These numbers are modest but genuine — the synthetic training data has deliberate noise baked into its ground-truth propensity function (see `scripts/generate_synthetic_data.py`), so a model that found a *perfect* fit would actually indicate a leakage bug, not a good model.

## Setup

Requires Python 3.11+ and a Supabase project (the Supabase CLI, `supabase`, is optional but convenient for applying the schema).

```
python -m venv .venv
.venv\Scripts\activate            # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
copy .env.example .env            # `cp` on macOS/Linux
```

Fill in `.env`:

| Variable | Description |
|---|---|
| `FLASK_SECRET_KEY` | Any random string — used for session signing and CSRF |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | The project's **service role** key (server-side only — never expose this to a browser) |

Apply the schema to your Supabase project (see [Data model & Supabase](#data-model--supabase) above), then generate synthetic data, seed it, and train the model:

```
python -m scripts.generate_synthetic_data   # writes CSVs to data/synthetic/
python -m scripts.seed_supabase             # loads them into Supabase (refuses to run if tables aren't empty)
python -m ml.train_model                    # writes ml/model.joblib + ml/metrics.json
```

## Running locally

```
flask --app wsgi run --debug
```

Visit `http://127.0.0.1:5000/`.

## Testing

```
pytest
```

62 tests across three layers, each with its own mocking seam:

- **`tests/test_services/`** — business logic, with `app/repositories/*` monkeypatched. No network, no database.
- **`tests/test_ml/`** — `ml/features.py` structural guarantees (status is never a feature, unseen categories don't crash inference) and an end-to-end fit/predict/explain cycle against a small in-memory fixture.
- **`tests/test_routes/`** — Flask test client against all four screens and every write path (create/edit/status-change/convert/archive), with the service layer monkeypatched.

`tests/conftest.py` provides the `app`/`client` fixtures and an autouse fixture that stubs `get_supabase_client` in every blueprint, so route tests never attempt a real Supabase connection.

## Project layout

```
app/
├── blueprints/<screen>/    routes.py (+ forms.py for create/edit screens)
├── services/               business logic
├── repositories/           supabase-py wrappers (the test-mocking seam)
├── templates/              Jinja2, one folder per screen + shared base/partials
├── constants.py            shared option lists (statuses, sources, etc.)
├── extensions.py           Supabase client + ML model/metrics loaders
└── config.py                env-var-backed Config
ml/
├── features.py             shared feature engineering (train + inference)
├── train_model.py          pulls data from Supabase, trains, evaluates, saves
├── model.joblib             trained pipeline (generated)
└── metrics.json             real held-out-test metrics (generated)
scripts/
├── generate_synthetic_data.py   synthetic courses/leads/registrations -> data/synthetic/*.csv
└── seed_supabase.py             loads those CSVs into Supabase
supabase/
├── schema.sql               DDL (source of truth)
└── migrations/               the same DDL, tracked as a Supabase migration
tests/                       pytest suite (see Testing above)
data/synthetic/               generated CSVs
docs/                         the functional specification
```
