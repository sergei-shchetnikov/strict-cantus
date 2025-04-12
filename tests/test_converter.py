import unittest, os
from converter import melody_to_intervals, taneyev_intervals_to_pitches, intervals_to_melody, find_local_extrema  # Импортируем тестируемую функцию
from music21 import stream, note, converter, key, tempo

class TestMelodyToIntervals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Настраиваем путь к тестовым данным перед запуском всех тестов."""
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def setUp(self):
        """Создаём тестовые мелодии."""
        self.scale = stream.Stream([
            note.Note("C4"), note.Note("D4"), note.Note("E4"), note.Note("F4")
        ])  # До-ре-ми-фа (интервалы: 1, 1, 1)

        self.jumps = stream.Stream([
            note.Note("C4"), note.Note("G4"), note.Note("E4"), note.Note("C4")
        ])  # Квинта вверх, терция вниз, терция вниз (интервалы: 4, -2, -2)

        self.repeated_notes = stream.Stream([
            note.Note("C4"), note.Note("C4"), note.Note("D4"), note.Note("C4")
        ])  # Унисон, секунда вверх, секунда вниз (интервалы: 0, 1, -1)

        # Загружаем тестовый файл MusicXML из папки data
        test_file = os.path.join(self.test_data_dir, "test_cantus.musicxml")
        self.cantus_file = converter.parse(test_file)

    def test_scale(self):
        self.assertEqual(melody_to_intervals(self.scale), [1, 1, 1])

    def test_jumps(self):
        self.assertEqual(melody_to_intervals(self.jumps), [4, -2, -2])

    def test_repeated_notes(self):
        self.assertEqual(melody_to_intervals(self.repeated_notes), [0, 1, -1])

    def test_cantus_file(self):
        """Тестирование интервалов из файла MusicXML."""
        self.assertEqual(
            melody_to_intervals(self.cantus_file), 
            [1, 2, -1, 3, -1, -1, -2, 1, -1, -1]
        )

class TestTaneyevIntervalsToPitches(unittest.TestCase):
    def test_simple_intervals(self):
        """Тест с простыми последовательными интервалами"""
        self.assertEqual(taneyev_intervals_to_pitches([1, 1, 1, 1]), [0, 1, 2, 3, 4])

    def test_mixed_intervals(self):
        """Тест со смешанными интервалами"""
        self.assertEqual(taneyev_intervals_to_pitches([1, 2, -1, 3, -1, -1, -2, 1, -1, -1]), [0, 1, 3, 2, 5, 4, 3, 1, 2, 1, 0])

    def test_all_zero(self):
        """Тест с нулевыми интервалами (мелодия на одной высоте)"""
        self.assertEqual(taneyev_intervals_to_pitches([0, 0, 0]), [0, 0, 0, 0])

    def test_negative_intervals(self):
        """Тест с интервалами, только уменьшающими высоту"""
        self.assertEqual(taneyev_intervals_to_pitches([-1, -2, -3]), [0, -1, -3, -6])

    def test_single_note(self):
        """Тест с одним интервалом"""
        self.assertEqual(taneyev_intervals_to_pitches([5]), [0, 5])

    def test_empty_list(self):
        """Тест с пустым списком"""
        self.assertEqual(taneyev_intervals_to_pitches([]), [])

class TestIntervalsToMelody(unittest.TestCase):
    def test_melody_structure(self):
        """Проверяем, что в полученной мелодии есть тональность, темп и ноты"""
        intervals = [2, -1, 3]  # Пример списка интервалов
        key_str = "C"  # До мажор
        scale_degree = 1  # Первая ступень (C)

        melody = intervals_to_melody(intervals, key_str, scale_degree)

        # Проверяем, что это Stream
        self.assertIsInstance(melody, stream.Stream)

        # Проверяем, что второй элемент — это объект MetronomeMark (темп)
        self.assertIsInstance(melody[0], tempo.MetronomeMark)
        self.assertEqual(melody[0].number, 140)  # Темп 140 половинными

        # Проверяем, что первый элемент — это объект Key (тональность)
        self.assertIsInstance(melody[1], key.Key)
        self.assertEqual(melody[1].tonic.name, "C")
        self.assertEqual(melody[1].mode, "major")        

        # Проверяем, что остальные элементы — это ноты
        notes = [n for n in melody if isinstance(n, note.Note)]
        self.assertEqual(len(notes), len(intervals) + 1)  # Должно быть на 1 ноту больше, чем интервалов

    def test_correct_pitches(self):
        """Проверяем, что интервалы правильно применены и питчи корректны"""
        intervals = [2, -1, 3]  # Мелодия по интервалам
        key_str = "C"  # До мажор
        scale_degree = 1  # Начинаем с первой ступени (C)

        melody = intervals_to_melody(intervals, key_str, scale_degree)
        
        # Ожидаемые ноты: C4 → E4 → D4 → G4
        expected_pitches = ["C4", "E4", "D4", "G4"]

        notes = [n for n in melody if isinstance(n, note.Note)]
        actual_pitches = [n.nameWithOctave for n in notes]

        self.assertEqual(actual_pitches, expected_pitches)

class TestFindLocalExtrema(unittest.TestCase):
    def test_single_maximum(self):
        self.assertEqual(find_local_extrema([0, 1, 2, 3, 4, 5, 0]), [0, 5, 0])

    def test_multiple_extrema(self):
        self.assertEqual(find_local_extrema([0, 1, 3, 7, -1, 5, 3, 2, 4, 0]), [0, 7, -1, 5, 2, 4, 0])

    def test_single_maximum_and_minimum(self):
        self.assertEqual(find_local_extrema([0, 5, 4, 3, 2, 1, 0]), [0, 5, 0])

    def test_single_extremum(self):
        self.assertEqual(find_local_extrema([0, -2, 0]), [0, -2, 0])    

if __name__ == '__main__':
    unittest.main()
