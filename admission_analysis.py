import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Create the data
data = {
    'date': ['30-Jan-24', '09-Feb-24', '14-Feb-24', '22-Apr-24', '13-May-24', '14-May-24', 
             '17-May-24', '06-Jun-24', '26-Jun-24', '27-Jun-24', '04-Jul-24', '11-Jul-24',
             '15-Jul-24', '24-Aug-24', '25-Aug-24', '24-Sept-24', '24-Oct-24', '26-Oct-24',
             '27-Oct-24', '28-Oct-24', '01-Nov-24', '10-Nov-24', '10-Nov-24', '11-Nov-24',
             '11-Nov-24', '21-Nov-24', '24-Nov-24', '24-Nov-24', '25-Nov-24'],
    'time_of_admission': ['17:00', '10:45', '01:30', '20:01', '17:25', '21:00', '01:10',
                         '00:05', '12:45', '17:14', '11:51', '11:09', '14:15', '05:00',
                         '03:00', '20:19', '18:00', '14:10', '18:35', '05:00', '00:40',
                         '17:20', '23:00', '13:35', '21:30', '21:20', '11:17', '16:50', '20:15'],
    'booking_status': ['booked', 'booked', 'post natal', 'booked', 'booked', 'booked',
                      'post nat', 'unbooked', 'unbooked', 'unbooked', 'unbooked', 'unbooked',
                      'booked', 'booked', 'booked', 'booked', 'booked', 'booked', 'booked',
                      'unbooked', 'unbooked', 'booked', 'booked', 'booked', 'booked',
                      'booked', 'booked', 'booked', 'booked'],
    'age': [40, 18, 25, 22, 23, 34, 34, 26, 33, 36, 34, 31, 20, 33, 20, 20, 15, 16,
            21, 29, 24, 24, 27, 31, 27, 25, 22, 38, 23],
    'estimated_gestational_age': [24, 26, 'postnatal', 35, 40, 33, 'postnatal', 30, 36, 34,
                                35, 30, 35, 30, 30, 26, 27, 22, 29, 24, 25, 35, 36, 28,
                                27, 35, 26, 28, 30],
    'diagnosis': ['schizophrenia', 'syncope spells', 'post partum pyschosis', 'seizure',
                 'seizure', 'anxiety', 'substance use', 'syncope', 'depression', 'low mood',
                 'depression', 'low mood', 'anxiety', 'seizure', 'seizure', 'parasuicide',
                 'seizure', 'seizure', 'parasuicide', 'parasuicide', 'parasuicide', 'syncope',
                 'syncope', 'anxiety', 'pyschogenic seizures', 'psychotic episode',
                 'parasuicide', 'anxiety', 'depression']
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y')

# Create visualizations directory
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# 1. Diagnosis Distribution
plt.figure(figsize=(12, 6))
diagnosis_counts = df['diagnosis'].value_counts()
diagnosis_counts.plot(kind='bar')
plt.title('Distribution of Diagnoses')
plt.xlabel('Diagnosis')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('visualizations/diagnosis_distribution.png')
plt.close()

# 2. Age Distribution
plt.figure(figsize=(10, 6))
plt.hist(df['age'], bins=15, edgecolor='black')
plt.title('Age Distribution of Patients')
plt.xlabel('Age')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('visualizations/age_distribution.png')
plt.close()

# 3. Booking Status Distribution
plt.figure(figsize=(8, 6))
booking_counts = df['booking_status'].value_counts()
plt.pie(booking_counts, labels=booking_counts.index, autopct='%1.1f%%')
plt.title('Distribution of Booking Status')
plt.tight_layout()
plt.savefig('visualizations/booking_status_distribution.png')
plt.close()

# 4. Admissions Over Time
plt.figure(figsize=(12, 6))
df['month'] = df['date'].dt.strftime('%B')
monthly_counts = df.groupby('month').size()
monthly_counts.plot(kind='bar')
plt.title('Number of Admissions by Month')
plt.xlabel('Month')
plt.ylabel('Number of Admissions')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('visualizations/admissions_by_month.png')
plt.close()

# 5. Time of Admission Distribution
df['hour'] = pd.to_datetime(df['time_of_admission']).dt.hour
plt.figure(figsize=(12, 6))
plt.hist(df['hour'], bins=24, range=(0, 24), edgecolor='black')
plt.title('Distribution of Admission Times')
plt.xlabel('Hour of Day (24-hour format)')
plt.ylabel('Number of Admissions')
plt.xticks(range(0, 24, 2))
plt.tight_layout()
plt.savefig('visualizations/admission_times_distribution.png')
plt.close()

# Print Summary Statistics
print("\nSummary Statistics:")
print("\n1. Total number of admissions:", len(df))
print("\n2. Average age of patients:", round(df['age'].mean(), 2))
print("\n3. Most common diagnoses:")
print(df['diagnosis'].value_counts().head())
print("\n4. Booking status distribution:")
print(df['booking_status'].value_counts())
print("\n5. Age range:", f"Minimum: {df['age'].min()}, Maximum: {df['age'].max()}")

# Additional Analysis
print("\nKey Findings:")
print(f"1. Most common diagnosis: {df['diagnosis'].mode()[0]}")
print(f"2. Percentage of booked cases: {(df['booking_status'] == 'booked').mean()*100:.1f}%")
print(f"3. Most common admission month: {df.groupby('month').size().idxmax()}")
print(f"4. Average patient age: {df['age'].mean():.1f} years")

print("\nAnalysis complete. Visualizations have been saved to the 'visualizations' folder.")
