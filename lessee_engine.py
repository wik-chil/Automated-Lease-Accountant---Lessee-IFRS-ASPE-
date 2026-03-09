from data_structures import JournalEntry, LeaseInputs
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


class LesseeEngine:
    """Class for classifying, measuring and journaling lease transactions from lessee perspective. Classification
    includes IFRS and ASPE standards."""

    def __init__(self, inputs: LeaseInputs):
        """Initialize lessee engine with lease inputs, and determine correct discount rate according to standards."""
        self.inputs = inputs

        # Determining correct discount rate based on standard.
        if self.inputs.standard == "IFRS" and self.inputs.implicit_rate is not None:
            self.discount_rate = self.inputs.implicit_rate
        elif self.inputs.standard == "ASPE" and self.inputs.implicit_rate is not None:
            self.discount_rate = min(self.inputs.implicit_rate, self.inputs.incremental_borrowing_rate)
        else:
            self.discount_rate = self.inputs.incremental_borrowing_rate


    def present_value_payments(self) -> float:
        """Calculate present value of lease payments and return as a float value."""
        r = self.discount_rate / self.inputs.payments_per_year
        pmt = self.inputs.lease_pmt
        n = self.inputs.lease_term_years * self.inputs.payments_per_year

        # If GRV available use it, else use bargain purchase option as fv
        fv = self.inputs.guaranteed_residual_value if (
                self.inputs.guaranteed_residual_value != 0) else self.inputs.bargain_purchase_option

        if r == 0:
            return round(min(pmt * n, self.inputs.asset_fair_value), 2)
        else:
            pv = pmt * ((1 - (1 + r) ** -n) / r) * (1 + r) + fv / (1 + r) ** n
            return round(min(pv, self.inputs.asset_fair_value), 2)

    def classify(self) -> str:
        """Based on inputs, classify lease as operating, capital or financing lease."""
        pv = self.present_value_payments()

        if self.inputs.standard == "IFRS":
            if pv <= 5000 or self.inputs.lease_term_years <= 1:
                return "operating lease"
            else:
                return "financing lease"

        else:
            # If lease term is at least 75% of economic life of asset -> capital lease
            life_test = (self.inputs.lease_term_years / self.inputs.asset_economic_life) >= 0.75

            # If minimum lease payments total at least 90% of asset fair value -> capital lease
            pv_test = (pv / self.inputs.asset_fair_value) >= 0.9

            # If transfer of ownership -> capital lease
            if self.inputs.ownership_transfer or not self.inputs.bargain_purchase_option or life_test or pv_test:
                return "capital lease"
            else:
                return "operating lease"

    def generate_amortization_schedule(self, lease_start_date: str, pmt_start_date: str):
        """Generate an amortization schedule for the lease, using the discount rate, present value of lease payments
        (initial investment), actual payments, and date inputs to return accurate amortization schedule."""
        # Check if payments start same day as the lease
        lease_start = datetime.strptime(lease_start_date, "%Y-%m-%d")
        pmt_start = datetime.strptime(pmt_start_date, "%Y-%m-%d")

        r = self.discount_rate / self.inputs.payments_per_year
        liability = self.present_value_payments()
        payment = self.inputs.lease_pmt

        if lease_start == pmt_start:
            total_periods = self.inputs.lease_term_years * self.inputs.payments_per_year + 1
        else:
            total_periods = self.inputs.lease_term_years * self.inputs.payments_per_year

        schedule = []

        current_date = lease_start

        for period in range(1, total_periods + 1):
            if lease_start == pmt_start and period == 1:
                interest = 0
            elif lease_start == pmt_start and period == total_periods:
                payment = 0
                interest = liability * r
            else:
                interest = liability * r
            principal_deduced = payment - interest
            closing_balance = liability - principal_deduced

            schedule.append({
                "Period": period,
                "Date": current_date.strftime("%Y-%m-%d"),
                "Opening Liability": round(liability, 2),
                "Lease Payment": round(payment, 2),
                "Interest": round(interest, 2),
                "Principal Deduction": round(principal_deduced, 2),
                "Closing Liability": round(closing_balance, 2)
            })

            liability = closing_balance

            current_date += relativedelta(years=1)

        return pd.DataFrame(schedule)

    def generate_journal_entries(self, lease_start_date: str, pmt_start_date: str):
        """Generate all journal entries for all periods within lease, assuming Dec. 31 year-end."""
        schedule = self.generate_amortization_schedule(lease_start_date, pmt_start_date)
        entries = []

        for _, row in schedule.iterrows():
            date = row["Date"]

            if self.inputs.standard == "IFRS" and self.classify() == "financing lease":
                if row["Period"] == 1:
                    # Record initial lease liability
                    entries.append(JournalEntry(date, "Right of Use Asset", "Lease Liability", row["Opening Liability"],
                                                "Record inception of lease."))
                    if lease_start_date == pmt_start_date:
                        # Record initial payment if made on date that lease began
                        entries.append(JournalEntry(date, "Lease Liability", "Cash", row["Lease Payment"],
                                                    "Record payment on lease."))
                else:
                    if row["Lease Payment"] != 0:
                        # Append payment towards lease liability
                        entries.append(JournalEntry(date, "Lease Liability", "Cash", row["Lease Payment"],
                                                    "Record payment on lease."))
                    if row["Interest"] != 0:
                        # Record interest expense accrued on lease liability
                        entries.append(JournalEntry(date, "Interest Expense", "Lease Liability", row["Interest"],
                                                    "Record interest on lease."))

        return entries

inp = LeaseInputs("IFRS", "lessee", 5, 20066.26, 1, 88000, 10, 0.09, 0.09, False, 4500, 0, 0)
lease = LesseeEngine(inp)

print(lease.present_value_payments())
print(lease.generate_amortization_schedule("2020-4-4", "2020-4-4"))
entries = (lease.generate_journal_entries("2020-4-4", "2020-4-4"))

for e in entries:
    e.print_entry()