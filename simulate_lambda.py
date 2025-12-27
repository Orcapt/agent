"""
Simplified Lambda Simulator for Agent1
Uses the built-in orca utility for testing.
"""
import os
# Force DEV MODE for clear console output (must be set before imports)
os.environ["ORCA_DEV_MODE"] = "true"

from orca import simulate_lambda_handler
from lambda_handler import handler

if __name__ == "__main__":
    # One line to test HTTP, SQS, and Cron flows!
    simulate_lambda_handler(handler, message="Analyze my site, it's about AI research.")
