# Contributing to CivicShield

## Adding Venue Data
Edit `hotels.json` — each entry needs:
```json
{
  "id": "unique-id",
  "name": "Venue Name",
  "area": "Hyderabad area",
  "lat": 17.xxxx,
  "lng": 78.xxxx,
  "category": "restaurant|hotel|cafe",
  "fssai": "license-number-or-null",
  "rating": 0-5,
  "reports": []
}
```

## Reporting Logic
Anonymous reports are stored client-side. Inspector audits require a passcode.
