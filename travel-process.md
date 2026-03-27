# Travel Management Process

## Overview

Noah manages Simon's travel bookings, reminders, and trip support. This document outlines the full process.

---

## 1. Booking Intake

**How it works:**
- Simon forwards travel confirmation emails to your-assistant-email@gmail.com
- **Subject line convention:** Simon prefixes with `(TRAVEL)` - e.g., "(TRAVEL) Fwd: Flight Confirmation"
- Accepts: flights, hotels, Airbnbs, car rentals, trains, etc.
- Sources: Amex Travel, airlines, Airbnb, booking.com, etc.

**Processing schedule:**
- Email check runs 3x daily (6am, 10am, 2pm ET via `email-check` cron)
- `daily-travel-check` runs at 5am ET to scan for upcoming trips

**When I find a travel booking, I:**
1. Extract **all** details (dates, times, confirmation codes, airlines, flight numbers, terminals, etc.)
2. Create entry in **Notion Travel Management database** with:
   - Name (descriptive title with flight number if applicable)
   - Travel Dates (single date for flights, date range for accommodations)
   - Type (Flight or Accommodation)
   - Confirmation Number
   - Destination
3. Create **calendar events** with proper times (not all-day for flights)
4. For roundtrips: create **two separate entries + two calendar events** (outbound + return)
5. If details are missing → **ask Simon** rather than creating incomplete entries

---

## 2. Where Things Live

| What | Where |
|------|-------|
| Booking details | Notion → **Travel Management database** |
| Calendar events | your-assistant-email@gmail.com (synced to Simon's calendars) |
| Travel documents | TBD - secure storage for passport, insurance, etc. |

### Travel Management Database Schema

| Field | Type | Description |
|-------|------|-------------|
| Name | Title | Booking description (e.g., "Air Canada: Toronto → Mexico City (AC991)") |
| Travel Dates | Date | Start date (and end date for accommodations) |
| Type | Select | `Flight` or `Accommodation` |
| Confirmation Number | Text | Booking reference code(s) |
| Destination | Text | Destination city/location |

**How to add entries:**
- Use `database_id`: `2f744b5e-ebe5-8076-81f6-c59f1a289db7`
- One entry per booking (separate entries for outbound/return flights)
- Include flight numbers in Name field for flights
- Use date ranges for accommodations (check-in to check-out)

---

## 3. Pre-Trip Reminders

| When | What I Send |
|------|-------------|
| **7 days before** | Pre-trip checklist (packing, tasks to complete before leaving) |
| **3 days before** | Verify all bookings are confirmed, **include weather forecast for destination**, flag any issues |
| **24 hours before** | Check-in reminders, flight details, weather at destination |
| **Day of travel** | Departure time, terminal, confirmation codes, real-time flight updates |

---

## 4. During-Trip Support

- **Daily morning briefs** with the day's agenda
- **Location info**: nearest pharmacy, grocery store, hospital, etc.
- **Weather alerts** for destination
- **Flight status monitoring** for any delays or changes

---

## 5. Travel Document Management

- Keep digital copies of:
  - Passport
  - Travel insurance
  - Vaccination records (if needed)
  - Visa documents
  - Emergency contacts
- Organize by trip in secure storage
- Quick access when needed

---

## 6. Relevant Cron Jobs

| Job | Schedule (UTC) | Purpose |
|-----|----------------|---------|
| `email-check` | 10am, 2pm, 6pm | Check emails + process travel confirmations |
| `daily-travel-check` | 9am | Scan calendar for upcoming travel, send reminders |
| `morning-brief` | 7am | Daily brief (includes travel if applicable) |

---

## 7. Key Principles

1. **Complete information** — Always capture full details, ask if something's missing
2. **Two events for roundtrips** — Outbound and return flights are separate calendar events
3. **Proactive reminders** — Don't wait to be asked; surface important info ahead of time
4. **Real-time updates** — Monitor for flight changes on travel days
5. **Single source of truth** — Notion has the details, calendar has the schedule

---

*Last updated: 2026-01-29 (Updated to use Travel Management database)*
