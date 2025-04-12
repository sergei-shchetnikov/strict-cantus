from cantus import Cantus

def check_major_forbidden_leaps(cantus_obj: Cantus) -> bool:
    """
    Проверяет, что в мажорной мелодии нет скачков на увеличенные/уменьшенные интервалы.
    Запрещёнными считаются пары, в которых обе высоты принадлежат множеству {-8, -4, -1, 3, 6},
    и которые находятся либо рядом, либо через одну.
    """
    pitch_list = cantus_obj.pitches
    extremes = cantus_obj.extremes
    forbidden_set = {-8, -4, -1, 3, 6}
    group_a = {-8, -1, 6}
    group_b = {-4, 3}

    for i in range(len(pitch_list) - 1):
        if pitch_list[i] in forbidden_set and pitch_list[i + 1] in forbidden_set:
            return False

    for i in range(len(pitch_list) - 2):
        if pitch_list[i] in forbidden_set and pitch_list[i + 2] in forbidden_set:
            return False
        
    # Проверка, что extremes содержит элементы только из одной группы
    has_a = any(e in group_a for e in extremes)
    has_b = any(e in group_b for e in extremes)
    if has_a and has_b:
        return False
    
    return True