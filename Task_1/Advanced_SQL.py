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
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """
    SELECT 
        TRIM(c.CustomerClass) AS CustomerClass,
        AVG(CAST(cu.Income AS FLOAT)) AS AverageIncome
    FROM 
        (
            SELECT DISTINCT CustomerID, CustomerClass
            FROM credit
            WHERE TRIM(CustomerClass) IS NOT NULL
        ) c
    JOIN 
        (
            SELECT DISTINCT CustomerID, Income
            FROM customers
            WHERE TRIM(Income) ~ '^[0-9]+(\.[0-9]*)?$' -- Ensures Income contains valid numeric data
        ) cu
    ON 
        c.CustomerID = cu.CustomerID
    GROUP BY 
        TRIM(c.CustomerClass)
    ORDER BY 
        CustomerClass ASC;
    """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """
    "Only the following Provinces will be considered, NC, GT, MP, WC, EC, NW, FS, KZN, LP, other unexpected Provinces will be put in an 'Other' category"

    qry = """
    SELECT 
        CASE 
            WHEN TRIM(UPPER(c.Region)) IN ('NC', 'NORTHERNCAPE') THEN 'NC'
            WHEN TRIM(UPPER(c.Region)) IN ('GT', 'GAUTENG') THEN 'GT'
            WHEN TRIM(UPPER(c.Region)) IN ('MP', 'MPUMALANGA') THEN 'MP'
            WHEN TRIM(UPPER(c.Region)) IN ('WC', 'WESTERNCAPE') THEN 'WC'
            WHEN TRIM(UPPER(c.Region)) IN ('EC', 'EASTERNCAPE') THEN 'EC'
            WHEN TRIM(UPPER(c.Region)) IN ('NW', 'NORTHWEST') THEN 'NW'
            WHEN TRIM(UPPER(c.Region)) IN ('FS', 'FREESTATE') THEN 'FS'
            WHEN TRIM(UPPER(c.Region)) IN ('KZN', 'KWAZULU-NATAL') THEN 'KZN'
            WHEN TRIM(UPPER(c.Region)) IN ('LP', 'LIMPOPO') THEN 'LP'
            ELSE 'Other'
        END AS Province,
        COUNT(*) AS RejectedApplications
    FROM 
        (
            SELECT DISTINCT CustomerID, Region
            FROM customers
            WHERE TRIM(Region) IS NOT NULL
        ) c
    JOIN 
        (
            SELECT DISTINCT CustomerID, ApprovalStatus
            FROM loans
            WHERE TRIM(ApprovalStatus) IS NOT NULL
        ) l
    ON 
        c.CustomerID = l.CustomerID
    WHERE 
        TRIM(UPPER(l.ApprovalStatus)) = 'REJECTED'
    GROUP BY 
        Province
    ORDER BY 
        Province ASC;
    """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    qry = """
    CREATE TABLE financing AS
    WITH DistinctCustomers AS (
        SELECT DISTINCT CustomerID, Income
        FROM customers
        WHERE CustomerID IS NOT NULL AND Income IS NOT NULL
    ),
    DistinctLoans AS (
        SELECT CustomerID, LoanAmount, LoanTerm, InterestRate, ApprovalStatus
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY LoanAmount DESC) AS row_num
            FROM loans
            WHERE CustomerID IS NOT NULL
        )
        WHERE row_num = 1
    ),
    DistinctCredits AS (
        SELECT CustomerID, CreditScore
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY CreditScore DESC) AS row_num
            FROM credit
            WHERE CustomerID IS NOT NULL
        )
        WHERE row_num = 1
    )
    SELECT 
        c.CustomerID,
        c.Income,
        l.LoanAmount,
        l.LoanTerm,
        l.InterestRate,
        l.ApprovalStatus,
        cr.CreditScore
    FROM 
        DistinctCustomers c
    JOIN 
        DistinctLoans l ON c.CustomerID = l.CustomerID
    JOIN 
        DistinctCredits cr ON c.CustomerID = cr.CustomerID;
    """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    "Only the following time zones are considered, JST, PST, CET, EET, PNT, CST, IST, UTC, GMT, other unexpected time zones will come out as NULL."

    qry = """
    CREATE TABLE timeline AS
    WITH UniqueRepayments AS (
        SELECT DISTINCT 
            RepaymentID,
            CustomerID,
            Amount,
            RepaymentDate,
            TimeZone
        FROM repayments
        WHERE RepaymentID IS NOT NULL
    ),
    AdjustedRepayments AS (
        SELECT 
            ur.CustomerID,
            ur.RepaymentID,
            ur.Amount,
            m.MonthName,
            ur.RepaymentDate,
            -- Adjust repayment time to GMT (London Time)
            CASE 
                WHEN ur.TimeZone = 'JST' THEN ur.RepaymentDate - INTERVAL '9 hours'
                WHEN ur.TimeZone = 'PST' THEN ur.RepaymentDate + INTERVAL '8 hours'
                WHEN ur.TimeZone = 'CET' THEN ur.RepaymentDate - INTERVAL '1 hour'
                WHEN ur.TimeZone = 'EET' THEN ur.RepaymentDate - INTERVAL '2 hours'
                WHEN ur.TimeZone = 'PNT' THEN ur.RepaymentDate + INTERVAL '7 hours'
                WHEN ur.TimeZone = 'CST' THEN ur.RepaymentDate + INTERVAL '6 hours'
                WHEN ur.TimeZone = 'IST' THEN ur.RepaymentDate - INTERVAL '5 hours 30 minutes'
                WHEN ur.TimeZone = 'UTC' THEN ur.RepaymentDate
                WHEN ur.TimeZone = 'GMT' THEN ur.RepaymentDate
                ELSE NULL -- Handle unexpected time zones as NULL
            END AS AdjustedRepaymentDate
        FROM 
            UniqueRepayments ur
        LEFT JOIN 
            months m ON strftime('%m', ur.RepaymentDate) = m.MonthID
    ),
    FilteredRepayments AS (
        SELECT 
            CustomerID,
            MonthName,
            RepaymentID,
            Amount
        FROM 
            AdjustedRepayments
        WHERE 
            AdjustedRepaymentDate IS NOT NULL
            AND CAST(strftime('%H', AdjustedRepaymentDate) AS INTEGER) BETWEEN 6 AND 18 -- Between 6 AM and 6 PM GMT
    )
    SELECT 
        c.CustomerID,
        m.MonthName,
        COUNT(fr.RepaymentID) AS NumberOfRepayments,
        COALESCE(SUM(fr.Amount), 0) AS AmountTotal
    FROM 
        (SELECT DISTINCT CustomerID FROM customers WHERE CustomerID IS NOT NULL) c
    CROSS JOIN 
        months m
    LEFT JOIN 
        FilteredRepayments fr ON c.CustomerID = fr.CustomerID AND m.MonthName = fr.MonthName
    GROUP BY 
        c.CustomerID, m.MonthName
    ORDER BY 
        c.CustomerID, m.MonthName;
    """

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """
    SELECT 
        CustomerID,
        -- January
        SUM(CASE WHEN MonthName = 'January' THEN NumberOfRepayments ELSE 0 END) AS JanuaryRepayments,
        SUM(CASE WHEN MonthName = 'January' THEN AmountTotal ELSE 0 END) AS JanuaryTotal,
        -- February
        SUM(CASE WHEN MonthName = 'February' THEN NumberOfRepayments ELSE 0 END) AS FebruaryRepayments,
        SUM(CASE WHEN MonthName = 'February' THEN AmountTotal ELSE 0 END) AS FebruaryTotal,
        -- March
        SUM(CASE WHEN MonthName = 'March' THEN NumberOfRepayments ELSE 0 END) AS MarchRepayments,
        SUM(CASE WHEN MonthName = 'March' THEN AmountTotal ELSE 0 END) AS MarchTotal,
        -- April
        SUM(CASE WHEN MonthName = 'April' THEN NumberOfRepayments ELSE 0 END) AS AprilRepayments,
        SUM(CASE WHEN MonthName = 'April' THEN AmountTotal ELSE 0 END) AS AprilTotal,
        -- May
        SUM(CASE WHEN MonthName = 'May' THEN NumberOfRepayments ELSE 0 END) AS MayRepayments,
        SUM(CASE WHEN MonthName = 'May' THEN AmountTotal ELSE 0 END) AS MayTotal,
        -- June
        SUM(CASE WHEN MonthName = 'June' THEN NumberOfRepayments ELSE 0 END) AS JuneRepayments,
        SUM(CASE WHEN MonthName = 'June' THEN AmountTotal ELSE 0 END) AS JuneTotal,
        -- July
        SUM(CASE WHEN MonthName = 'July' THEN NumberOfRepayments ELSE 0 END) AS JulyRepayments,
        SUM(CASE WHEN MonthName = 'July' THEN AmountTotal ELSE 0 END) AS JulyTotal,
        -- August
        SUM(CASE WHEN MonthName = 'August' THEN NumberOfRepayments ELSE 0 END) AS AugustRepayments,
        SUM(CASE WHEN MonthName = 'August' THEN AmountTotal ELSE 0 END) AS AugustTotal,
        -- September
        SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END) AS SeptemberRepayments,
        SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0 END) AS SeptemberTotal,
        -- October
        SUM(CASE WHEN MonthName = 'October' THEN NumberOfRepayments ELSE 0 END) AS OctoberRepayments,
        SUM(CASE WHEN MonthName = 'October' THEN AmountTotal ELSE 0 END) AS OctoberTotal,
        -- November
        SUM(CASE WHEN MonthName = 'November' THEN NumberOfRepayments ELSE 0 END) AS NovemberRepayments,
        SUM(CASE WHEN MonthName = 'November' THEN AmountTotal ELSE 0 END) AS NovemberTotal,
        -- December
        SUM(CASE WHEN MonthName = 'December' THEN NumberOfRepayments ELSE 0 END) AS DecemberRepayments,
        SUM(CASE WHEN MonthName = 'December' THEN AmountTotal ELSE 0 END) AS DecemberTotal
    FROM 
        timeline
    GROUP BY 
        CustomerID
    ORDER BY 
        CustomerID;
    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """
    CREATE TABLE corrected_customers AS
    WITH MaleData AS (
        -- Filter male customers and remove duplicates based on CustomerID
        SELECT DISTINCT 
            CustomerID,
            Age,
            Gender
        FROM customers
        WHERE UPPER(TRIM(Gender)) IN ('MALE', 'M')
    ),
    FemaleData AS (
        -- Filter female customers and remove duplicates based on CustomerID
        SELECT DISTINCT 
            CustomerID,
            Age,
            Gender
        FROM customers
        WHERE UPPER(TRIM(Gender)) IN ('FEMALE', 'F')
    ),
    
    -- Correct ages for males by shifting upwards using LEAD with a 2-row shift
    MaleCorrected AS (
        SELECT 
            CustomerID,
            Age,
            -- Adjust the age by shifting 2 rows upwards
            LEAD(Age, 2) OVER (ORDER BY CustomerID) AS CorrectedAge,
            Gender
        FROM MaleData
    ),
    -- Correct ages for females similarly by shifting upwards using LEAD with a 2-row shift
    FemaleCorrected AS (
        SELECT 
            CustomerID,
            Age,
            -- Adjust the age by shifting 2 rows upwards
            LEAD(Age, 2) OVER (ORDER BY CustomerID) AS CorrectedAge,
            Gender
        FROM FemaleData
    ),
    
    -- Handle NaN values in the MaleCorrected table by replacing the last 2 rows with the top 2 rows' ages
    MaleFinal AS (
        SELECT 
            CustomerID,
            Age,
            CASE 
                -- Replace the second last row with the first row's age
                WHEN ROW_NUMBER() OVER (ORDER BY CustomerID DESC) = 2 THEN 
                    (SELECT Age FROM MaleCorrected ORDER BY CustomerID LIMIT 1) -- First row's Age
                -- Replace the last row with the second row's age
                WHEN ROW_NUMBER() OVER (ORDER BY CustomerID DESC) = 1 THEN 
                    (SELECT Age FROM MaleCorrected ORDER BY CustomerID LIMIT 2 OFFSET 1) -- Second row's Age
                ELSE CorrectedAge -- For all other rows, use the corrected age
            END AS CorrectedAge,
            Gender
        FROM MaleCorrected
    ),
    -- Handle NaN values in the FemaleCorrected table by replacing the last 2 rows with the top 2 rows' ages
    FemaleFinal AS (
        SELECT 
            CustomerID,
            Age,
            CASE 
                -- Replace the second last row with the first row's age
                WHEN ROW_NUMBER() OVER (ORDER BY CustomerID DESC) = 2 THEN 
                    (SELECT Age FROM FemaleCorrected ORDER BY CustomerID LIMIT 1) -- First row's Age
                -- Replace the last row with the second row's age
                WHEN ROW_NUMBER() OVER (ORDER BY CustomerID DESC) = 1 THEN 
                    (SELECT Age FROM FemaleCorrected ORDER BY CustomerID LIMIT 2 OFFSET 1) -- Second row's Age
                ELSE CorrectedAge -- For all other rows, use the corrected age
            END AS CorrectedAge,
            Gender
        FROM FemaleCorrected
    ),
    
    -- Combine the corrected tables for males and females
    Combined AS (
        SELECT CustomerID, Age, CorrectedAge, Gender FROM MaleFinal
        UNION ALL
        SELECT CustomerID, Age, CorrectedAge, Gender FROM FemaleFinal
    )
    
    -- Final selection of distinct customer IDs, ensuring the correct format for the Gender column
    SELECT DISTINCT 
        CustomerID,
        Age,
        CorrectedAge,
        CASE 
            WHEN UPPER(TRIM(Gender)) IN ('FEMALE', 'F') THEN 'Female'
            WHEN UPPER(TRIM(Gender)) IN ('MALE', 'M') THEN 'Male'
            ELSE 'Other' 
        END AS Gender
    FROM Combined
    ORDER BY CustomerID;
    
    SELECT * FROM corrected_customers;

    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    qry = """
    WITH AgeCategoryData AS (
        -- Assigning AgeCategory based on CorrectedAge
        SELECT 
            CustomerID,
            Age,
            CorrectedAge,
            Gender,
            CASE 
                WHEN CorrectedAge < 20 THEN 'Teen'
                WHEN CorrectedAge >= 20 AND CorrectedAge < 30 THEN 'Young Adult'
                WHEN CorrectedAge >= 30 AND CorrectedAge < 60 THEN 'Adult'
                WHEN CorrectedAge >= 60 THEN 'Pensioner'
            END AS AgeCategory
        FROM corrected_customers
    ),
    
    RepaymentData AS (
        -- Counting repayments per customer
        SELECT 
            CustomerID,
            COUNT(*) AS TotalRepayments
        FROM repayments  -- Assuming a `repayments` table exists where we can count the repayments per customer
        GROUP BY CustomerID
    ),
    
    RankData AS (
        -- Combining the AgeCategory with repayment count and assigning rank
        SELECT 
            a.CustomerID,
            a.Age,
            a.CorrectedAge,
            a.Gender,
            a.AgeCategory,
            COALESCE(b.TotalRepayments, 0) AS TotalRepayments,
            DENSE_RANK() OVER (PARTITION BY a.AgeCategory ORDER BY COALESCE(b.TotalRepayments, 0) DESC) AS Rank
        FROM AgeCategoryData a
        LEFT JOIN RepaymentData b ON a.CustomerID = b.CustomerID
    )
    
    -- Final selection of required columns
    SELECT 
        CustomerID,
        Age,
        CorrectedAge,
        Gender,
        AgeCategory,
        Rank
    FROM RankData
    ORDER BY CustomerID;
    """

    return qry
