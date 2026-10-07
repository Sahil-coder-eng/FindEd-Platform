"""
Comprehensive Unit Tests for Calculation Engine
================================================
Validates EMI, repayment, moratorium, total cost, scenario, sensitivity,
and education cost calculations against known results and edge cases.

Run with:
    python -m unittest discover -s tests
"""

import unittest
import math
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculations.emi import calculate_emi, calculate_emi_amount
from calculations.repayment import generate_amortization_schedule, get_yearly_summary
from calculations.moratorium import calculate_moratorium_impact
from calculations.total_cost import calculate_total_cost
from calculations.scenarios import compare_scenarios, find_scenario_differences
from calculations.sensitivity import rate_sensitivity, tenure_sensitivity
from calculations.education_cost import estimate_education_cost, convert_currency, currency_sensitivity


# ════════════════════════════════════════════════════════════════════
# EMI CALCULATION TESTS
# ════════════════════════════════════════════════════════════════════

class TestEMICalculation(unittest.TestCase):
    """Test the core EMI calculation engine."""

    def test_standard_emi(self):
        """₹10,00,000 at 9% for 10 years → EMI ≈ ₹12,668."""
        result = calculate_emi(1000000, 9.0, 10)
        self.assertTrue(12600 <= result["emi"] <= 12700, f"EMI {result['emi']} out of expected range")
        self.assertEqual(result["principal"], 1000000)
        self.assertEqual(result["annual_rate"], 9.0)
        self.assertEqual(result["tenure_years"], 10)
        self.assertEqual(result["tenure_months"], 120)

    def test_total_payment_exceeds_principal(self):
        """Total payment must exceed principal when rate > 0."""
        result = calculate_emi(500000, 8.5, 5)
        self.assertTrue(result["total_payment"] > result["principal"])
        self.assertTrue(result["total_interest"] > 0)

    def test_total_payment_equals_sum(self):
        """Total payment = principal + total interest."""
        result = calculate_emi(1000000, 10.0, 15)
        self.assertLess(abs(result["total_payment"] - (result["principal"] + result["total_interest"])), 1)

    def test_zero_interest_rate(self):
        """0% rate → EMI = principal / months, no interest."""
        result = calculate_emi(1200000, 0.0, 10)
        self.assertEqual(result["emi"], 10000.0)  # 1200000 / 120
        self.assertEqual(result["total_interest"], 0.0)
        self.assertEqual(result["total_payment"], 1200000.0)

    def test_high_interest_rate(self):
        """High rate should still produce valid results."""
        result = calculate_emi(500000, 20.0, 5)
        self.assertTrue(result["emi"] > 0)
        self.assertTrue(result["total_interest"] > 0)

    def test_one_year_tenure(self):
        """1-year tenure should work."""
        result = calculate_emi(100000, 10.0, 1)
        self.assertEqual(result["tenure_months"], 12)
        self.assertTrue(result["emi"] > 0)

    def test_invalid_principal_raises(self):
        """Zero or negative principal should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_emi(0, 9.0, 10)
        with self.assertRaises(ValueError):
            calculate_emi(-100000, 9.0, 10)

    def test_negative_rate_raises(self):
        """Negative rate should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_emi(1000000, -1.0, 10)

    def test_zero_tenure_raises(self):
        """Zero tenure should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_emi(1000000, 9.0, 0)

    def test_interest_to_principal_ratio(self):
        """Interest/principal ratio should be positive for non-zero rate."""
        result = calculate_emi(1000000, 9.0, 10)
        self.assertTrue(result["interest_to_principal_ratio"] > 0)

    def test_emi_amount_helper(self):
        """Helper function should match main function."""
        full = calculate_emi(1000000, 9.0, 10)
        helper = calculate_emi_amount(1000000, 9.0, 120)
        self.assertLess(abs(full["emi"] - helper), 1)


# ════════════════════════════════════════════════════════════════════
# REPAYMENT SCHEDULE TESTS
# ════════════════════════════════════════════════════════════════════

class TestRepaymentSchedule(unittest.TestCase):
    """Test amortization schedule generation."""

    def test_schedule_length(self):
        """Schedule should have exactly tenure_months rows."""
        schedule = generate_amortization_schedule(1000000, 9.0, 10)
        self.assertEqual(len(schedule), 120)

    def test_principal_fully_repaid(self):
        """Closing balance of last month should be zero (or very close)."""
        schedule = generate_amortization_schedule(1000000, 9.0, 10)
        self.assertEqual(schedule.iloc[-1]["closing_principal"], 0.0)

    def test_total_principal_equals_original(self):
        """Sum of all principal components should equal original principal."""
        schedule = generate_amortization_schedule(1000000, 9.0, 10)
        total_principal = schedule["principal_component"].sum()
        self.assertLess(abs(total_principal - 1000000), 10)  # within ₹10 rounding

    def test_interest_decreases_over_time(self):
        """Interest component should generally decrease over time."""
        schedule = generate_amortization_schedule(1000000, 9.0, 10)
        first_interest = schedule.iloc[0]["interest_component"]
        last_interest = schedule.iloc[-1]["interest_component"]
        self.assertTrue(first_interest > last_interest)

    def test_principal_increases_over_time(self):
        """Principal component should generally increase over time."""
        schedule = generate_amortization_schedule(1000000, 9.0, 10)
        first_principal = schedule.iloc[0]["principal_component"]
        mid_principal = schedule.iloc[60]["principal_component"]
        self.assertTrue(mid_principal > first_principal)

    def test_yearly_summary(self):
        """Yearly summary should have correct number of years."""
        schedule = generate_amortization_schedule(1000000, 9.0, 10)
        yearly = get_yearly_summary(schedule)
        self.assertEqual(len(yearly), 10)

    def test_empty_schedule_for_invalid_input(self):
        """Should return empty DataFrame for invalid inputs."""
        schedule = generate_amortization_schedule(0, 9.0, 10)
        self.assertTrue(schedule.empty)


# ════════════════════════════════════════════════════════════════════
# MORATORIUM TESTS
# ════════════════════════════════════════════════════════════════════

class TestMoratorium(unittest.TestCase):
    """Test moratorium impact calculations."""

    def test_capitalized_increases_principal(self):
        """Capitalized interest should increase the effective principal."""
        result = calculate_moratorium_impact(
            1000000, 9.0, 48, 6, 10, "capitalized"
        )
        self.assertTrue(result["effective_principal_at_repayment"] > 1000000)
        self.assertTrue(result["principal_increase"] > 0)

    def test_paid_during_keeps_principal(self):
        """Interest paid during moratorium should keep principal unchanged."""
        result = calculate_moratorium_impact(
            1000000, 9.0, 48, 6, 10, "paid_during"
        )
        self.assertEqual(result["effective_principal_at_repayment"], 1000000)
        self.assertEqual(result["principal_increase"], 0)

    def test_capitalized_costs_more(self):
        """Capitalized interest should result in higher total cost than paid_during."""
        cap = calculate_moratorium_impact(1000000, 9.0, 48, 6, 10, "capitalized")
        paid = calculate_moratorium_impact(1000000, 9.0, 48, 6, 10, "paid_during")
        self.assertTrue(cap["total_cost_with_moratorium"] > paid["total_cost_with_moratorium"])

    def test_moratorium_increases_emi_when_capitalized(self):
        """With capitalized interest, EMI should be higher."""
        result = calculate_moratorium_impact(
            1000000, 9.0, 48, 6, 10, "capitalized"
        )
        self.assertTrue(result["emi_with_moratorium"] > result["emi_without_moratorium"])
        self.assertTrue(result["emi_increase"] > 0)

    def test_paid_during_same_emi(self):
        """With paid-during, EMI should be the same as without moratorium."""
        result = calculate_moratorium_impact(
            1000000, 9.0, 48, 6, 10, "paid_during"
        )
        self.assertEqual(result["emi_with_moratorium"], result["emi_without_moratorium"])

    def test_timeline_durations(self):
        """Timeline durations should add up correctly."""
        result = calculate_moratorium_impact(
            1000000, 9.0, 48, 6, 10, "capitalized"
        )
        tl = result["timeline"]
        self.assertEqual(tl["total_moratorium"]["duration_months"], 54)
        self.assertEqual(tl["repayment_period"]["duration_months"], 120)
        self.assertEqual(tl["total_loan_duration"]["duration_months"], 174)

    def test_invalid_treatment_raises(self):
        """Unknown interest treatment should raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_moratorium_impact(1000000, 9.0, 48, 6, 10, "unknown")


