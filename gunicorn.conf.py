# Configuration optimisée pour le plan gratuit de Render (512MB de mémoire)
# Limite les ressources consommées pour éviter les timeouts et les SIGKILL
workers = 1
worker_class = "sync"
timeout = 30
max_requests = 500
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm"
preload_app = True
