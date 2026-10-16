# `harvey` data package

Legal tasks in the style of Harvey's Legal Agent Benchmark. See `FORMAT.md` for the task format
and `package.yaml` for acceptance constraints (>= 10 binary criteria, reference models < 75%
criteria pass rate, lawyer QA >= 70%).

| task | practice area | edge case |
|---|---|---|
| `tasks/caa-gag-clause-deidentified-claims-access` | ERISA / health & welfare, CAA 2021 transparency | ERISA § 724 bars agreements restricting electronic access to de-identified claims data but prescribes no format, mechanism or price; when do fees, lags, formats and consent rights become a "direct or indirect" restriction? |

Research candidates produced by `envlab research` land in `candidates/` and are promoted into
`tasks/` with `envlab promote`.
