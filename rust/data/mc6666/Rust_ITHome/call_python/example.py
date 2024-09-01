import matplotlib.pyplot as plt
import seaborn as sns

# Load an example dataset with long-form data
df = sns.load_dataset("tips")

# Plot the responses for different events and regions
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x="day", y="tip", hue="day", data=df)
ax.get_legend().remove()            
plt.show()             