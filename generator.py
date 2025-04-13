import sqlite3
from itertools import combinations_with_replacement, permutations
from multiprocessing import Pool
from functools import lru_cache
from converter import intervals_to_melody
from music21 import stream, meter, tempo, note, bar, clef
from general_rules import is_valid_melody
from cantus import Cantus

# Настраиваемые параметры
MELODY_LENGTH = 8  # длина мелодии
STEP_COUNT_THRESHOLD = 4  # минимальное количество поступенных ходов (1 и -1)
DB_PATH = f"melodies_{MELODY_LENGTH}_{STEP_COUNT_THRESHOLD}.db"  # путь к файлу базы данных

def generate_combinations():
    elements = frozenset([-7, -4, -3, -2, -1, 1, 2, 3, 4, 5, 7])
    valid_combos = set()
    
    # Предварительная фильтрация для уменьшения числа комбинаций
    for combo in combinations_with_replacement(elements, MELODY_LENGTH - 1):
        if sum(combo) == 0 and combo.count(1) + combo.count(-1) >= STEP_COUNT_THRESHOLD:
            valid_combos.add(tuple(combo))
            
    return valid_combos

def filter_combinations(combinations):
    # Функция теперь не нужна, фильтрация происходит в generate_combinations
    return combinations

@lru_cache(maxsize=1024)
def check_ending_steps(perm):
    return perm[-1] in {1, -1} and perm[-2] in {1, -1}

def process_combo(combo):
    local_valid = set()
    for perm in set(permutations(combo)):
        if check_ending_steps(perm):
            local_valid.add(perm)
    return local_valid

def process_perm(taneyev_intervals):
    cantus = Cantus(list(taneyev_intervals))
    if is_valid_melody(cantus):
        return cantus.intervals
    return None

def generate_valid_permutations(combinations):
    valid_permutations = set()
    
    # Параллельная обработка комбинаций
    with Pool() as pool:
        results = pool.map(process_combo, combinations)
    
    for result in results:
        valid_permutations.update(result)
    
    return list(valid_permutations)

def generate_valid_melodies(permutations):
    # Параллельная проверка мелодий
    with Pool() as pool:
        melodies = pool.map(process_perm, permutations)
    
    return [m for m in melodies if m is not None]

def generate_full_score(valid_melodies):
    full_score = stream.Stream()
    full_score.append(meter.TimeSignature(f"{MELODY_LENGTH}/1"))
    
    tempo_mark = tempo.MetronomeMark(number=140)
    tempo_mark.referent = note.Note(type="half")
    full_score.append(tempo_mark)

    for intervals in valid_melodies:
        melody = intervals_to_melody(intervals, "C", 1)
        full_score.append(melody)

    full_score.makeMeasures(inPlace=True)

    previous_clef = None  # здесь будем хранить предыдущий "bestClef"

    for m in full_score.getElementsByClass('Measure'):
        m.rightBarline = bar.Barline('final')

        best = clef.bestClef(m)
        if best is not None:
            # Только если clef отличается от предыдущего
            if previous_clef is None or best.sign != previous_clef.sign or best.line != previous_clef.line:
                m.insert(0.0, best)
                previous_clef = best

    full_score.show()

def save_melodies_to_db(melodies, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS melodies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intervals TEXT
        )
    """)
    
    for melody in melodies:
        interval_str = ",".join(map(str, melody))
        cursor.execute("INSERT INTO melodies (intervals) VALUES (?)", (interval_str,))
    
    conn.commit()
    conn.close()
    print(f"{len(melodies)} мелодий сохранено в базу данных '{db_path}'.")

def main():
    combinations = generate_combinations()
    filtered_combinations = filter_combinations(combinations)
    valid_permutations = generate_valid_permutations(filtered_combinations)
    valid_melodies = generate_valid_melodies(valid_permutations)

    print(f"Сгенерировано {len(valid_melodies)} валидных мелодий.")
    # generate_full_score(valid_melodies)
    # save_melodies_to_db(valid_melodies)
    print("Генерация завершена.")

if __name__ == "__main__":
    main()
