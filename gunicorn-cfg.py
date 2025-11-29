# -*- encoding: utf-8 -*-
"""
Copyright (c) 2025 - present vip.masmoudiweddingplanner.com

Gunicorn configuration for production on QNAP TS-264
"""

# Bind to all IP addresses inside the container on port 8000
bind = '0.0.0.0:8000'

# Number of worker processes
# 4 workers is suitable for 4 cores and 8GB RAM of the NAS
workers = 4

# Worker type (sync is default, good for most Flask apps)
worker_class = 'sync'

# Logging configuration
accesslog = '-'      # log access messages to stdout
errorlog = '-'       # log errors to stdout
loglevel = 'info'    # 'info' is recommended for production

# Capture stdout/stderr from Flask and other libraries
capture_output = True
enable_stdio_inheritance = True

# Timeout for requests in seconds
# Prevents workers from hanging on long requests
timeout = 120        

# Max requests before restarting a worker
# Helps prevent memory leaks
max_requests = 1000
max_requests_jitter = 50
