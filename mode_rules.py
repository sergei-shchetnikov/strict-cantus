from cantus import Cantus

def check_major_forbidden_leaps(cantus_obj: Cantus) -> bool:
    """
    Проверяет, что в мажорной мелодии нет скачков на увеличенные/уменьшенные интервалы.
    Конкретно - нет соседних высот, где обе принадлежат множеству {-8, -4, -1, 3, 6}.

    Параметры:
        pitch_list (list[int]): Список высот нот в танеевских ступенях.

    Возвращает:
        bool: False если найдены запрещённые скачки, True если таких скачков нет.

    Примеры:
        >>> check_major_forbidden_leaps([0, 2, 4, 3, 1, 0])  # Допустимая мажорная мелодия
        True
        >>> check_major_forbidden_leaps([0, 3, 6, 4, 1, 0])    # Запрещённый скачок 3-6
        False
    """
    pitch_list = cantus_obj.pitches
    forbidden_pairs = {-8, -4, -1, 3, 6}
    
    for i in range(len(pitch_list) - 1):
        current = pitch_list[i]
        next_pitch = pitch_list[i + 1]
        
        if current in forbidden_pairs and next_pitch in forbidden_pairs:
            return False
            
    return True