# ════════════════════════════════════════════════════════════════════
# TOTAL COST TESTS
# ════════════════════════════════════════════════════════════════════

class TestTotalCost(unittest.TestCase):
    """Test total cost calculations."""

    def test_cost_without_fees(self):
        """Cost without fees should equal total EMI payments."""
        result = calculate_total_cost(1000000, 9.0, 10)
        self.assertEqual(result["total_known_cost"], result["total_emi_payments"])
        self.assertEqual(result["processing_fee_status"], "not_available")

    def test_cost_with_processing_fee(self):
        """Processing fee should be added to total cost."""
        result = calculate_total_cost(1000000, 9.0, 10, processing_fee_pct=1.0)
        self.assertEqual(result["processing_fee"], 10000.0)
        self.assertEqual(result["processing_fee_status"], "included")
        self.assertTrue(result["total_known_cost"] > result["total_emi_payments"])

    def test_unavailable_charges_flagged(self):
        """Unavailable charges should be flagged, not assumed zero."""
        result = calculate_total_cost(
            1000000, 9.0, 10,
            other_charges={"Insurance": None, "Legal Fee": 500},
        )
        self.assertIn("Insurance", result["unavailable_charges"])
        self.assertIn("Legal Fee", result["known_charges"])

    def test_disclaimer_mentions_unavailable(self):
        """Disclaimer should mention unavailable charges."""
        result = calculate_total_cost(
            1000000, 9.0, 10,
            other_charges={"Insurance": None},
        )
        self.assertIn("Insurance", result["disclaimer"])


