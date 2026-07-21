# pyrefly: ignore [missing-import]
import kagglehub
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Visualisation
plt.scatter(salary_df['YearsExperience'],salary_df['Salary'])
plt.xlabel("Years of Experience")
plt.ylabel("Salary")
plt.title("Years of Experience vs Salary")
plt.show()

#Correlation analysis
salary_corellation = salary_df.corr()
print("Correlation analysis")
print(salary_corellation)
sns.heatmap(salary_corellation)


