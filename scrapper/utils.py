def get_param(querys, key, join_with=',', default=''):
    """Extrait les valeurs associées à une clé, les joint avec un séparateur et retourne une chaîne."""
    return join_with.join(map(str, [value for k, value in querys if k == key])) or default