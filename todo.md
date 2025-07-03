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

  - [x] GET /api/budgets/{budget_id}/categories — wyświetl wszystkie kategorie w budżecie
  - [ ] GET /api/budgets/{budget_id}/report/pdf — jakis koks raporcik
  - [ ] GET /api/budgets/{budget_id}/export/csv — eksportuj dane do CSV
  - [ ] GET /api/budgets/{budget_id}/export/excel — eksportuj dane do Excela (XLSX)

  - [x] GET /api/budgets/{budget_id}/transactions — lista transakcji w budżecie
  - [x] POST /api/budgets/{budget_id}/transactions — dodaj transakcję
  - [x] GET /api/budgets/{budget_id}/transactions/{transaction_id} — szczegóły transakcji
  - [x] PATCH /api/budgets/{budget_id}/transactions/{transaction_id} — edytuj transakcję
  - [x] DELETE /api/budgets/{budget_id}/transactions/{transaction_id} — usuń transakcję

- [ ] Portfolio Management - STOCKS

  - [ ] GET /api/portfolios/stocks — lista portfeli akcji
  - [ ] POST /api/portfolios/stocks — utwórz nowy portfel akcji
  - [ ] GET /api/portfolios/stocks/{portfolio_id} — szczegóły portfela
  - [ ] PATCH /api/portfolios/stocks/{portfolio_id} — edytuj portfel
  - [ ] DELETE /api/portfolios/stocks/{portfolio_id} — usuń portfel

  - [ ] GET /api/portfolios/stocks/{portfolio_id}/transactions — lista transakcji
  - [ ] POST /api/portfolios/stocks/{portfolio_id}/transactions — dodaj transakcję
  - [ ] GET /api/portfolios/stocks/{portfolio_id}/transactions/{transaction_id} — szczegóły transakcji
  - [ ] PATCH /api/portfolios/stocks/{portfolio_id}/transactions/{transaction_id} — edytuj transakcję
  - [ ] DELETE /api/portfolios/stocks/{portfolio_id}/transactions/{transaction_id} — usuń transakcję
  - [ ] GET /api/assets/stocks/ — lista spółek z możliwością filtrowania/wyszukiwania (np. po nazwie, symbolu, sektorze)
  - [ ] GET /api/assets/stocks/{stock_id} — metadane spółki
  - [ ] GET /api/assets/stocks/{stock_id}/historical — historia cen spółki
  - [ ] GET /api/stocks/fields/metadata — metadane pól spółki (opis co znaczy beta, pe_ratio itd.)

- [ ] Portfolio Management - CRYPTOS

  - [ ] GET /api/portfolios/cryptos — lista portfeli krypto
  - [ ] POST /api/portfolios/cryptos — utwórz nowy portfel krypto
  - [ ] GET /api/portfolios/cryptos/{portfolio_id} — szczegóły portfela
  - [ ] PATCH /api/portfolios/cryptos/{portfolio_id} — edytuj portfel
  - [ ] DELETE /api/portfolios/cryptos/{portfolio_id} — usuń portfel

  - [ ] GET /api/portfolios/cryptos/{portfolio_id}/transactions — lista transakcji
  - [ ] POST /api/portfolios/cryptos/{portfolio_id}/transactions — dodaj transakcję
  - [ ] GET /api/portfolios/cryptos/{portfolio_id}/transactions/{transaction_id} — szczegóły transakcji
  - [ ] PATCH /api/portfolios/cryptos/{portfolio_id}/transactions/{transaction_id} — edytuj transakcję
  - [ ] DELETE /api/portfolios/cryptos/{portfolio_id}/transactions/{transaction_id} — usuń transakcję
  - [ ] GET /api/assets/cryptos/ - lista kryptowalut z możliwością filtrowania/wyszukiwania (np. po nazwie, symbolu, sektorze)
  - [ ] GET /api/assets/cryptos/{crypto_id} — informacje o kryptowalucie
  - [ ] GET /api/assets/cryptos/{crypto_id}/historical — historia cen kryptowaluty

- [ ] Integrate cryptocurrency info API (coingecko coincap)
- [ ] Integrate stocks info yfinanace
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
