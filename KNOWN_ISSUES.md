# Known Issues and Findings

This document tracks known limitations of the current build and the data-quality
findings surfaced while working with the example catalog. It complements the
design rationale in the README.

## Known limitations

- **No storefront automated tests.** The API enforces 100% line coverage, but the
  React storefront is currently validated only through its production build in CI.
  Component and end-to-end tests are the natural next addition.
- **Authentication and authorization are out of scope.** All endpoints are open.
  A real deployment would put the catalog write operations and checkout behind
  authenticated sessions and role checks.
- **Payment is a stub.** The checkout flow returns a fake payment reference behind
  the same service boundary a real provider would occupy. No external charge is made.
- **Product text is stored verbatim.** Import validates length and required fields
  but does not strip or transform HTML in names and descriptions. This is safe in
  the current surfaces because React escapes output on render and all database
  access is parameterized through SQLAlchemy, so stored markup or SQL-like strings
  are treated as inert data. If product text were ever rendered as raw HTML or
  interpolated into a query, sanitization would need to be added at that boundary.
- **Deleting a purchased product is blocked by design.** A product referenced by an
  existing order cannot be deleted; the foreign key surfaces as a `409 Conflict`
  with a clear message rather than cascading and erasing order history.

## Data-quality findings

The example catalog intentionally contains malformed and adversarial rows. Import
treats bad rows as data rather than failures: each row is validated on its own and
the endpoint returns a per-row report instead of rejecting the whole file. The rows
below confirm that behavior end to end.

| Row (by SKU or name)                     | Issue                          | Import result                                   |
| ---------------------------------------- | ------------------------------ | ----------------------------------------------- |
| `YM-015` Yoga Mat                        | Price is the word `free`       | Rejected: price is not a valid number           |
| `DL-007` Desk Lamp                       | Stock is `-5`                  | Rejected: stock must not be negative            |
| `HD-099` (blank name)                    | Required name is empty         | Rejected: name is required                      |
| `<script>alert('xss')</script>` XS-001   | Script markup in the name      | Stored verbatim, escaped on render              |
| `Robert'); DROP TABLE products;--` SQL-001 | SQL-injection style name     | Stored verbatim, queries are parameterized      |
| `BS-021` Bluetooth Speaker (appears twice) | Duplicate SKU                | Upserted, last write wins                       |
| `QI-001` Quote "Inside" Name             | Escaped quotes in the name     | Parsed correctly by the CSV reader              |
| Fully empty rows                         | All columns blank              | Skipped without an error                        |

Prices accept a leading currency symbol and thousands separators before being stored
as `Numeric`. Weight is optional and category is optional; both are accepted as blank.