# ════════════════════════════════════════════════════════════════════
# SCENARIO COMPARISON TESTS
# ════════════════════════════════════════════════════════════════════

class TestScenarioComparison(unittest.TestCase):
    """Test scenario comparison engine."""

    def test_comparison_returns_correct_rows(self):
        """Should return one row per scenario."""
        scenarios = [
            {"name": "A", "principal": 1000000, "annual_rate": 9.0, "tenure_years": 10},
            {"name": "B", "principal": 1000000, "annual_rate": 9.0, "tenure_years": 7},
        ]
        df = compare_scenarios(scenarios)
        self.assertEqual(len(df), 2)

    def test_shorter_tenure_higher_emi(self):
        """Shorter tenure → higher EMI but less total interest."""
        scenarios = [
            {"name": "Long", "principal": 1000000, "annual_rate": 9.0, "tenure_years": 10},
            {"name": "Short", "principal": 1000000, "annual_rate": 9.0, "tenure_years": 5},
        ]
        df = compare_scenarios(scenarios)
        long_row = df[df["Scenario"] == "Long"].iloc[0]
        short_row = df[df["Scenario"] == "Short"].iloc[0]
        self.assertTrue(short_row["Monthly EMI (₹)"] > long_row["Monthly EMI (₹)"])
        self.assertTrue(short_row["Total Interest (₹)"] < long_row["Total Interest (₹)"])

    def test_scenario_differences(self):
        """Spreads should be positive when scenarios differ."""
        scenarios = [
            {"name": "A", "principal": 1000000, "annual_rate": 8.0, "tenure_years": 10},
            {"name": "B", "principal": 1000000, "annual_rate": 12.0, "tenure_years": 10},
        ]
        df = compare_scenarios(scenarios)
        spreads = find_scenario_differences(df)
        self.assertTrue(spreads["emi_spread"] > 0)
        self.assertTrue(spreads["interest_spread"] > 0)


# ════════════════════════════════════════════════════════════════════
# SENSITIVITY TESTS
# ════════════════════════════════════════════════════════════════════

