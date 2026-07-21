# pyrefly: ignore [missing-import]
from sklearn.linear_model import LinearRegression
import kagglehub
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.api import OLS
from statsmodels.api import add_constant
from scipy import stats

# Download latest version
path = kagglehub.dataset_download("abhishek14398/salary-dataset-simple-linear-regression")

# Raed in the database
salary_df = pd.read_csv(path+"/Salary_dataset.csv")

# Database describtions
print(salary_df.head())
salary_df.drop(salary_df.columns[[0]], axis = 1, inplace=True)
print(salary_df.head())

print("\nData Description")
print(salary_df.describe())

print("\nMissing Values")
print(salary_df.isnull().sum())

print("\nData Info")
salary_df.info()

print("\nData Shape")
print(salary_df.shape)
"""
# Visualisation
plt.scatter(salary_df['YearsExperience'],salary_df['Salary'])
plt.xlabel("Years of Experience")
plt.ylabel("Salary")
plt.title("Years of Experience vs Salary")
plt.show()

# Bar chart of how many people have each level of experience (rounded to nearest integer)
experience_counts = salary_df['YearsExperience'].round().value_counts().sort_index()

plt.figure(figsize=(10, 6))
sns.barplot(x=experience_counts.index.astype(int), y=experience_counts.values, palette='viridis', hue=experience_counts.index.astype(int), legend=False)
plt.xlabel('Years of Experience (Rounded)')
plt.ylabel('Number of People')
plt.title('Number of People by Years of Experience')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()



#Correlation analysis
salary_corellation = salary_df.corr()
print("Correlation analysis")
print(salary_corellation)
sns.heatmap(salary_corellation)
plt.show()
"""
# Normality Tests
print("\nNormality Tests (Shapiro-Wilk Test)")
for column in salary_df.columns:
    stat, p_val = stats.shapiro(salary_df[column])
    print(f"Variable: {column}")
    print(f"  Statistic={stat:.4f}, p-value={p_val:.4f}")
    if p_val > 0.05:
        print("  Result: The data is normally distributed (fail to reject H0 at 5% significance level).")
    else:
        print("  Result: The data is NOT normally distributed (reject H0 at 5% significance level).")


# Running linear regression
y_variable = pd.DataFrame(salary_df["Salary"])
x_variables = pd.DataFrame(salary_df["YearsExperience"])
model = LinearRegression().fit(x_variables, y_variable)

print("R-squared: ", model.score(x_variables, y_variable))

#Statsmodels OLS
model_ols = OLS(y_variable, add_constant(x_variables)).fit()
print(model_ols.summary())

# Regression diagnostics and analysis of assumptions
 # Homoscedasticity
plt.scatter(model_ols.predict(), model_ols.resid)
plt.xlabel("Fitted Values")
plt.ylabel("Residuals")
plt.title("Residuals vs Fitted Values")
plt.show()

# Durbin-Watson statistic
print("Durbin-Watson statistic: ", model_ols.durbin_watson)

# QQ-plot
import statsmodels.api as sm
import matplotlib.pyplot as plt

fig = sm.qqplot(model_ols.resid, line='s')
plt.title("QQ-Plot of Residuals")
plt.show()

# Residuals Histogram

plt.hist(model_ols.resid, bins=20)
plt.xlabel("Residuals")
plt.ylabel("Frequency")
plt.title("Histogram of Residuals")
plt.show()

# Normality test of residuals
stat, p_val = stats.shapiro(model_ols.resid)
print(f"Variable: {column}")
print(f"  Statistic={stat:.4f}, p-value={p_val:.4f}")
if p_val > 0.05:
    print("  Result: The data is normally distributed (fail to reject H0 at 5% significance level).")
else:
    print("  Result: The data is NOT normally distributed (reject H0 at 5% significance level).")