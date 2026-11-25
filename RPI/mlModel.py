#Version 0.3.0
#Infer RSSI between measured positions for more granular mapping of WiFi signal strength in a given area,
#then infer the best permanent placement of the WiFi access point.
#Input CSV columns: x, y, avg_rssi, rssi_ESP32_1..3, timestamp (unix seconds).
#Only x, y and avg_rssi are used for modelling; the other columns are kept untouched for debugging/analysis.
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

CSV_PATH = 'position.csv'
RSSI_COL = 'avg_rssi'
STEP_SIZE = 0.10           # metres, spacing of inferred points along each path segment
MAX_JUMP = 3.0             # metres, a point this far from BOTH neighbours is a position glitch
ROOM_HEIGHT = 2.7          # metres, max height of room (AP mounted at ceiling)
PI_HEIGHT = 1.0            # metres, height of the roaming Pi's antenna
GRID_RES = 0.10            # metres, resolution of candidate-placement grid
MIN_DIST = 0.5             # metres, avoid log10(0) near the AP

df = pd.read_csv(CSV_PATH)
#If this script already ran, drop previously inferred rows so they don't compound
if 'interpolated' in df.columns:
    df = df[~df['interpolated'].astype(bool)].drop(columns='interpolated')
df = df.sort_values('timestamp', kind='stable').reset_index(drop=True)


#--- Clean: flag position glitches (single-sample spikes, e.g. x=-12.77) ---
xy_all = df[['x', 'y']].to_numpy(dtype=float)
step = np.hypot(*np.diff(xy_all, axis=0).T)
jump_prev = np.r_[np.inf, step]
jump_next = np.r_[step, np.inf]
glitch = (jump_prev > MAX_JUMP) & (jump_next > MAX_JUMP)
clean = df[~glitch].reset_index(drop=True)
print(f'Ignoring {glitch.sum()} glitched position(s): '
      f'{df.loc[glitch, ["x", "y"]].to_numpy().tolist()}')

xy = clean[['x', 'y']].to_numpy(dtype=float)
rssi = clean[RSSI_COL].to_numpy(dtype=float)


#--- Fit a log-distance path-loss model: RSSI = P0 - 10*n*log10(d) ---
#Unknowns: effective source location (ax, ay), reference power P0 at 1 m, path-loss exponent n
def path_loss(params, pts):
    ax, ay, p0, n = params
    d = np.maximum(np.hypot(pts[:, 0] - ax, pts[:, 1] - ay), MIN_DIST)
    return p0 - 10 * n * np.log10(d)

start = np.r_[xy[np.argmax(rssi)], rssi.max(), 2.5]   # start at the strongest reading
fit = least_squares(lambda p: path_loss(p, xy) - rssi, start, loss='soft_l1', f_scale=3.0,
                    bounds=([-np.inf, -np.inf, -100, 1.5], [np.inf, np.inf, 0, 6]))
ax, ay, p0, n_exp = fit.x
residuals = rssi - path_loss(fit.x, xy)
print(f'Path-loss fit: P0={p0:.1f} dBm, n={n_exp:.2f}, strongest-signal centre at ({ax:.2f}, {ay:.2f}), '
      f'MAE={np.mean(np.abs(residuals)):.2f} dB')


#--- Infer RSSI between each pair of consecutive positions and write to CSV ---
#Points are spaced STEP_SIZE apart along each segment (none for repeated/near-identical positions).
#Each inferred value = path-loss prediction + residual linearly blended between the two endpoints,
#so values pass exactly through the measured readings and follow the physics in between.
new_rows = []
for i in range(len(clean) - 1):
    seg_len = np.hypot(*(xy[i + 1] - xy[i]))
    n_new = int(seg_len // STEP_SIZE) - (seg_len % STEP_SIZE < 1e-9)   # points strictly inside the segment
    for k in range(1, n_new + 1):
        t = k / (n_new + 1)
        pt = (1 - t) * xy[i] + t * xy[i + 1]
        pred = path_loss(fit.x, pt[None, :])[0] + (1 - t) * residuals[i] + t * residuals[i + 1]
        ts0, ts1 = clean.at[i, 'timestamp'], clean.at[i + 1, 'timestamp']
        new_rows.append({'x': round(pt[0], 2), 'y': round(pt[1], 2), RSSI_COL: round(pred, 1),
                         'timestamp': round(ts0 + t * (ts1 - ts0), 3), 'interpolated': True})

orig = df.assign(interpolated=False)          # keeps glitch rows + ESP32 debug columns as-is
dense = (pd.concat([orig, pd.DataFrame(new_rows)], ignore_index=True)
           .sort_values('timestamp', kind='stable')[list(df.columns) + ['interpolated']])
dense.to_csv(CSV_PATH, index=False)
print(f'Wrote {len(dense)} rows ({len(new_rows)} inferred) to {CSV_PATH}')


#--- Determine permanent placement of WiFi access point ---
#Search a grid over the surveyed area for the AP spot that maximises the WORST predicted RSSI
#across every surveyed position (best coverage of weak spots), using the fitted P0 and n.
pts = np.unique(np.round(np.r_[xy, dense.loc[dense['interpolated'], ['x', 'y']].to_numpy(float)], 2), axis=0)
gx = np.arange(pts[:, 0].min(), pts[:, 0].max() + GRID_RES, GRID_RES)
gy = np.arange(pts[:, 1].min(), pts[:, 1].max() + GRID_RES, GRID_RES)
cx, cy = np.meshgrid(gx, gy)
cand = np.c_[cx.ravel(), cy.ravel()]

dz = ROOM_HEIGHT - PI_HEIGHT
worst = np.empty(len(cand))
mean = np.empty(len(cand))
for j in range(0, len(cand), 2000):           # chunked to keep memory low on a Pi
    c = cand[j:j + 2000]
    d = np.sqrt((pts[None, :, 0] - c[:, None, 0])**2 + (pts[None, :, 1] - c[:, None, 1])**2 + dz**2)
    pred = p0 - 10 * n_exp * np.log10(np.maximum(d, MIN_DIST))
    worst[j:j + 2000] = pred.min(axis=1)
    mean[j:j + 2000] = pred.mean(axis=1)
best = np.lexsort((-mean, -worst))[0]          # best worst-case, ties broken by average signal

x_position, y_position = cand[best]
z_position = ROOM_HEIGHT
print(f'Recommended AP placement: x={x_position:.2f}, y={y_position:.2f}, z={z_position:.2f} '
      f'(worst-case RSSI {worst[best]:.1f} dBm, mean {mean[best]:.1f} dBm)')
