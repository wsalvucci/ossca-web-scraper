# ossca-web-scraper
A web scraper for OSSCA soccer games at http://ossca.org/schedules.asp

Each `20XXData.json` file holds the year's information in the format:

```json
[
  {
    "year": 2003,
    "schoolSchedules": [
      {
        "id": 1,
        "name": "Olentangy (Lewis Center)",
        "schedule": [
          {
            "opponent": "Hilliard Davidson",
            "result": "W",
            "pointsFor": 1,
            "pointsAgainst": 0
          },
          ...
        ]
      },
      ...
    ]
  }
]
```
