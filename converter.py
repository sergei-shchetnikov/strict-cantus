from music21 import converter, interval, note, stream, key

def standard_to_taneyev(n):
    '''преобразует обозначение интрервалов в систему Танеева:
    для n > 1 уменьшает число на 1
    для n < -1 увеличивает число на 1
    для 1 и -1 возвращает 0
    для 0 оставляет 0
    '''
    if abs(n) == 1:
        return 0
    return n - (1 if n > 0 else -1)

def taneyev_to_standard(n):
    """ 
    Обратное преобразование из системы Танеева в обычные интервалы:
    - Если n == 0, возвращает 1 (восстанавливает секунду).
    - Если n > 0, увеличивает число на 1.
    - Если n < 0, уменьшает число на 1.
    """
    if n == 0:
        return 1
    return n + (1 if n > 0 else -1)

def melody_to_intervals(melody):
    """
    Преобразует одноголосную мелодию в список интервалов между соседними нотами.
    
    Аргументы:
        melody (str | stream.Stream): Путь к MusicXML-файлу или music21 Stream.
    
    Возвращает:
        list[int]: Список интервалов (прима = 0, секунда = ±1 и т.д.).
    """
    if isinstance(melody, str):  # Если передан путь к файлу
        melody = converter.parse(melody)  

    notes = []
    for n in melody.flatten().getElementsByClass(note.Note):
        notes.append(n)

    taneyev_intervals = []
    for i in range(1, len(notes)):
        intvl = interval.notesToGeneric(notes[i-1], notes[i])  # Определяем интервалы
        taneyev_intervals.append(standard_to_taneyev(intvl.directed))  # Добавляем направленный интервал

    return taneyev_intervals

def intervals_to_melody(taneyev_intervals, key_str, scale_degree):
    """
    Преобразует список интервалов в мелодию.

    Args:
        interval_list (list[int]): Список интервалов (например, [2, -1, 3]).
        key_str (str): Тональность мелодии: заглавная буква - мажор, строчная - минор
        (например, 'D' - ре мажор, 'e-' - ми бемоль минор).
        scale_degree (int): Ступень в тональности, с которой начинается мелодия.

    Returns:
        music21.stream.Stream: Сгенерированная мелодия.
    """
    key_obj = key.Key(key_str)
    melody = stream.Stream()
    melody.append(key_obj)  # Добавляем тональность в stream

    scale = key_obj.getScale(mode=key_obj.mode)  # Берем мажорную или минорную гамму
    start_pitch = scale.pitches[scale_degree - 1]  # Берем нужную ступень

    # Создаем первую ноту
    current_note = note.Note(start_pitch, quarterLength=4)
    melody.append(current_note)

    # Применяем интервалы
    for step in taneyev_intervals:
        interv = interval.GenericInterval(taneyev_to_standard(step))  # Создаем объект интервала
        next_pitch = interv.transposePitchKeyAware(current_note.pitch, key_obj)  # Транспонируем

        current_note = note.Note(next_pitch, quarterLength=4)
        melody.append(current_note)

    return melody

def taneyev_intervals_to_pitches(taneyev_intervals):
    """
    Преобразует список танеевских интервалов в список танеевских высот относительно первой ноты.

    Args:
        intervals (list[int]): Список интервалов в системе Танеева.

    Returns:
        list[int]: Список танеевских высот.
    """
    if not taneyev_intervals:  # Если список интервалов пустой, сразу возвращаем пустой список
        return []

    taneyev_pitches = [0]
    current_pitch = 0  # Начинаем с 0 (тоника)

    for interval in taneyev_intervals:
        current_pitch += interval  # Добавляем текущий интервал к сумме
        taneyev_pitches.append(current_pitch)

    return taneyev_pitches

def find_local_extrema(taneyev_pitches):
    """
    Находит локальные экстремумы в списке высот, который начинается и заканчивается на 0.
    Первый и последний 0 всегда включаются в список экстремумов.
    Локальные экстремумы — это элементы, которые больше или меньше своих соседей.

    Параметры:
    ----------
    pitches : list of int
        Список высот, начинающийся и заканчивающийся на 0.

    Возвращает:
    ----------
    list of int
        Список локальных экстремумов, начинающийся и заканчивающийся на 0.
    """

    taneyev_extrema = [taneyev_pitches[0]]  # Всегда начинается с 0
    n = len(taneyev_pitches)

    # Проверка внутренних элементов
    for i in range(1, n - 1):
        # Проверка для локального максимума
        if taneyev_pitches[i] > taneyev_pitches[i - 1] and taneyev_pitches[i] > taneyev_pitches[i + 1]:
            taneyev_extrema.append(taneyev_pitches[i])
        # Проверка для локального минимума
        elif taneyev_pitches[i] < taneyev_pitches[i - 1] and taneyev_pitches[i] < taneyev_pitches[i + 1]:
            taneyev_extrema.append(taneyev_pitches[i])

    taneyev_extrema.append(taneyev_pitches[-1])  # Всегда заканчивается на 0
    return taneyev_extrema

def convert_pitches_to_degrees(taneyev_pitches: list[int]) -> list[int]:
    """
    Преобразует список абсолютных высот в танеевских обозначениях
    в список ступеней в стандартных обозначениях (1 - тоника, ..., 7 - седьмая спупень).
    
    Соответствие высот ступеням:
    Высоты: [..., -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, ...]
    Ступени: [..., 1,  2,  3,  4,  5,  6,  7,  1, 2, 3, 4, 5, 6, 7, 1, ...]
    
    Параметры:
        pitch_list (list[int]): Список высот (целые числа)
        
    Возвращает:
        list[int]: Список ступеней (целые числа от 1 до 7)
    """
    return [((pitch - 1) % 7) + 1 if pitch != 0 else 1 for pitch in taneyev_pitches]