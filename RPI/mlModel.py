#Version 0.1.0
#Predict next RSSI value for more granular mapping of WiFi signal strength in a given area
#Import ml libraries
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv('rssi_distance_data.csv')  # Import time stamped wifi RSSI .csv file
#Predict rssi value at next position based on rssi and distance data from previous positions
X = df[['rssi', 'distance']]  # Features: RSSI and distance
y = df['next_rssi']  # Target: next RSSI value

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

#Print model evaluation metrics
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'Mean Absolute Error: {mae}')
print(f'R-squared: {r2}')
#End predictive model code

#Determine permanent placement of WiFi access point based on predicted RSSI values and distance measurements
x_position = 0.0  # Placeholder for x-coordinate of the access point
y_position = 0.0  # Placeholder for y-coordinate of the access point
z_position = 0.0  # Max height of room

