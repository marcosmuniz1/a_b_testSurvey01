import pandas as pd
import os
from scipy.stats import levene
from scipy.stats import ttest_ind
import statsmodels.api as sm
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Define a custom color palette of greens
green_palette3 = sns.color_palette("Greens", n_colors=3)
green_palette4 = sns.color_palette("Greens", n_colors=4)
green_palette5 = sns.color_palette("Greens", n_colors=5)

df=pd.read_csv("survey_data.csv")
print(df.info())
print("\n**********\n")

# Problem statement ###################

print("Variant column indicates whether response comes from which variant in the A/B test")
print('Goal is to show wether there are significant differences in survey proportions for affected questions and wether time or bad respondent rate gets worse as a result of the change\n')
print('Easiest seems to be survey duration so lets start by looking at that')
print("\n**********\n")

variant_A = df[df['variant'] == 'A']
variant_B = df[df['variant'] == 'B']

# Step 1: survey lenght differences: ###################

duration_a = variant_A['completion_minutes']
duration_b = variant_B['completion_minutes']

plt.hist(duration_a, histtype='stepfilled', density=True, color="lightblue",label='Variant A')
plt.hist(duration_b, histtype='step',density=True, label='Variant B')
plt.xlabel('Duration (minutes)')
plt.ylabel('Frequency')
plt.legend()
plt.title('Frequency Distribution of Survey Duration')
plt.savefig('histogram.png')

print(df.groupby('variant')['completion_minutes'].mean())
print("\n**********\n")


print('These look somewhat different. let"''"s test for equality of means')
print("i wll be using student's test, so first going to use levine's to test variance similarity\n")

# levene

print ("Levene's test for variance differences:")
stat, p_value = levene(duration_a,duration_b)
if p_value < 0.05:
    print("The variances are significantly different (heteroscedastic)\n")
else:
    print("There is no significant difference in variances (homoscedastic)\n")

# student's test

print ("Student equality of means:\n")
t_stat, p_value = ttest_ind(duration_a, duration_b)

# Print the results
print(f'T-statistic: {t_stat}')
print(f'P-value: {p_value}')

if p_value < 0.05:
    print("The difference in mean duration is statistically significant.\n")
else:
    print("There is no statistically significant difference in mean duration.\n")
    
print('on to proportion differences')
print("\n**********\n")


# Step 2: survey response proportions: question A #####

print("question A:")

# value counts by variant
a_counts = df.groupby('variant')['answer_a'].value_counts(normalize=True).reset_index(name='count')

# Pivot the DataFrame for plotting
pivot_data = a_counts.pivot(index='variant', columns='answer_a', values='count')

fig, ax = plt.subplots(figsize=(10, 6))
sns.set_palette(green_palette4)
pivot_data.plot(kind='bar', stacked=True, ax=ax)

plt.title('Response Rates by Variant')
plt.xlabel('Variant')
plt.ylabel('Normalized Count')
plt.legend(title='Response')

plt.legend(title='Response', bbox_to_anchor=(1.05, 1), loc='upper left')

for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.annotate(f'{height:.2%}', (x + width/2, y + height/2), ha='center')

plt.tight_layout()
plt.savefig('a_counts_compared.png')

print("makes more sense to use a single metric to test, so im going to merge answers assoicated with significant interest and test wether they vary by variant ")
print("checking for proportion differences in response rates for Somewhat interested or more:")

# reseting question a) so it only has two values:

df['answer_a_condensed']=np.where(
    (df.answer_a=='Not at all interested') | (df.answer_a=='Slightly interested') , 'Less than somewhat interested',
    np.where((df.answer_a=='Somewhat interested') | (df.answer_a=='Very interested') , 'Somewhat interested or more',
    "oh no, error!!"))

# need to update my subsets as we have a new column

variant_A = df[df['variant'] == 'A']
variant_B = df[df['variant'] == 'B']

# prepping input for sample proportions test: count and subset size

count_A = len(variant_A[variant_A['answer_a_condensed'] == 'Somewhat interested or more'])
count_B = len(variant_B[variant_B['answer_a_condensed'] == 'Somewhat interested or more'])

n_A = len(variant_A)
n_B = len(variant_B)

# Perform the two-proportion z-test
stat, pval = proportions_ztest([count_A, count_B], [n_A, n_B])

# Output the test results
print(f"Z-statistic: {stat}")
print(f"P-value: {pval}")

# Determine significance
alpha = 0.05  # Set your desired significance level
if pval < alpha:
    print("There is a significant difference between variants A and B for question a.")
else:
    print("There is no significant difference between variants A and B for question a.")