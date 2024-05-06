import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define the path to the BIDS dataset directory
bids_dir = '/home/spinney/project/data/neuroventure/bids'

# Initialize a list to store all data
all_data = []
list_of_unaligned = []

# Loop through all subjects and sessions
for root, dirs, files in os.walk(bids_dir):
    for file in files:
        if file.endswith('events.tsv') and 'stop' in file:
            events_file = os.path.join(root, file)
            # Extract subject and session from filename using regex
            match = re.match(r'sub-(\d+)_ses-(\d+)_', file)
            subject = match.group(1)
            session = match.group(2)
            # Load the events file into a DataFrame
            events_df = pd.read_csv(events_file, sep='\t')
            # Extract first and last onset times
            try:
                first_onset_time = events_df['onset'].iloc[0]
                last_onset_time = events_df['onset'].iloc[-1]
                if float(first_onset_time) > 1.0:
                     list_of_unaligned.append(f"sub-{subject}/ses-{session}")
                # Append to all data list as dictionary
                all_data.append({'subject': subject, 'session': session, 'onset': first_onset_time, 'time': 'first'})
                all_data.append({'subject': subject, 'session': session, 'onset': last_onset_time, 'time': 'last'})
            except:
                print(f"Empty stop event file for {subject} at {session}")

# Convert the all data list to DataFrame
all_data_df = pd.DataFrame(all_data)

# Set seaborn style
sns.set(style="whitegrid")

# Create the panel plot with separate plots for each session in a single column
g = sns.FacetGrid(all_data_df, col='session', hue='time', col_wrap=1, height=12, aspect=2, sharex=False, sharey=False)
g.map(sns.histplot, 'subject', 'onset', bins=20, alpha=0.5)
g.add_legend()
g.set_axis_labels('Subject', 'Onset Time')
g.set_titles(col_template="Session {col_name}")
plt.xticks(rotation=45)  # Rotate x-axis labels
plt.tight_layout()
plt.savefig('panel_plot.png')
plt.close()

print("Panel plot saved successfully.")

print("List of subjects with first onset larger than 1s")
print(list_of_unaligned)
