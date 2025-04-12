from cantus import Cantus
from mode_rules import check_major_forbidden_leaps
'''
- ✓ Максимальный диапазон - децима. (cantus.range)

- ✓ Последний тон должен достигаться поступенным движением. (cantus.intervals)
- ✓ Избегать чрезмерного движения в одном направлении (больше 5 нот в линии). (cantus.intervals)
- ✓ Скачки больше терции должны быть подготовлены противоположным движением и продолжены противоположным движением. (cantus.intervals)

- ✓ Правило кульминации: самый верхний и самый нижний тоны не должны повторяться, если это не начальная и конечная нота. (cantus.pitches)
- ✓ Как минимум 2 изменения направления движения. (cantus.extremes)
- ✓ Запрещено повторение одной высоты более 4 раз за мелодию и повторение одной высоты три раза через ноту (cantus.pitches)

- ✓ Запрещены повторение нот, повторение групп нот и секвенции. (cantus.intervals)
- ✓ Запрещено опевание септимы. (cantus.pitches)

'''

def has_range_valid(cantus_obj: Cantus, max_range: int = 9) -> bool:
    '''Проверяет, что диапазон мелодии не превышает децимы: 9 '''
    return cantus_obj.range <= max_range

def has_stepwise_final(cantus_obj: Cantus) -> bool:
    '''Проверяет, что последний тон достигается поступенно '''
    intervals = cantus_obj.intervals
    return abs(intervals[-1]) == 1 and abs(intervals[-2]) == 1

def is_not_too_linear(cantus_obj: Cantus) -> bool:
    '''Проверяет, что нет слишком длинного поступенного движения в одну сторону
    более 5 нот подряд.'''
    intervals = cantus_obj.intervals

    count = 1
    for i in range(1, len(intervals)):
        if intervals[i] == intervals[i-1]:
            count += 1
            if count >= 5:
                return False
        else:
            count = 1
    return True

def are_leaps_prepared_and_filled(cantus_obj: Cantus) -> bool:
    """Проверяет, что скачки приготовлены по правилам"""
    segments_until_and_after_leaps = cantus_obj.get_segments_until_and_after_leaps

    def opp(prev, leap):
        '''Разное направление движения'''
        return leap * prev < 0
    
    def same(prev, leap):
        '''Одинаковое направление движения'''
        return prev * leap > 0

    for segment in segments_until_and_after_leaps:
        match segment:
            case [*_, prev1, leap] if same(prev1, leap):
                return False  # [1, 5, ...] ✗
                
            case [*_, prev2, prev1, leap] if (
                opp(prev1, leap) 
                and same(prev2, leap) 
                and abs(prev1) < abs(leap / 2) - 0.5 # Коэффициент достаточного заполнения скачка
            ):
                return False  # [..., -1, 1, -5] ✗
                
            case [*_, prev3, prev2, prev1, leap] if (
                opp(prev1, leap) 
                and opp(prev2, leap) 
                and same(prev3, leap) 
                and abs(prev1 + prev2) < abs(leap / 2)
            ):
                return False  # [..., 1, -1, -1, 5, ...] ✗

    return True

def check_culmination_rule(cantus_obj: Cantus) -> bool:
    '''
    Проверяет правило кульминации для списка высот нот.

    Правило кульминации:
    - Если все числа в списке высот неотрицательные, то максимальное значение должно встречаться только один раз.
    - Если все числа в списке высот неположительные, то минимальное значение должно встречаться только один раз.
    - Если в списке высот есть как положительные, так и отрицательные числа, то и максимальное, и минимальное значения
      должны встречаться только один раз.
    '''
    pitch_list = cantus_obj.pitches

    max_pitch = max(pitch_list)
    min_pitch = min(pitch_list)

    # Проверка, если все числа неотрицательные
    if all(pitch >= 0 for pitch in pitch_list):
        return pitch_list.count(max_pitch) == 1

    # Проверка, если все числа неположительные
    elif all(pitch <= 0 for pitch in pitch_list):
        return pitch_list.count(min_pitch) == 1

    # Если есть и положительные, и отрицательные числа
    else:
        return pitch_list.count(max_pitch) == 1 and pitch_list.count(min_pitch) == 1
    
def check_direction_changes(cantus_obj: Cantus) -> bool:
    """
    Проверяет, меняет ли мелодия направление как минимум 2 раза.
    """
    extremes = cantus_obj.extremes
    return len(extremes) >= 4

def no_pitch_repeats(cantus_obj: Cantus, max_repeats=3) -> bool:
    '''Проверяет, что высоты нот (pitch) не повторяются слишком часто.

    Условия:
    1. Нет тройного повторения высоты через одну ноту.
    2. Ни одна высота не повторяется max_repeats раза во всем списке.
    '''
    pitch_list = cantus_obj.pitches
        # Проверка на тройное повторение через одну ноту
    for i in range(len(pitch_list) - 4):
        # Проверяем шаблон: a, b, a, c, a
        if pitch_list[i] == pitch_list[i + 2] == pitch_list[i + 4]:
            return False

    # Проверка на повторение одной высоты 4 раза во всем списке
    pitch_counts = {}  # Словарь для подсчета высот
    for pitch in pitch_list:
        if pitch in pitch_counts:
            pitch_counts[pitch] += 1
        else:
            pitch_counts[pitch] = 1

        if pitch_counts[pitch] >= max_repeats:
            return False

    return True

def has_no_pattern(cantus_obj: Cantus) -> bool:
    """Проверяет, что в списке высот нет повторяющихся фрагментов вида a, b, ..., a, b, ..."""
    pitches = cantus_obj.pitches
    max_pattern_length = len(pitches) // 2  # Максимальная длина паттерна
    for pattern_len in range(1, max_pattern_length + 1):
        for i in range(len(pitches) - 2 * pattern_len + 1):
            pattern1 = pitches[i:i + pattern_len]
            pattern2 = pitches[i + pattern_len:i + 2 * pattern_len]
            if pattern1 == pattern2:
                return False  # Найден повторяющийся шаблон
    return True  # Повторяющихся фрагментов не найдено


def seventh_rule_satisfied(cantus_obj: Cantus) -> bool:
    """
    Проверяет, что в мелодии нет опевания септимы.
    """
    extremes = cantus_obj.extremes

    for step in range(1, len(extremes)):
        for i in range(len(extremes) - step):
            if abs(extremes[i] - extremes[i + step]) == 6:
                return False
    return True

def is_valid_melody(cantus_obj: Cantus) -> bool:
    return all([has_range_valid(cantus_obj), 
               has_stepwise_final(cantus_obj), 
               is_not_too_linear(cantus_obj), 
               are_leaps_prepared_and_filled(cantus_obj), 
               check_culmination_rule(cantus_obj), 
               check_direction_changes(cantus_obj), 
               no_pitch_repeats(cantus_obj),
               has_no_pattern(cantus_obj),
               seventh_rule_satisfied(cantus_obj),
               check_major_forbidden_leaps(cantus_obj)])


        
