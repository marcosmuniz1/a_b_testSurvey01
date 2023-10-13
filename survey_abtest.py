import pandas as pd
import os
from scipy.stats import levene
from scipy.stats import ttest_ind

os.chdir("C:/Users/marco/Dropbox (MPD)/Analytics Argentina/Personal Files/MM/Python/PYMNTS_Stuff/user_cluster_analysis")
df=pd.read_csv("survey_data.csv")

print(df.groupby('variant')['completion_minutes'].mean())

# These look somewhat different. let's test for equality of means

## we are going to use The ttest_ind function that is part of the scipy.stats module
## ttest_ind is specifically used for performing an independent two-sample t-test.
## This test is also known as the Student's t-test and is used to determine if there is a
## statistically significant difference between the means of two independent groups (samples). 
# the only prerequiste pending is to assess equality of variances, i can use Levene's test

duration_a = df[df['variant'] == 'A']['completion_minutes']
duration_b = df[df['variant'] == 'B']['completion_minutes']

stat, p_value = levene(duration_a,duration_b)

if p_value < 0.05:
    print("The variances are significantly different (heteroscedastic).")
else:
    print("There is no significant difference in variances (homoscedastic).")

# now we can do student's test

t_stat, p_value = ttest_ind(duration_a, duration_b)

# Print the results
print(f'T-statistic: {t_stat}')
print(f'P-value: {p_value}')

if p_value < 0.05:
    print("The difference in mean duration is statistically significant.")
else:
    print("There is no statistically significant difference in mean duration.")