class TestSensitivity(unittest.TestCase):
    """Test sensitivity analysis engine."""

    def test_rate_sensitivity_returns_rows(self):
        """Should return rows for each rate step."""
        df = rate_sensitivity(1000000, 10, 7.0, 12.0, 1.0)
        self.assertEqual(len(df), 6)  # 7, 8, 9, 10, 11, 12

    def test_higher_rate_higher_emi(self):
        """Higher rate should always produce higher EMI."""
        df = rate_sensitivity(1000000, 10, 7.0, 12.0, 1.0)
        emis = df["Monthly EMI (₹)"].tolist()
        self.assertEqual(emis, sorted(emis))  # should be monotonically increasing

    def test_tenure_sensitivity_returns_rows(self):
        """Should return rows for each tenure option."""
        df = tenure_sensitivity(1000000, 9.0, [5, 10, 15])
        self.assertEqual(len(df), 3)

    def test_shorter_tenure_higher_emi_lower_interest(self):
        """Shorter tenure → higher EMI, lower total interest."""
        df = tenure_sensitivity(1000000, 9.0, [5, 10, 15])
        # EMI should decrease as tenure increases
        emis = df["Monthly EMI (₹)"].tolist()
        self.assertEqual(emis, sorted(emis, reverse=True))
        # Interest should increase as tenure increases
        interests = df["Total Interest (₹)"].tolist()
        self.assertEqual(interests, sorted(interests))


# ════════════════════════════════════════════════════════════════════
# EDUCATION COST TESTS
# ════════════════════════════════════════════════════════════════════

class TestEducationCost(unittest.TestCase):
    """Test education cost estimator."""

    def test_basic_cost_estimation(self):
        """Basic cost calculation should work."""
        result = estimate_education_cost(
            tuition=200000, hostel=80000, num_years=4,
        )
        self.assertEqual(result["total_education_cost"], (200000 + 80000) * 4)
        self.assertEqual(result["financing_required"], result["total_education_cost"])

    def test_scholarship_reduces_requirement(self):
        """Scholarship should reduce financing requirement."""
        result = estimate_education_cost(
            tuition=200000, num_years=4,
            scholarship=300000,
        )
        self.assertEqual(result["financing_required"], 200000 * 4 - 300000)

    def test_financing_not_negative(self):
        """Financing requirement should not go below zero."""
        result = estimate_education_cost(
            tuition=100000, num_years=1,
            scholarship=500000,
        )
        self.assertEqual(result["financing_required"], 0)

    def test_currency_conversion(self):
        """Currency conversion should multiply correctly."""
        result = convert_currency(30000, 83.0, "$", "₹")
        self.assertEqual(result["converted_amount"], 2490000.0)

    def test_currency_sensitivity_returns_results(self):
        """Should return sensitivity results."""
        results = currency_sensitivity(30000, 83.0, 10, 5)
        self.assertEqual(len(results), 11)  # -5 to +5 inclusive
        # Base rate should be in the middle
        self.assertEqual(results[5]["rate_change_pct"], 0.0)


# ════════════════════════════════════════════════════════════════════
# CROSS-VALIDATION TESTS
# ════════════════════════════════════════════════════════════════════

class TestCrossValidation(unittest.TestCase):
    """
    Cross-validate our calculations against known mathematical results.
    These serve as integration tests ensuring the formulas are correct.
    """

    def test_known_emi_value_1(self):
        """
        ₹5,00,000 at 8.5% for 5 years.
        Expected EMI ≈ ₹10,258.27 (verified against mathematical formula).
        """
        result = calculate_emi(500000, 8.5, 5)
        self.assertLess(abs(result["emi"] - 10258.27), 1)  # within ₹1

    def test_known_emi_value_2(self):
        """
        ₹20,00,000 at 10% for 15 years.
        Expected EMI ≈ ₹21,492 (verified against standard tables).
        """
        result = calculate_emi(2000000, 10.0, 15)
        self.assertLess(abs(result["emi"] - 21492), 15)

    def test_amortization_total_interest_matches_emi(self):
        """
        Total interest from amortization schedule should match
        the total interest from EMI calculation.
        """
        emi_result = calculate_emi(1000000, 9.0, 10)
        schedule = generate_amortization_schedule(1000000, 9.0, 10)
        schedule_interest = schedule["interest_component"].sum()
        self.assertLess(abs(schedule_interest - emi_result["total_interest"]), 100)  # within ₹100


if __name__ == "__main__":
    unittest.main()
