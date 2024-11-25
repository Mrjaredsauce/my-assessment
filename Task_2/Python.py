import os

import numpy as np
import pandas as pd

"""
To answer the following questions, make use of datasets: 
    'scheduled_loan_repayments.csv'
    'actual_loan_repayments.csv'
These files are located in the 'data' folder. 

'scheduled_loan_repayments.csv' contains the expected monthly payments for each loan. These values are constant regardless of what is actually paid.
'actual_loan_repayments.csv' contains the actual amount paid to each loan for each month.

All loans have a loan term of 2 years with an annual interest rate of 10%. Repayments are scheduled monthly.
A type 1 default occurs on a loan when any scheduled monthly repayment is not met in full.
A type 2 default occurs on a loan when more than 15% of the expected total payments are unpaid for the year.

Note: Do not round any final answers.

"""


def calculate_df_balances(df_scheduled, df_actual):
    """
    This is a utility function that creates a merged dataframe that will be used in the following questions.
    This function will not be graded, do not make changes to it.

    Args:
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
        df_actual (DataFrame): Dataframe created from the 'actual_loan_repayments.csv' dataset

    Returns:
        DataFrame: A merged Dataframe with additional calculated columns to help with the following questions.

    """

    df_merged = pd.merge(df_actual, df_scheduled)

    def calculate_balance(group):
        r_monthly = 0.1 / 12
        group = group.sort_values("Month")
        balances = []
        interest_payments = []
        loan_start_balances = []
        for index, row in group.iterrows():
            if balances:
                interest_payment = balances[-1] * r_monthly
                balance_with_interest = balances[-1] + interest_payment
            else:
                interest_payment = row["LoanAmount"] * r_monthly
                balance_with_interest = row["LoanAmount"] + interest_payment
                loan_start_balances.append(row["LoanAmount"])

            new_balance = balance_with_interest - row["ActualRepayment"]
            interest_payments.append(interest_payment)

            new_balance = max(0, new_balance)
            balances.append(new_balance)

        loan_start_balances.extend(balances)
        loan_start_balances.pop()
        group["LoanBalanceStart"] = loan_start_balances
        group["LoanBalanceEnd"] = balances
        group["InterestPayment"] = interest_payments
        return group

    df_balances = (
        df_merged.groupby("LoanID", as_index=False)
        .apply(calculate_balance)
        .reset_index(drop=True)
    )

    df_balances["LoanBalanceEnd"] = df_balances["LoanBalanceEnd"].round(2)
    df_balances["InterestPayment"] = df_balances["InterestPayment"].round(2)
    df_balances["LoanBalanceStart"] = df_balances["LoanBalanceStart"].round(2)

    return df_balances


# Do not edit these directories
root = os.getcwd()

if "Task_2" in root:
    df_scheduled = pd.read_csv("data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("data/actual_loan_repayments.csv")
else:
    df_scheduled = pd.read_csv("Task_2/data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("Task_2/data/actual_loan_repayments.csv")

df_balances = calculate_df_balances(df_scheduled, df_actual)


def question_1(df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 1 default definition.

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The percentage of type 1 defaulted loans (ie 50.0 not 0.5)

    """

    # Determine if a row is defaulted accourding to Type 1 definition (ActualRepayment < ScheduledRepayment)
    df_balances["DefaultedType1"] = df_balances["ActualRepayment"] < df_balances["ScheduledRepayment"]

    # Group by LoanID and determine if any row in the group has defaulted
    loan_defaults = df_balances.groupby("LoanID")["DefaultedType1"].max()

    # Calculate the percentage of defaulted loans
    total_loans = len(loan_defaults)
    defaulted_loans = loan_defaults.sum()
    default_rate_percent = (defaulted_loans / total_loans) * 100

    return default_rate_percent


def question_2(df_scheduled, df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 2 default definition

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset

    Returns:
        float: The percentage of type 2 defaulted loans (ie 50.0 not 0.5)

    """

    # Sum ActualRepayment and ScheduledRepayment for each LoanID
    actual_sum = df_balances.groupby("LoanID")["ActualRepayment"].sum()
    expected_sum = df_balances.groupby("LoanID")["ScheduledRepayment"].sum()

    # Merge the actual and expected sums on LoanID
    merged_df = pd.DataFrame({
        'ActualRepayment': actual_sum,
        'ScheduledRepayment': expected_sum
    }).reset_index()

    # Add a column to identify if a loan defaulted according to Type 2 definition
    merged_df["DefaultedType2"] = merged_df["ActualRepayment"] <= merged_df["ScheduledRepayment"] * 0.85
    
    # Calculate the percentage of loans that defaulted (at least one default)
    total_loans = len(merged_df)
    defaulted_loans = merged_df["DefaultedType2"].sum()
    default_rate_percent = (defaulted_loans / total_loans) * 100

    return default_rate_percent


def question_3(df_balances):
    """
    Calculate the anualized portfolio CPR (As a %) from the geometric mean SMM.
    SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
    SMM_mean is calculated as (∏(1+SMM))^(1/12) - 1
    CPR is calcualted as: 1 - (1- SMM_mean)^12

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The anualized CPR of the loan portfolio as a percent.

    """

     # Calculate Unscheduled Principal for each row
    df_balances["UnscheduledPrincipal"] = np.where(
        df_balances["ActualRepayment"] > df_balances["ScheduledRepayment"],
        df_balances["ActualRepayment"] - df_balances["ScheduledRepayment"],
        0
    )

    # Calculate SMM for each row
    df_balances["SMM"] = np.where(
        df_balances["LoanBalanceStart"] > 0,
        df_balances["UnscheduledPrincipal"] / df_balances["LoanBalanceStart"],
        0
    )

    # Calculate geometric mean SMM
    SMM_mean = np.prod((1 + df_balances["SMM"]) ** (1 / len(df_balances["SMM"]))) - 1
    SMM_mean_percent = SMM_mean * 100

    # Calculate the annualized CPR from the SMM Mean
    cpr = 1 - (1 - SMM_mean) ** 12
    cpr_percent = cpr * 100

    return cpr_percent


def question_4(df_balances):
    """
    Calculate the predicted total loss for the second year in the loan term.
    Use the equation: probability_of_default * total_loan_balance * (1 - recovery_rate).
    The probability_of_default value must be taken from either your question_1 or question_2 answer.
    Decide between the two answers based on which default definition you believe to be the more useful metric.
    Assume a recovery rate of 80%

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The predicted total loss for the second year in the loan term.

    """

    # Get the probability of default, using Type 2 definition
    default_rate_percent = question_2(df_balances, df_balances)  # Reusing question_2 to get the default rate
    probability_of_default = default_rate_percent / 100  # Convert to a decimal

    # Assume recovery rate of 80%
    recovery_rate = 0.80

    # Get the final loan balance for the year for each LoanID
    loan_balance_end_of_year = df_balances[df_balances['Month'] == 12].groupby('LoanID')['LoanBalanceEnd'].first()

    # Calculate the total predicted loss for each loan
    total_loss = (loan_balance_end_of_year * probability_of_default * (1 - recovery_rate)).sum()

    return total_loss
