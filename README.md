# Automated-Lease-Accountant---Lessee-IFRS-ASPE-
Program which converts lease inputs from lessee perspective, into accurate, standardized accounting journal entries.

- data_structures.py file contains the necessary data classes for program to work (JournalEntry, and LeaseInputs)
- lessee_engine.py file contains the "lessee engine" class, which processes, standardizes, measures and generates initial and subseuqent accounting-ready entries. This is calculated through an amortization schedule, generated within the class via a function.
