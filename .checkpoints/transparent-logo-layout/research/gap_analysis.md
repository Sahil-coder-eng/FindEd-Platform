# Gap Analysis — Education Loan Comparison Platform

## 1. Existing Solution Capability Matrix

The following matrix compares the capabilities of existing tools and platforms
with our prototype. This comparison is based on publicly observable features
as of September 2026.

| Capability | Bank EMI Calculators | Loan Aggregators (e.g., BankBazaar) | Vidya Lakshmi Portal | Our Prototype |
|---|:---:|:---:|:---:|:---:|
| Basic EMI Calculation | ✓ | ✓ | — | ✓ |
| Multiple Lender Comparison | — | ✓ (listing) | ✓ (listing) | ✓ (with analysis) |
| Full Amortization Schedule | Limited | Limited | — | ✓ |
| Amortization Visualization | — | — | — | ✓ |
| Moratorium Impact Analysis | — | Limited | — | ✓ |
| Interest Capitalization Simulator | — | — | — | ✓ |
| Total Cost (incl. fees) | — | Partial | — | ✓ |
| Scenario Comparison | — | — | — | ✓ |
| Interest Rate Sensitivity | — | — | — | ✓ |
| Tenure Sensitivity | — | — | — | ✓ |
| Education Cost Estimator | — | — | — | ✓ |
| Currency Conversion | — | — | — | ✓ |
| Exchange Rate Sensitivity | — | — | — | ✓ |
| Source Transparency (dated) | Varies | Varies | N/A | ✓ |
| Destination Updates | — | — | — | ✓ (sample) |
| Formula Explanation | Rare | Rare | — | ✓ |
| Open/Transparent Data | N/A | N/A | N/A | ✓ |

**Legend:**
- ✓ = Available
- — = Not available or not observed
- Limited = Partially available or basic version
- Varies = Depends on specific implementation

> **Note:** This matrix reflects publicly observable features. Some platforms
> may have additional capabilities behind login walls or in premium tiers.
> We do not claim these features are entirely absent from the market — only
> that the *combination* in a single transparent platform is the gap we address.

## 2. Key Gaps Identified

### Gap 1: Moratorium Impact Transparency
**Problem:** Most calculators compute EMI on the principal as-is, without
accounting for the moratorium period common to education loans.

**Impact:** Students do not realize that 4+ years of interest capitalization
can significantly inflate their effective principal and total cost.

**Our response:** Dedicated moratorium simulator with two modes (paid-during
vs. capitalized) and visual timeline.

### Gap 2: No Scenario / Sensitivity Analysis
**Problem:** Existing tools provide single-point outputs. Users cannot easily
explore "what if I choose 7 years instead of 10?" or "what if the rate is
0.5% higher?"

**Impact:** Students cannot make informed tradeoff decisions.

**Our response:** Full scenario comparison (up to 4 configurations) and
sensitivity analysis for both rate and tenure.

### Gap 3: Source & Data Transparency
**Problem:** Most platforms do not clearly indicate when rate data was collected,
from what source, or when it was last verified.

**Impact:** Users may make decisions based on outdated information.

**Our response:** Every lender record includes source URL and verification date.
Missing data is explicitly flagged.

### Gap 4: True Cost Visibility
**Problem:** Advertised interest rates do not reflect the full cost. Processing
fees, moratorium interest, and other charges are often omitted.

**Impact:** Students underestimate the total financial outflow.

**Our response:** Total cost calculator that aggregates known charges and
explicitly flags unavailable ones.

### Gap 5: Mathematical Transparency
**Problem:** Most calculators are "black boxes" — users enter numbers and get
an output without understanding the math.

**Impact:** Reduces financial literacy and trust.

**Our response:** "How is this calculated?" explainers with full formula
derivation and worked examples for every computation.

## 3. Novelty Statement

> Our novelty is **not** that we "invented an EMI calculator."
>
> Our proposed contribution is: **An integrated and transparent framework
> for comparing education-loan costs** that accounts for repayment schedules,
> moratorium effects, applicable charges, scenario analysis, and relevant
> destination information — presented in a student-friendly interface with
> full mathematical and source transparency.
>
> This novelty should be validated through continued literature research
> and user testing.

## 4. Limitations of Our Analysis

1. We have not exhaustively tested every feature of every loan aggregator —
   some may have capabilities not visible publicly.
2. This gap analysis is based on observation as of September 2026 and may
   not reflect recent updates to competitor platforms.
3. Our prototype is a Phase 1 (PML 1–3) demonstrator; some identified gaps
   (e.g., live data, automated updates) are addressed in our architecture
   but not yet implemented.
