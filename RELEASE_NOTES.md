# bos-auto

 * Support for dynamic markets which come with their own triggers and
   allow later setting up of betting market groups according to a
   dynamic metric, such as *handicap* and *overunder* values.
 * Support for cancel events.
 * Improve API endpoint responses when taking incidents from data proxy
 * Massive improvements in unit testing and coverage.
 * Fix leadtime_max so that events are created at a later point in time.
 * Improve code structure and documentation.
 * Scheduler moved into API

## Changelog

 * [26a15e5](https://github.com/PBSA/bos-auto/commit/26a15e5) cleanup bos-auto cli
 * [4de7243](https://github.com/PBSA/bos-auto/commit/4de7243) use proper log method
 * [6b23f3c](https://github.com/PBSA/bos-auto/commit/6b23f3c) proper name for cancel trigger
 * [af84f89](https://github.com/PBSA/bos-auto/commit/af84f89) do not throw exception in this case
 * [35443d6](https://github.com/PBSA/bos-auto/commit/35443d6) proper use of comparators
 * [07665ec](https://github.com/PBSA/bos-auto/commit/07665ec) add new config to MANIFEST
 * [8740fa0](https://github.com/PBSA/bos-auto/commit/8740fa0) fix unittests and add docs
 * [8910232](https://github.com/PBSA/bos-auto/commit/8910232) Allow to define approver and proposer in cli.py
 * [24f982a](https://github.com/PBSA/bos-auto/commit/24f982a) improve triggers
 * [9441e5f](https://github.com/PBSA/bos-auto/commit/9441e5f) Default config in file
 * [f230aae](https://github.com/PBSA/bos-auto/commit/f230aae) new call to list postponed incidents
 * [51892e4](https://github.com/PBSA/bos-auto/commit/51892e4) new bookiesports syntax
 * [2baf292](https://github.com/PBSA/bos-auto/commit/2baf292) Automatically start scheduler in API call
 * [c01620b](https://github.com/PBSA/bos-auto/commit/c01620b) Unit tests passing
 * [fadc27d](https://github.com/PBSA/bos-auto/commit/fadc27d) Create and approve dynamic BMGs with fuzzy value
 * [99eb04f](https://github.com/PBSA/bos-auto/commit/99eb04f) Triggers and unittests
 * [00b216f](https://github.com/PBSA/bos-auto/commit/00b216f) cleanup
 * [a978751](https://github.com/PBSA/bos-auto/commit/a978751) use bos-incidents validator
 * [72b2d35](https://github.com/PBSA/bos-auto/commit/72b2d35) unify unittests with fixtures
 * [69ac74f](https://github.com/PBSA/bos-auto/commit/69ac74f) Cancel trigger
 * [2c4df61](https://github.com/PBSA/bos-auto/commit/2c4df61) Cleanup unit tests
 * [38ba7bf](https://github.com/PBSA/bos-auto/commit/38ba7bf) bug in logging
 * [30e38b4](https://github.com/PBSA/bos-auto/commit/30e38b4) add timing to worker check scheduled also intial with executor add more configurable logging
 * [76d1aaf](https://github.com/PBSA/bos-auto/commit/76d1aaf) adjust docs title level
 * [d9a88d4](https://github.com/PBSA/bos-auto/commit/d9a88d4) triggers must react on distict hashes add more versions to isalive
 * [5b6a5b0](https://github.com/PBSA/bos-auto/commit/5b6a5b0) Allow a None whisle_time
 * [de2b2af](https://github.com/PBSA/bos-auto/commit/de2b2af) Make 503 a bad request (400)


# bos-sync 

 * Support for dynamic markets which come with their own triggers and
   allow later setting up of betting market groups according to a
   dynamic metric, such as *handicap* and *overunder* values.
 * Add fuzzy logic matcher to allow resolving dynamic markets within
   given boundaries.
 * Support for cancel events.
 * Improvements to substitutes for BMG/BM names and result metric
   computation.
 * Start time is compared in case of setting up an event so that teams
   can play against each other multiple times per season.
 * Massive improvements in unit testing and coverage.
 * Fix leadtime_max so that events are created at a later point in time.
 * Improve code structure and documentation.
 * Unified comparators for fuzzy logic.
 * Allow for two kinds of handicap values (integer and floats).

## Changelog

 * [12a36b5](https://github.com/PBSA/bos-sync/commit/12a36b5) Enable floating point handicap scheme by default
 * [df2f8b4](https://github.com/PBSA/bos-sync/commit/df2f8b4) Add new parameter to allow for floating handicaps, add unit tests
 * [199cb66](https://github.com/PBSA/bos-sync/commit/199cb66) add correct display name
 * [7a69754](https://github.com/PBSA/bos-sync/commit/7a69754) add ou .5 values
 * [3a82f7d](https://github.com/PBSA/bos-sync/commit/3a82f7d) Add more docs
 * [0edf974](https://github.com/PBSA/bos-sync/commit/0edf974) Fix unit tests
 * [6cc2ddc](https://github.com/PBSA/bos-sync/commit/6cc2ddc) Unify the use of comparators
 * [7254199](https://github.com/PBSA/bos-sync/commit/7254199) add docs
 * [74e2853](https://github.com/PBSA/bos-sync/commit/74e2853) Deal with rounding for over/under differently
 * [37cd4a9](https://github.com/PBSA/bos-sync/commit/37cd4a9) added doc
 * [b1dae45](https://github.com/PBSA/bos-sync/commit/b1dae45) Round to next .5 overunder
 * [042c170](https://github.com/PBSA/bos-sync/commit/042c170) fix issue with 0 values
 * [05372e3](https://github.com/PBSA/bos-sync/commit/05372e3) new bookiesports syntax
 * [9347499](https://github.com/PBSA/bos-sync/commit/9347499) Unit tests passing
 * [193b4a2](https://github.com/PBSA/bos-sync/commit/193b4a2) move code
 * [7689683](https://github.com/PBSA/bos-sync/commit/7689683) unify bettingmarket and bettingmarket groups
 * [c538bd2](https://github.com/PBSA/bos-sync/commit/c538bd2) Add fuzzy tests
 * [42ec46d](https://github.com/PBSA/bos-sync/commit/42ec46d) move code
 * [ad79b7d](https://github.com/PBSA/bos-sync/commit/ad79b7d) Migrate tests for BMGs to separate static methods and implement fuzzy checker
 * [4c1d9c5](https://github.com/PBSA/bos-sync/commit/4c1d9c5) complete overunder dynamic betting markets
 * [23201a8](https://github.com/PBSA/bos-sync/commit/23201a8) initial work for overunder
 * [9e0ead7](https://github.com/PBSA/bos-sync/commit/9e0ead7) cleanup substitutions
 * [8f3b625](https://github.com/PBSA/bos-sync/commit/8f3b625) identify sport and eventgroup through identifier instead of english name
 * [dead785](https://github.com/PBSA/bos-sync/commit/dead785) initial work for dynamic betting markets
 * [6073f51](https://github.com/PBSA/bos-sync/commit/6073f51) more cleanup
 * [aa4902f](https://github.com/PBSA/bos-sync/commit/aa4902f) cleanup
 * [23606d8](https://github.com/PBSA/bos-sync/commit/23606d8) improvements on unit tests with fixtures
 * [db9dfef](https://github.com/PBSA/bos-sync/commit/db9dfef) fix unit tests for status updates
 * [d3cd7fe](https://github.com/PBSA/bos-sync/commit/d3cd7fe) Improve find_id for Event()
 * [4ca99a2](https://github.com/PBSA/bos-sync/commit/4ca99a2) Improve unit test around leadtime_Max
 * [87c0e0f](https://github.com/PBSA/bos-sync/commit/87c0e0f) another attempt to fix behavior of leadtime_Max
 * [9b3dcad](https://github.com/PBSA/bos-sync/commit/9b3dcad) Update Unit tests
 * [82a75db](https://github.com/PBSA/bos-sync/commit/82a75db) Improve testing
 * [8d4b055](https://github.com/PBSA/bos-sync/commit/8d4b055) Disable testing of season
 * [987d8f6](https://github.com/PBSA/bos-sync/commit/987d8f6) new test to make sure it approves a pending proposal
 * [51271ac](https://github.com/PBSA/bos-sync/commit/51271ac) Compare start_times to allow teams to play against each other multiple times per season

# python-peerplays

 * Show proposer in proposals
 * Implement missing operations for bos-sync operations
 * Support for HTTPs
 * Refactor Caching to improve bos-sync/bos-auto processing speed
 * Make PasswordKey compatible with Core-UI
 * Implement Tournaments and RPS
 * Major improvement to coverage and documentation
 * Many fixes

## Changelog

 * [ec537c4](https://github.com/PBSA/python-peerplays/commit/ec537c4) (origin/develop) Allow claiming of genesis balance
 * [7801359](https://github.com/PBSA/python-peerplays/commit/7801359) claim balance operation and test
 * [8ea557c](https://github.com/PBSA/python-peerplays/commit/8ea557c) change default node for Alice network
 * [3817aba](https://github.com/PBSA/python-peerplays/commit/3817aba) Use new Graphene API interface
 * [1c6175e](https://github.com/PBSA/python-peerplays/commit/1c6175e) Fix Alice compatibility
 * [0d503be](https://github.com/PBSA/python-peerplays/commit/0d503be) fix expiration
 * [5fa74d8](https://github.com/PBSA/python-peerplays/commit/5fa74d8) Fix Alice compatibility
 * [4cc1b5a](https://github.com/PBSA/python-peerplays/commit/4cc1b5a) fix expiration
 * [68984db](https://github.com/PBSA/python-peerplays/commit/68984db) (origin/add_id_to_asset) Added the id of the asset as a property of the asset object.
 * [3093af0](https://github.com/PBSA/python-peerplays/commit/3093af0) Allow fee defined as symbol
 * [3e41a48](https://github.com/PBSA/python-peerplays/commit/3e41a48) Fix account_creation issue with keys
 * [7233a89](https://github.com/PBSA/python-peerplays/commit/7233a89) Fix asset_fee declaration
 * [030c717](https://github.com/PBSA/python-peerplays/commit/030c717) general improvments
 * [8e1f6a4](https://github.com/PBSA/python-peerplays/commit/8e1f6a4) Fix unittests
 * [9d44d33](https://github.com/PBSA/python-peerplays/commit/9d44d33) Do not update status if not changing
 * [265bcdb](https://github.com/PBSA/python-peerplays/commit/265bcdb) fix RST->MD in readme.md
 * [1daade4](https://github.com/PBSA/python-peerplays/commit/1daade4) added new docs
 * [e795f5c](https://github.com/PBSA/python-peerplays/commit/e795f5c) update test
 * [049bcaa](https://github.com/PBSA/python-peerplays/commit/049bcaa) Fixes and better unit testing
 * [1437323](https://github.com/PBSA/python-peerplays/commit/1437323) Fix clear transaction issue and allow defining of fee_asset
 * [bd81dcf](https://github.com/PBSA/python-peerplays/commit/bd81dcf) Fix unecessary signature issue
 * [d14cc9e](https://github.com/PBSA/python-peerplays/commit/d14cc9e) New chain-id for charlie
 * [6996836](https://github.com/PBSA/python-peerplays/commit/6996836) Allow change the memo key
 * [772b08b](https://github.com/PBSA/python-peerplays/commit/772b08b) Add 'blockchain' attribute to context
 * [4a51c19](https://github.com/PBSA/python-peerplays/commit/4a51c19) use a different default API endpoint
 * [3fb585d](https://github.com/PBSA/python-peerplays/commit/3fb585d) Update of known chains
 * [44c1a6d](https://github.com/PBSA/python-peerplays/commit/44c1a6d) New method to set the blocking boolean variable
 * [39ad073](https://github.com/PBSA/python-peerplays/commit/39ad073) even more caching
 * [3b8b3b3](https://github.com/PBSA/python-peerplays/commit/3b8b3b3) Improve speed by additional caching
 * [6b13f29](https://github.com/PBSA/python-peerplays/commit/6b13f29) (origin/documentation) Added a description for the library.
 * [7956283](https://github.com/PBSA/python-peerplays/commit/7956283) Remove lazy since we already have the entire object
 * [da1deb4](https://github.com/PBSA/python-peerplays/commit/da1deb4) more caching
 * [f4e2739](https://github.com/PBSA/python-peerplays/commit/f4e2739) introduce bm caching
 * [88a431c](https://github.com/PBSA/python-peerplays/commit/88a431c) introduce proposals caching
 * [03211d3](https://github.com/PBSA/python-peerplays/commit/03211d3) properly use new naming scheme
 * [d179d60](https://github.com/PBSA/python-peerplays/commit/d179d60) Reduce grading time
 * [2d30647](https://github.com/PBSA/python-peerplays/commit/2d30647) fix unrequired parameters
 * [0ec910f](https://github.com/PBSA/python-peerplays/commit/0ec910f) Ensure to set config from BlockchainInstance
 * [eadbaf6](https://github.com/PBSA/python-peerplays/commit/eadbaf6) new default backend API
 * [a937f5a](https://github.com/PBSA/python-peerplays/commit/a937f5a) New charliechain id
 * [a53f581](https://github.com/PBSA/python-peerplays/commit/a53f581) Migrate improvements from bitshares
 * [1f5e479](https://github.com/PBSA/python-peerplays/commit/1f5e479) (origin/feature/charlie-compatibility) compatibility with baxter and charlie
 * [17e40fa](https://github.com/PBSA/python-peerplays/commit/17e40fa) Implement tournaments and RPS
 * [2f1fa56](https://github.com/PBSA/python-peerplays/commit/2f1fa56) Allow for simpler changing of status and resolving
 * [e27781d](https://github.com/PBSA/python-peerplays/commit/e27781d) fix unit test errors
 * [ac3a13b](https://github.com/PBSA/python-peerplays/commit/ac3a13b) [account] make PasswordKey compatible with core-ui
 * [be469ea](https://github.com/PBSA/python-peerplays/commit/be469ea) [fix] syntax error in python3.5
 * [659651e](https://github.com/PBSA/python-peerplays/commit/659651e) [docs] Add docs for cli.rpc
 * [6f2a9da](https://github.com/PBSA/python-peerplays/commit/6f2a9da) Refactoring to use BlockchainInstance
 * [d28b678](https://github.com/PBSA/python-peerplays/commit/d28b678) Improve unittesting capabilities
 * [bf2e61a](https://github.com/PBSA/python-peerplays/commit/bf2e61a) Added Charlie to the list of known chains
 * [e7fe127](https://github.com/PBSA/python-peerplays/commit/e7fe127) [witnesses] filter by active witnesses
 * [cb31af7](https://github.com/PBSA/python-peerplays/commit/cb31af7) [cli] sport is optional parameter
 * [4e09f27](https://github.com/PBSA/python-peerplays/commit/4e09f27) fix unit test
 * [a8e014a](https://github.com/PBSA/python-peerplays/commit/a8e014a) fix unit test
 * [5018b94](https://github.com/PBSA/python-peerplays/commit/5018b94) [witness] implement __contains__
 * [d931ce4](https://github.com/PBSA/python-peerplays/commit/d931ce4) bookie list all command line extension
 * [5adada4](https://github.com/PBSA/python-peerplays/commit/5adada4) store pretty_print in ui module
 * [cf8107e](https://github.com/PBSA/python-peerplays/commit/cf8107e) replace bitshares
 * [c26c315](https://github.com/PBSA/python-peerplays/commit/c26c315) temporary disable test until network ready
 * [253ef5a](https://github.com/PBSA/python-peerplays/commit/253ef5a) [chache] fix clearing of cache
 * [d0337bb](https://github.com/PBSA/python-peerplays/commit/d0337bb) Properly set heritance
 * [69bd20f](https://github.com/PBSA/python-peerplays/commit/69bd20f) Allow createwallet and unlock from main class
 * [6c3ffe2](https://github.com/PBSA/python-peerplays/commit/6c3ffe2) fix bug in get_pubkey
 * [fbd51aa](https://github.com/PBSA/python-peerplays/commit/fbd51aa) [wallet] Allow to wipe the wallet
 * [31c2c53](https://github.com/PBSA/python-peerplays/commit/31c2c53) Loop for providing passphrase
 * [ffa90f7](https://github.com/PBSA/python-peerplays/commit/ffa90f7) [cli] allow to specify a proposer
 * [f2ad220](https://github.com/PBSA/python-peerplays/commit/f2ad220) [cli] show proposal approvers per name
 * [277c48b](https://github.com/PBSA/python-peerplays/commit/277c48b) [cli] use new scheme everywhere
 * [25852e5](https://github.com/PBSA/python-peerplays/commit/25852e5) [cli] improvements
 * [ae184a2](https://github.com/PBSA/python-peerplays/commit/ae184a2) add RPC file
 * [a280feb](https://github.com/PBSA/python-peerplays/commit/a280feb) Support HTTP(S) endpoints via HTTP/RPC
 * [139e172](https://github.com/PBSA/python-peerplays/commit/139e172) [peerplays] Fix bet_place mulitplier
 * [4006af9](https://github.com/PBSA/python-peerplays/commit/4006af9) re-order kwargs
 * [6bb0487](https://github.com/PBSA/python-peerplays/commit/6bb0487) Fix missing instance handover
 * [e3f709d](https://github.com/PBSA/python-peerplays/commit/e3f709d) do not fail if 'trx' does not exist
 * [db596fe](https://github.com/PBSA/python-peerplays/commit/db596fe) fix proposer signing
 * [9881f53](https://github.com/PBSA/python-peerplays/commit/9881f53) set default node to alpha network
 * [1086d47](https://github.com/PBSA/python-peerplays/commit/1086d47) Use proposer to sign a proposal and not the account
 * [3664ea1](https://github.com/PBSA/python-peerplays/commit/3664ea1) Fix Unittest for event_update
 * [2fd4396](https://github.com/PBSA/python-peerplays/commit/2fd4396) status -> new_status
 * [fb7c1c3](https://github.com/PBSA/python-peerplays/commit/fb7c1c3) import as to avoid dependency loops
 * [c17e77f](https://github.com/PBSA/python-peerplays/commit/c17e77f) sync blockchain monitor class with bitshares
 * [8cfacae](https://github.com/PBSA/python-peerplays/commit/8cfacae) reworked shared instance and add clear_cache
 * [2d27b60](https://github.com/PBSA/python-peerplays/commit/2d27b60) Use empty string as default for scroes
 * [dfec98e](https://github.com/PBSA/python-peerplays/commit/dfec98e) [peerplays] add call to execute event_update_status
 * [c4a0aff](https://github.com/PBSA/python-peerplays/commit/c4a0aff) Add new operation for Update_event_status and unit tests after blockchain forked
 * [f768f6d](https://github.com/PBSA/python-peerplays/commit/f768f6d) do not try to build with python3.7
 * [2eb6500](https://github.com/PBSA/python-peerplays/commit/2eb6500) [travis] try tox-travis
 * [be28450](https://github.com/PBSA/python-peerplays/commit/be28450) [travis] try fix a bug that causes tests to break
 * [2558d36](https://github.com/PBSA/python-peerplays/commit/2558d36) [docs] improve documentation
 * [c421480](https://github.com/PBSA/python-peerplays/commit/c421480) [peerplays] properly make use of new enumerators
 * [6f36715](https://github.com/PBSA/python-peerplays/commit/6f36715) [tests] do not run tests against cli-wallet by default
 * [a9ccfd3](https://github.com/PBSA/python-peerplays/commit/a9ccfd3) [docs] auto compile documents
 * [b1f60a5](https://github.com/PBSA/python-peerplays/commit/b1f60a5) [status enumerators] Updated operations to reflect status enumerators properly
 * [e23deb2](https://github.com/PBSA/python-peerplays/commit/e23deb2) add new testnet chainid
 * [6c46702](https://github.com/PBSA/python-peerplays/commit/6c46702) [cli] proposals shows proposer as name
 * [9cee101](https://github.com/PBSA/python-peerplays/commit/9cee101) [wallet] cleanups and better error handling
