# TODO List

## Project Setup

- [x] Initialize Git repository
- [x] Set up project structure
- [x] Configure linter and formatter

## TODO

- [x] User authentication
- [x] Email system - (confirm user via email, reset password via mail)
- [x] Configure testing environment for app
- [x] Implement email rate limiter (limit email sends to once per 30 minutes per endpoint)
- [x] Add rate limiter for all API endpoints
- [x] User profile management
- [ ] Budget management

  - [x] GET /api/budgets — pobierz wszystkie budżety użytkownika
  - [x] POST /api/budgets — utwórz nowy budżet
  - [x] GET /api/budgets/{budget_id} — szczegóły jednego budżetu
  - [x] PATCH /api/budgets/{budget_id} — edytuj budżet
  - [x] DELETE /api/budgets/{budget_id} — usuń budżet

  - [ ] GET /api/budgets/{budget_id}/summary — podsumowanie pewnie jakies info jak do raportu tylko mniej szczegolowe nwm

  - [ ] GET /api/budgets/{budget_id}/report/pdf — jakis koks raporcik
  - [ ] GET /api/budgets/{budget_id}/export/csv — eksportuj dane do CSV
  - [ ] GET /api/budgets/{budget_id}/export/excel — eksportuj dane do Excela (XLSX)

  - [ ] GET /api/budgets/{budget_id}/transactions — lista transakcji w budżecie
  - [ ] POST /api/budgets/{budget_id}/transactions — dodaj transakcję
  - [ ] GET /api/budgets/{budget_id}/transactions/{transaction_id} — szczegóły transakcji
  - [ ] PATCH /api/budgets/{budget_id}/transactions/{transaction_id} — edytuj transakcję
  - [ ] DELETE /api/budgets/{budget_id}/transactions/{transaction_id} — usuń transakcję

- [ ] Integrate cryptocurrency prices API (coingecko coincap)
- [ ] Add redis (for handling websockets/http for crypto prices)
- [ ] Implement WebSockets for real-time monitoring of cryptocurrency

## Bug and issue Fixes

- [ ] fix issue with reseting password via access token and password, not working and i don't have idea why
- [x] fix issue with loading version of module bcrypt
- [x] fix issue (not updating new password) with reset password via Email
- [x] fix issue with jwt when access_token expire it return weird response change it!!!
- [x] refresh token endpoint not working

## Extra Notes for Project Features

- Enhance category details by adding attributes such as type ("basic", "daily", "other") and classification (e.g., "income" or "expense") to improve category search and filtering.

## Documentation

- [ ] Update README file
- [ ] Diagram ERD (add title to budget and budgetransaction entity)
