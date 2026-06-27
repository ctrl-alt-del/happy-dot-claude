# Sprint Planning Notes — June 20, 2026

## Attendees
Alice (Tech Lead), Bob (Frontend), Carlos (Backend), Diana (Design), Ethan (PM)

## Agenda and Notes

### 1. Dark Mode Toggle
- Diana: mockups are done, shared in Figma (link: figma.com/design/darkmode-v3)
- The toggle should be in Settings → Appearance, not in the top nav like the old design had
- Alice: we should use CSS custom properties for color tokens, not hardcoded hex values — we already have a `tokens.css` with light mode defined, dark mode just needs the alternate values
- Bob: the toggle should persist across page reloads, use localStorage with a `theme` key
- Ethan: is this a P1 or P2? → Diana says P1, our user survey showed 68% want dark mode
- Alice: let's also handle `prefers-color-scheme` media query so the default matches the OS
- Carlos: backend doesn't need changes for this, it's purely frontend

### 2. Search Autocomplete
- Bob: I started a spike branch for the search autocomplete feature
- Should query the backend after the user has typed 3+ characters
- Debounce the input by 300ms so we don't hammer the API
- Dropdown should show top 5 results with highlighted match text
- Carlos: the `/api/search?q=` endpoint already exists from the v1.3 release, it returns `{ results: [{ id, title, snippet }] }` with a 200ms SLA
- Diana: dropdown should look like the sketch in slack #design-search — rounded corners, subtle shadow, 8px padding per item
- Ethan: ship this before the newsletter feature because Marketing is asking for it for their campaign launch on July 15
- Alice: what about keyboard navigation? Arrow keys to move, Enter to select, Escape to close — standard pattern
- Bob: also we need to handle the loading state and the "no results" empty state
- Diana: empty state should say "No matches found" in muted text, not just a blank dropdown

### 3. Newsletter Feature
- Ethan: Marketing wants a weekly newsletter signup form on the landing page
- Just email field + submit button for MVP
- Need GDPR consent checkbox (required, pre-ticked = illegal, so unchecked by default)
- Carlos: I'll add a `POST /api/newsletter/subscribe` endpoint, body: `{ email, consent: boolean }`, returns 201
- Duplicate email = return 409 Conflict with message "Already subscribed"
- Rate limit: max 3 requests per IP per hour
- Alice: frontend should validate email format before submitting
- Diana: the form should be below the hero section, not in a modal — modals tested poorly with our user demographic
- Ethan: this is P2, can ship after search autocomplete

### 4. Misc / Parking Lot
- Alice: we need to upgrade React from 18.2 to 18.3 soon, there's a hydration fix we need
- Carlos: the staging DB needs the migration from last sprint applied before QA can test anything
- Ethan: Q3 planning meeting is next Tuesday at 2pm, everyone should have their feature proposals in by Monday EOD

## Action Items
- [ ] Diana: finalize dark mode Figma specs → by June 22
- [ ] Bob: finish search spike and share branch → by June 23
- [ ] Carlos: create newsletter endpoint ticket in Jira → by June 21
- [ ] Alice: review React 18.3 changelog → by June 24
