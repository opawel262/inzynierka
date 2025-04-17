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
- [ ] User profile management
- [ ] budget management
- [ ] invest maangement
- [ ] Integrate cryptocurrency prices API (coingecko coincap)
- [ ] Add redis (for handling websockets/http for crypto prices)
- [ ] Implement WebSockets for real-time monitoring of cryptocurrency

## Bug and issue Fixes

- [ ] fix issue with reseting password via access token and password, not working and i don't have idea why
- [ ] fix issue with loading version of module bcrypt
- [x] fix issue (not updating new password) with reset password via Email
- [x] fix issue with jwt when access_token expire it return weird response change it!!!
- [x] refresh token endpoint not working

## Documentation

- [ ] Update README file
