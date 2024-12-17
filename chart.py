import json
import matplotlib.pyplot as plt
import numpy as np

# Lists to store the latencies
make_request_latencies = []
race_finished_latencies = []

# Read the log file and parse the latencies
with open('out.log', 'r') as f:
    for line in f:
        try:
            data = json.loads(line.strip())
            if data.get('message') == 'makeRequest completed':
                make_request_latencies.append(data['fetchTime'])
            elif data.get('message') == 'request race finished':
                race_finished_latencies.append(data['time_taken'])
        except json.JSONDecodeError:
            continue

# Function to compute CDF
def compute_cdf(data):
    sorted_data = np.sort(data)
    y = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, y

# Compute CDFs
x1, y1 = compute_cdf(make_request_latencies)
x2, y2 = compute_cdf(race_finished_latencies)

# Calculate percentage differences
def calc_percent_diff(val1, val2):
    # Returns positive number if val1 > val2 (meaning race is faster)
    return ((val1 - val2) / val1) * 100

median_diff = calc_percent_diff(np.median(make_request_latencies), np.median(race_finished_latencies))
p95_diff = calc_percent_diff(np.percentile(make_request_latencies, 95), np.percentile(race_finished_latencies, 95))
p99_diff = calc_percent_diff(np.percentile(make_request_latencies, 99), np.percentile(race_finished_latencies, 99))
p9999_diff = calc_percent_diff(np.percentile(make_request_latencies, 99.99), np.percentile(race_finished_latencies, 99.99))
max_diff = calc_percent_diff(np.max(make_request_latencies), np.max(race_finished_latencies))

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(x1, y1, label='Request latency', color='blue')
plt.plot(x2, y2, label='Perceived latency', color='red')

# Customize the plot
plt.xlabel('Latency (ms)')
plt.ylabel('Cumulative Density')
plt.title('CDF of Request Latencies (Anthropic API)')
plt.grid(True, alpha=0.3)
plt.legend()

# Add some statistics in text box
stats_text = (
    f'Request latency:\n'
    f'  median: {np.median(make_request_latencies):.1f}ms\n'
    f'  95th: {np.percentile(make_request_latencies, 95):.1f}ms\n'
    f'  99th: {np.percentile(make_request_latencies, 99):.1f}ms\n'
    f'  99.99th: {np.percentile(make_request_latencies, 99.99):.1f}ms\n'
    f'  max: {np.max(make_request_latencies):.1f}ms\n\n'
    f'Perceived latency:\n'
    f'  median: {np.median(race_finished_latencies):.1f}ms\n'
    f'  95th: {np.percentile(race_finished_latencies, 95):.1f}ms\n'
    f'  99th: {np.percentile(race_finished_latencies, 99):.1f}ms\n'
    f'  99.99th: {np.percentile(race_finished_latencies, 99.99):.1f}ms\n'
    f'  max: {np.max(race_finished_latencies):.1f}ms\n\n'
    f'Percentage speed up:\n'
    f'  median: {median_diff:+.1f}%\n'
    f'  95th: {p95_diff:+.1f}%\n'
    f'  99th: {p99_diff:+.1f}%\n'
    f'  99.99th: {p9999_diff:+.1f}%\n'
    f'  max: {max_diff:+.1f}%'
)
plt.text(0.02, 0.02, stats_text,
         transform=plt.gca().transAxes,
         bbox=dict(facecolor='white', alpha=0.8),
         fontsize=8,
         family='monospace')

plt.tight_layout()
plt.savefig('chart.png')
plt.close()
