import pandas as pd
import os
from scipy.stats import levene
from scipy.stats import ttest_ind
import statsmodels.api as sm
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# plus, defining a custom color palette of greens
green_palette3 = sns.color_palette("Greens", n_colors=3)
green_palette4 = sns.color_palette("Greens", n_colors=4)
green_palette5 = sns.color_palette("Greens", n_colors=5)

df=pd.read_csv("survey_data.csv")
print(df.info())
print("\n**********\n")

# Problem statement ###################

print("Variant column indicates whether response comes from which variant in the A/B test")
print('Goal is to show whether there are significant differences in survey proportions for affected questions and wether time or bad respondent rate gets worse as a result of the change\n')
print('I will establish to counters, testnum and fails and we can later make a decision based on the number of test failed (i.e detectable changes)')
testnum=0
fails=0
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
#plt.savefig('histogram.png')

print(df.groupby('variant')['completion_minutes'].mean())
print("\n**********\n")


print('These look somewhat different. let"''"s test for equality of means')
print("i wll be using student's test, so first going to use levine's to test variance similarity\n")

# levene test

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
    testnum+=1
    fails+= 1
else:
    print("There is no statistically significant difference in mean duration.\n")
    testnum+=1
    fails+= 0
    
print('on to proportion differences')
print("\n**********\n")


# Step 2: survey response proportions: question A ###################

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
#plt.savefig('a_counts_compared.png')

print("makes more sense to use a single metric to test, so im going to merge answers associated with significant interest and test wether they vary by variant ")
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
    testnum+=1
    fails+= 1
else:
    print("There is no significant difference between variants A and B for question a.")
    testnum+=1
    fails+= 0

print("\n**********\n")
    
# Step 3: Bad respondent rate between variants ##################

print("different questionnaire approaches may be harder to understand causing responses which are inconsistent and therefore unusable")
print("therefore it is also important to assess wether the proportion of usable responses isnt affected by the change\n")

print(f"bad respondent rate in variant a: {variant_A.BR.mean()}")
print(f"bad respondent rate in variant b: {variant_B.BR.mean()}")

# testing this proportion is the same as for response rates

count_A = len(variant_A[variant_A['BR'] == 1])
count_B = len(variant_B[variant_B['BR'] == 1])

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
    print("There is a significant difference between variants A and B in terms of BR rates.")
    testnum+=1
    fails+= 1
else:
    print("There is no significant difference between variants A and B in terms of BR rates.")
    testnum+=1
    fails+=0
    
# Step 4: Pending response rates ##########################

print("remaining proportions to evaluate:\n")
for q in list([df.answer_b,df.answer_c,df.answer_d,df.answer_e]):
    print(q.value_counts(normalize=True))
    print("*"*3)
    
# b, c and d are analogue so i can probably loop

for q in list(['answer_b','answer_c','answer_d']):
    print(f"sample proportion equality testing on {q}")
    count_A = len(variant_A[variant_A[q] == "Yes"])
    count_B = len(variant_B[variant_B[q] == "Yes"])

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
        print(f"There is a significant difference between variants A and B regarding {q}")
        testnum+=1
        fails+= 1
    else:
        print(f"There is no significant difference between variants A and B regarding {q}")
        testnum+=1
        fails+= 0
    print("****\n")
    
print("the process for question e is quite the same, just the loop parameter changing\n")

for u in df.answer_e.unique():
    print(f"sample proportion equality testing on {u} response rates for question e")
    count_A = len(variant_A[variant_A['answer_e'] == u])
    count_B = len(variant_B[variant_B['answer_e'] == u])

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
        print(f"There is a significant difference between variants A and B regarding {u} in answer_e")
        testnum+=1
        fails+= 1
    else:
        print(f"There is no significant difference between variants A and B regarding {u} in answer_e")
        testnum+=1
        fails+= 0
    print("****\n")
    
print("CONCLUSION:\n")

print(f"out of {testnum} tests, {fails} indicate significant differences in the results of the alternative designs")