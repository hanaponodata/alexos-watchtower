import time
from flask import Blueprint, render_template

perf_panel = Blueprint('perf_panel', __name__)

@perf_panel.route('/perf')
def perf():
    # Example: fetch metrics from backend
    p95_latency = 120  # ms, stub
    fps = 60  # stub
    return render_template('perf_panel.html', p95_latency=p95_latency, fps=fps) 