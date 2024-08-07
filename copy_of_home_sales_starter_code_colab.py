# -*- coding: utf-8 -*-
"""Copy_of_Home_Sales_starter_code_colab.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sdGChez135Uv0_kyLInTO27v5sqWGSJK
"""

import os
# Find the latest version of spark 3.x  from http://www.apache.org/dist/spark/ and enter as the spark version
# For example:
# spark_version = 'spark-3.5.1'
spark_version = 'spark-3.5.1'
os.environ['SPARK_VERSION']=spark_version

# Install Spark and Java
!apt-get update
!apt-get install openjdk-11-jdk-headless -qq > /dev/null
!wget -q http://www.apache.org/dist/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz
!tar xf $SPARK_VERSION-bin-hadoop3.tgz
!pip install -q findspark

# Set Environment Variables
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["SPARK_HOME"] = f"/content/{spark_version}-bin-hadoop3"

# Start a SparkSession
import findspark
findspark.init()

# Import packages
from pyspark.sql import SparkSession
import time

# Create a SparkSession
spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

# 1. Read in the AWS S3 bucket into a DataFrame.
from pyspark import SparkFiles
url = "https://2u-data-curriculum-team.s3.amazonaws.com/dataviz-classroom/v1.2/22-big-data/home_sales_revised.csv"
spark.sparkContext.addFile(url)
home_df=spark.read.csv(SparkFiles.get("home_sales_revised.csv"),sep=",",header=True)
home_df.show()

# 2. Create a temporary view of the DataFrame.

home_df.createOrReplaceTempView('home_sales')

# 3. What is the average price for a four bedroom house sold per year, rounded to two decimal places?

four_bed_avg=spark.sql(""" select round(avg(price),2), year(date) from home_sales where bedrooms = 4 group by year(date) order by year(date) """)
four_bed_avg.show()

# 4. What is the average price of a home for each year the home was built,
# that have 3 bedrooms and 3 bathrooms, rounded to two decimal places?

three_bed_bath_avg=spark.sql(""" select round(avg(price),2), date_built from home_sales where bedrooms = 3 and bathrooms = 3 group by date_built order by date_built """)
three_bed_bath_avg.show()

# 5. What is the average price of a home for each year the home was built,
# that have 3 bedrooms, 3 bathrooms, with two floors,
# and are greater than or equal to 2,000 square feet, rounded to two decimal places?
three_bed_bath_floors_avg=spark.sql(""" select round(avg(price),2), date_built from home_sales where bedrooms = 3 and bathrooms = 3 and floors = 2 and sqft_living >= 2000 group by date_built order by date_built """)

three_bed_bath_floors_avg.show()

# 6. What is the average price of a home per "view" rating, rounded to two decimal places,
# having an average home price greater than or equal to $350,000? Order by descending view rating.
# Although this is a small dataset, determine the run time for this query.

start_time = time.time()

spark.sql(""" select round(avg(price),2), view from home_sales group by view having avg(price) >= 350000 order by view""").show()

print("--- %s seconds ---" % (time.time() - start_time))

# 7. Cache the the temporary table home_sales.
spark.sql("cache table home_sales")

# 8. Check if the table is cached.
spark.catalog.isCached('home_sales')

# 9. Using the cached data, run the last query above, that calculates
# the average price of a home per "view" rating, rounded to two decimal places,
# having an average home price greater than or equal to $350,000.
# Determine the runtime and compare it to the uncached runtime.

start_time = time.time()
spark.sql(""" select round(avg(price),2), view from home_sales group by view having avg(price) <= 350000 order by view""").show()


print("--- %s seconds ---" % (time.time() - start_time))

# 10. Partition by the "date_built" field on the formatted parquet home sales data
home_df.write.partitionBy("date_built").mode("overwrite").parquet("home_parquet")

# 11. Read the parquet formatted data.
parquet_df=spark.read.parquet('home_parquet')

# 12. Create a temporary table for the parquet data.
parquet_df.createOrReplaceTempView('parquet_temp')

# 13. Using the parquet DataFrame, run the last query above, that calculates
# the average price of a home per "view" rating, rounded to two decimal places,
# having an average home price greater than or equal to $350,000.
# Determine the runtime and compare it to the cached runtime.

start_time = time.time()

spark.sql(""" select round(avg(price),2), view from parquet_temp group by view having avg(price) < 350000 order by view""").show()

print("--- %s seconds ---" % (time.time() - start_time))

# 14. Uncache the home_sales temporary table.
spark.sql("uncache table home_sales")

# 15. Check if the home_sales is no longer cached

if spark.catalog.isCached('home_sales') :
  print("a table is still cached")
else:
  print("all clear")
