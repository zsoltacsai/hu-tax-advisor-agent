# Phase 4.5 fresh legal-source review

Research was performed on 2026-10-08. Official-source URLs/content were revisited through EUR-Lex, European Commission Taxation and Customs Union, NAV, and the Nemzeti Jogszabálytár search index. URL reachability and legal-content verification are tracked separately in `sources/registry.json`. Direct EUR-Lex/NJT HTML access may present anti-bot or timeout responses; where that happened, the repository records the limitation rather than claiming direct-page access.

## Articles 44 and 45

EUR-Lex Directive 2006/112/EC, consolidated to 2025-04-14, supplies the current text. Article 44 applies to a taxable person acting as such and identifies the business seat, the relevant receiving fixed establishment, or a fallback residence. Article 45 applies to a non-taxable person and identifies the supplier business seat, a supplier fixed establishment from which the service is supplied, or a fallback residence. Directive 2008/8/EC, Article 2, applies its general service rules from 2010-01-01. European Commission guidance calls these the basic rules, stresses service nature/customer status, and lists exceptions including immovable property, transport, events and Article 58. NAV's 2026 filing instructions describe the Hungarian domestic general B2B/B2C place rules by reference to Áfa tv. 37. § (1)-(2).

The approved-candidate scope deliberately requires a human reviewed `GENERAL_SERVICE` label and special-rule screen. It only permits execution where the relevant fixed-establishment review explicitly returns `no_relevant_fixed_establishment`. It does not decide whether such an establishment exists or receives/dispatches a service. Customer status/location, supplier location and transaction date must each be supplied and reviewed. No VAT charging, reverse charge, tax point, invoice or reporting result follows from the place-of-supply stage.

## Articles 58 and 59c

Directive 2017/2455 introduced the Article 58 destination framework and Article 59c threshold mechanism from 2019. Article 58 requires a non-taxable customer and qualifying telecommunications, broadcasting or electronically supplied service; electronic communication alone is not sufficient. For 2026, Article 59c has supplier single-Member-State, cross-border B2C, current and previous calendar year aggregate threshold, and option conditions. Below-threshold/no-option situations displace Article 58. Directive (EU) 2025/516 amends Article 59c with effect from 2027-01-01. A separate effective-dated rule version will be necessary.

The current engine/schema cannot represent all of those Article 59c inputs faithfully. The fresh Article 58 snapshot and candidate are preserved, but the AI reviewer returns `NEEDS_CHANGES`. It cannot be approved based on the present assessment enum. WP CareGrid remains unclassified.

## Source access caveats

The official NJT search index displayed current-looking excerpts for Articles 37(1)-(2), but direct NJT access returned a timeout/502. Therefore the primary Hungarian source remains content-unverified in the source registry and is not cited as verified evidence in an executable rule. NAV guidance is an official interpretation/support source, not primary law. EUR-Lex indexed text was accessed for the exact relevant Articles and Directive 2008/8 commencement; the consolidated 2025 date is pinned explicitly. These checks verify the cited material as accessed in this research run and do not provide live monitoring after 2026-10-08.
