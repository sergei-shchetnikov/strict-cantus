from dataclasses import dataclass
from typing import List
from converter import intervals_to_melody

@dataclass
class Cantus:
    """Класс для представления cantus firmus в виде, абстрагированном от лада
    и качества интервалов (большие, малые, уменьшенные и т. д.), а также от 
    длительности нот.

    Интервалы между парами соседних нот в мелодии в танеевской системе обозначений:
    ...    
    -3: кварта вниз
    -2: терция вниз
    -1: секунда вниз
    0: прима
    1: секунда вверх
    2: терция вверх
    3: кварта вверх
    ...

    """
    SECONDS = {-1, 1}
    THIRDS = {-2, 2}
    FOURTHS = {-3, 3}
    FIFTHS = {-4, 4}
    SIXTHS = {5}

    intervals: List[int] # Список интервалов между парами соседних нот в мелодии.

    @property
    def length(self):
        """Возвращает длину мелодии - количество нот."""
        return len(self.intervals) + 1    

    def notes_string(self, mode: str) -> str:
        """Возвращает строку нот мелодии в до мажоре или ля миноре."""
        if mode == 'major':
            melody = intervals_to_melody(self.intervals, 'C', 1)
        elif mode == 'minor':
            melody = intervals_to_melody(self.intervals, 'a', 1)
        else:
            raise ValueError("Mode must be either 'major' or 'minor'")
        
        notes = []
        for note in melody.notes:
            notes.append(note.nameWithOctave)
        return ' '.join(notes)
    
    @property
    def range(self):
        """Вычисляет диапазон как разницу между максимальной и минимальной высотой."""
        return max(self.pitches) - min(self.pitches)

    @property
    def pitches(self) -> List[int]:
        '''Возвращает высоты относительно первого тона.'''
        calculated_pitches = [0]
        for interval in self.intervals:
            calculated_pitches.append(calculated_pitches[-1] + interval)
        return calculated_pitches

    @property
    def degrees(self) -> List[int]:
        """Возвращает ступени относительно первого тона.
        
        Соответствие высот и ступеней:
        Высоты:  [..., -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, ...]
        Ступени: [...,  0,  1,  2,  3,  4,  5,  6, 0, 1, 2, 3, 4, 5, 6, 0, ...]

        """
        return [self._pitch_to_degree(p) for p in self.pitches]

    def _pitch_to_degree(self, height: int) -> int:
        """Конвертирует высоту в ступень."""
        return (height) % 7

    @property
    def extremes(self):
        """Возвращает список локальных экстремумов в списке высот.
        Первая и последняя высоты всегда включаются в этот список.
        """
        extremes_list = [self.pitches[0]]  # Всегда добавляем первый элемент

        for i in range(1, len(self.pitches) - 1):
            prev = self.pitches[i - 1]
            current = self.pitches[i]
            next_ = self.pitches[i + 1]

            # Проверяем, является ли текущий элемент экстремумом
            if (current > prev and current > next_) or (current < prev and current < next_):
                extremes_list.append(current)

        extremes_list.append(self.pitches[-1])  # Всегда добавляем последний элемент

        return extremes_list
    
    @property
    def extreme_degrees(self):
        """Возвращает ступени (degrees) точек экстремумов."""

        # Применяем _pitch_to_degree к каждому элементу self.extremes
        return [self._pitch_to_degree(pitch) for pitch in self.extremes]
    
    @property
    def get_segments_until_and_after_leaps(self):
        """Разбивает список интервалов на сегменты от начала до каждого скачка (включительно).
        Затем делает то же для реверсированного списка интервалов.
        """
        until = self._get_segments_until_leaps(self.intervals)
        after = self._get_segments_until_leaps(self.intervals[::-1])
        return until + after

    def _get_segments_until_leaps(self, interval_list):
        """Вспомогательный метод для получения сегментов до скачков в заданном списке.
        Скачок — интервал, модуль которого >= 3 (кварта).
        Если скачков нет, возвращает [].
        """
        leap_indices = [i for i, x in enumerate(interval_list) if abs(x) >= 3]
        return [interval_list[:i+1] for i in leap_indices] if leap_indices else []