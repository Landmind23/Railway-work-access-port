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

1. Edit `/home/runner/work/Railway-work-access-port/Railway-work-access-port/sources.json` with source websites or feeds:
   - `publishing_entity`
   - `website`
   - `url`
2. Run the scanner:

```bash
python /home/runner/work/Railway-work-access-port/Railway-work-access-port/opportunity_scanner.py \
  --sources /home/runner/work/Railway-work-access-port/Railway-work-access-port/sources.json \
  --output /home/runner/work/Railway-work-access-port/Railway-work-access-port/output/railway_opportunities.csv
```

3. Open the generated CSV in Excel or any CSV-compatible tool.

## Testing

```bash
python -m unittest discover -s /home/runner/work/Railway-work-access-port/Railway-work-access-port/tests -v
```
