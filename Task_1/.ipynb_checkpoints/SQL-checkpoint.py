"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)


NOTE:
Each question in this section is isolated, for example, you do not need to consider how Q5 may affect Q4.
Remember to clean your data.

"""


def question_1():
    """
    Find the name, surname and customer ids for all the duplicated customer ids in the customers dataset.
    Return the `Name`, `Surname` and `CustomerID`
    """

    qry = """
        SELECT TRIM(Name) AS Name, TRIM(Surname) AS Surname, CustomerID
        FROM customers
        WHERE TRIM(CustomerID) IS NOT NULL
        AND TRIM(CustomerID) IN (
            SELECT TRIM(CustomerID)
            FROM customers
            GROUP BY TRIM(CustomerID)
            HAVING COUNT(TRIM(CustomerID)) > 1
        )
        """

    return qry


def question_2():
    """
    Return the `Name`, `Surname` and `Income` of all female customers in the dataset in descending order of income
    """

    qry = """
        SELECT TRIM(Name) AS Name, TRIM(Surname) AS Surname, Income
        FROM customers
        WHERE UPPER(TRIM(Gender)) IN ('FEMALE', 'F')
        AND Income IS NOT NULL
        ORDER BY Income DESC"""

    return qry


def question_3():
    """
    Calculate the percentage of approved loans by LoanTerm, with the result displayed as a percentage out of 100.
    ie 50 not 0.5
    There is only 1 loan per customer ID.
    """

    qry = """
        SELECT TRIM(LoanTerm) AS LoanTerm, 
           (COUNT(CASE WHEN UPPER(TRIM(ApprovalStatus)) = 'APPROVED' THEN 1 END) * 100.0) / COUNT(DISTINCT TRIM(CustomerID)) AS ApprovedLoanPercentage
        FROM loans
        WHERE TRIM(LoanTerm) IS NOT NULL
        AND TRIM(ApprovalStatus) IS NOT NULL
        AND TRIM(CustomerID) IS NOT NULL
        GROUP BY TRIM(LoanTerm)
        ORDER BY LoanTerm ASC
        """

    return qry


def question_4():
    """
    Return a breakdown of the number of customers per CustomerClass in the credit data
    Return columns `CustomerClass` and `Count`
    """

    qry = """
        SELECT TRIM(CustomerClass) AS CustomerClass, 
        COUNT(DISTINCT CustomerID) AS Count
        FROM credit
        WHERE TRIM(CustomerClass) IS NOT NULL
        AND TRIM(CustomerID) IS NOT NULL
        GROUP BY TRIM(CustomerClass)
        """

    return qry


def question_5():
    """
    Make use of the UPDATE function to amend/fix the following: Customers with a CreditScore between and including 600 to 650 must be classified as CustomerClass C.
    """

    qry = """
        UPDATE credit
        SET CustomerClass = 'C'
        WHERE CreditScore BETWEEN 600 AND 650
        AND CustomerClass IS NOT NULL
        AND rowid = (
            SELECT MIN(rowid)
            FROM credit c2
            WHERE credit.CustomerID = c2.CustomerID
        );
        """

    return qry
