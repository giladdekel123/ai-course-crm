# AI Course CRM

Flask + Supabase CRM for tracking AI-course leads from first contact through enrollment and payment, with an ML tab predicting purchase probability. See `docs/` for the full specification.

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # fill in SUPABASE_URL / SUPABASE_SERVICE_KEY
```

Apply `supabase/schema.sql` in the Supabase SQL editor (or via the CLI) against your project before running the app, then seed and train:

```
python -m scripts.generate_synthetic_data
python -m scripts.seed_supabase
python -m ml.train_model
```

```
flask --app wsgi run --debug
```

## Layout

- `app/` — Flask application (blueprints per screen, services, repositories, templates)
- `ml/` — model training script, feature engineering, trained model + metrics
- `scripts/` — synthetic data generation and Supabase seeding
- `supabase/schema.sql` — database schema
- `tests/` — pytest suite
