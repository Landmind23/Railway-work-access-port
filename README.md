# Railway-work-access-port

Automates collection of railway-related tenders, business opportunities, and project publications related to Africa, then exports results into an Excel-compatible CSV datasheet.

## What it exports

The CSV includes:
- publishing entity
- website
- link
- contact numbers
- email
- project name
- duration
- currently open (Yes/No/Unknown)
- key players

## Usage

1. Edit `sources.json` with source websites or feeds:
   - `publishing_entity`
   - `website`
   - `url`
2. Run the scanner:

```bash
python opportunity_scanner.py \
  --sources sources.json \
  --output output/railway_opportunities.csv
```

3. Open the generated CSV in Excel or any CSV-compatible tool.

## Testing

```bash
python -m unittest discover -s tests -v
```
