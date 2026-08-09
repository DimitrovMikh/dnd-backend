from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter-Instanz: Ermittelt die Client-IP über die Remote-Adresse
limiter = Limiter(key_func=get_remote_address)