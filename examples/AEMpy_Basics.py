import aempy

# 1. Conect and get version

# Connect to the AEM Instance
instance = aempy.AEM()

# Get product information
productinfo = instance.info()

# Print product version
print(productinfo.version)

# 2. Get error logs

# Connect to the system console
system = aempy.System()

# Get the five first line of the error.log file
errorlogs = system.log_error(5)

# Print the lines
print(errorlogs)

# 3. Parse logs

# Get the 10.000 first lines of error.log
errorlogs = system.log_error()

# Import Pandas library
import pandas as pd

# Split the logs and arrange in a table using the Pandas library
dfLog = pd.DataFrame([sub.split(" ") for sub in errorlogs])

# Add Names to the columns
dfLog = dfLog.rename(columns={0:'date',1:'time',2:'level',3:'ID',4:'class',5:'msg'})


# Print the parsed logs
print(dfLog)

# 4. Convert logs to Pandas Dataframe
dfErrors = system.log_to_pandas(errorlogs)

print(dfErrors.head())

print(dfErrors.describe())

# Analyze the errors
dfLevelError = dfErrors[dfErrors["level"].str.match("ERROR")]
print("Information about log errors:")

# Display the first 5 lines
print(dfLevelError.head())

# Display the last 5 lines
print(dfLevelError.tail())

# Describe the table
print(dfLevelError.describe())
