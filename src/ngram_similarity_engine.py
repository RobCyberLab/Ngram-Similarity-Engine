import os
import hashlib
import sqlite3
import pefile
import capstone
import json
import matplotlib.pyplot as plt

NGR_SIZE = 5  # Dimensiunea n-gramului
T = 30  # Numărul maxim de asignări pentru n-gramă

# Funcția pentru filtrarea anumitor mnemonici pe baza unor reguli
def check(mnemonic):
    # if mnemonic in ["nop", "int3", "hlt", "wait"]:
    #     return None
    # elif mnemonic in ["sub", "dec", "inc", "sbb", "adc", "neg"]:
    #     return "add"
    # elif mnemonic in ["imul", "div", "idiv"]:
    #     return "mul"
    # else:
        return mnemonic

# Funcția pentru extragerea n-gramurilor dintr-un fișier executabil
def extract_ngrams(file_path):
    pe = pefile.PE(file_path)  # Parse the PE file using pefile library
    nd = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)  # Initialize Capstone disassembler
    ngrams = set()  # Set to store unique n-grams extracted from the executable

    # Iterate through each section of the PE file
    for sect in pe.sections:
        # Check if the section is executable (marked by the IMAGE_SCN_MEM_EXECUTE flag)
        if (sect.Characteristics & 0x20) != 0:
            opcodes = []  # List to store opcode mnemonics for the current section
            # Disassemble the instructions in the section using Capstone
            for instr in nd.disasm(sect.get_data(), sect.VirtualAddress):
                opcode = check(instr.mnemonic)  # Filter the mnemonic instruction using the check function
                if opcode is not None:
                    opcodes.append(opcode)  # Append the filtered opcode to the list
                    if len(opcodes) >= NGR_SIZE:  # Check if enough opcodes are collected to form an n-gram
                        ngrams.add(tuple(opcodes[-NGR_SIZE:]))  # Add the n-gram to the set
    return json.dumps(list(ngrams))  # Serialize n-grams to JSON format and return

# Funcția pentru calcularea hash-ului unui șir de caractere
# Funcția pentru calcularea hash-ului unui șir de caractere
def calculate_hash(data, algorithm='md5'):
    # Se alege algoritmul de hash în funcție de argumentul algorithm
    hasher = hashlib.md5() if algorithm == 'md5' else hashlib.sha1() if algorithm == 'sha1' else hashlib.sha256()
    # Se actualizează hash-ul cu șirul de caractere encodat în UTF-8
    hasher.update(data.encode('utf-8'))
    # Se returnează reprezentarea hexazecimală a hash-ului calculat
    return hasher.hexdigest()

# Ex1 ----------------------------------------------------------------

# Funcția pentru construirea bazei de date cu n-gramuri brute
def build_raw_database(folder_path, database_path):
    # Conectarea la baza de date
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    # Crearea tabelului Homeworks dacă nu există deja
    c.execute('''CREATE TABLE IF NOT EXISTS Homeworks
    (Hash TEXT, Assign TEXT, Student TEXT, Ngrams BLOB)''')

    # Iterarea prin fișierele din folder și adăugarea datelor în baza de date
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Verificarea dacă fișierul este un fișier executabil sau un fișier sursă C++
            if file.endswith('.exe') or file.endswith('.cpp'):
                # Extrage n-gramurile din fișierul specificat
                ngrams = extract_ngrams(file_path)
                # Calculează hash-ul pentru n-gramurile extrase
                hash_value = calculate_hash(ngrams)
                # Extrage numele asignării și numele studentului din numele fișierului
                assign, student = file.split('_')[:2]
                # Elimină extensia fișierului pentru a obține numele studentului
                student = os.path.splitext(student)[0]
                # Inserează datele în baza de date
                c.execute("INSERT INTO Homeworks VALUES (?, ?, ?, ?)", (hash_value, assign, student, ngrams))

    # Confirmă și închide conexiunea la baza de date
    conn.commit()
    conn.close()

# Ex2 ----------------------------------------------------------------

# Funcția pentru filtrarea și construirea bazei de date filtrate
def filter_and_build_database(raw_database_path, filtered_database_path):
    # Conectarea la baza de date brută și filtrată
    conn_raw = sqlite3.connect(raw_database_path)  # Conexiune la baza de date brută
    conn_filtered = sqlite3.connect(filtered_database_path)  # Conexiune la baza de date filtrată

    # Inițializarea cursorilor pentru bazele de date
    c_raw = conn_raw.cursor()  # Cursor pentru baza de date brută
    c_filtered = conn_filtered.cursor()  # Cursor pentru baza de date filtrată

    # Crearea tabelului în baza de date filtrată, dacă nu există deja
    c_filtered.execute('''CREATE TABLE IF NOT EXISTS Homeworks
        (Hash TEXT, Assign TEXT, Student TEXT, Ngrams BLOB)''')

    # Selecție și filtrare a datelor din baza de date brută
    c_raw.execute("SELECT Assign, Student, Ngrams FROM Homeworks")  # Selecție a datelor din baza de date brută
    rows = c_raw.fetchall()  # Fetchăm toate rândurile selectate
    filtered_ngrams = {}  # Dicționar pentru a ține evidența numărului de apariții ale n-gramelor

    # Calcularea numărului de apariții pentru fiecare n-gramă în fiecare asignare pentru fiecare student
    for assign, student, ngrams_json in rows:
        ngrams = json.loads(ngrams_json)  # Parsarea n-gramele din format JSON
        for ngram in ngrams:
            ngram_key = (assign, tuple(ngram))
            filtered_ngrams[ngram_key] = filtered_ngrams.get(ngram_key, 0) + 1

    # Filtrarea n-gramele și inserarea în baza de date filtrată
    for assign, student, ngrams_json in rows:
        ngrams = json.loads(ngrams_json)  # Parsarea n-gramele din format JSON
        # Filtrarea n-gramele pentru asignare, astfel încât să nu depășească numărul maxim T de apariții
        filtered_ngrams_for_assignment = [ngram for ngram in ngrams if filtered_ngrams[(assign, tuple(ngram))] <= T]
        # Inserarea datelor filtrate în baza de date filtrată, împreună cu hash-ul recalculat pentru n-gramele filtrate
        c_filtered.execute("INSERT INTO Homeworks (Hash, Assign, Student, Ngrams) VALUES (?, ?, ?, ?)",
                           (calculate_hash(json.dumps(filtered_ngrams_for_assignment)), assign, student, json.dumps(filtered_ngrams_for_assignment)))

    # Confirmarea schimbărilor și închiderea conexiunilor la baza de date
    conn_filtered.commit()  # Salvarea modificărilor în baza de date filtrată
    conn_raw.close()  # Închiderea conexiunii la baza de date brută
    conn_filtered.close()  # Închiderea conexiunii la baza de date filtrată

folder_path = r'D:\facult\a_master\an1_sem2\sdmsc\laborator\l5\homeworks\homeworks\binaries'
raw_database_path = 'features_raw.db'
filtered_database_path = 'features.db'

# Verifica dacă baza de date brută există deja
if not os.path.exists(raw_database_path):
    # Creează baza de date brută dacă nu există
    build_raw_database(folder_path, raw_database_path)
    print("Baza de date brută a fost creata.")
else:
    print("Baza de date brută există deja. Nu se va crea alta.")

# Verifica dacă baza de date filtrată există deja
if not os.path.exists(filtered_database_path):
    # Creează baza de date filtrată dacă nu există
    filter_and_build_database(raw_database_path, filtered_database_path)
    print("Baza de date filtrată a fost creata.")
else:
    print("Baza de date filtrată există deja. Nu se va crea alta.")

# Ex4 ----------------------------------------------------------------

# Funcția pentru calcularea similarității Jaccard între toate perechile de teme pentru fiecare asignare
def calculate_all_similarity(db):
    conn = sqlite3.connect(db)  # Conectare la baza de date
    c = conn.cursor()  # Inițializare cursor pentru interogare

    # Interogare pentru a obține toate asignările distincte
    c.execute("SELECT DISTINCT Assign FROM Homeworks")
    assignments = c.fetchall()  # Se obțin toate asignările

    top_similar_pairs = []  # Lista pentru a ține cele mai similare perechi

    # Pentru fiecare asignare
    for assign in assignments:
        assign = assign[0]  # Extragem numele asignării
        # Interogare pentru a obține toți studenții care au lucrări pentru această asignare
        c.execute("SELECT DISTINCT Student FROM Homeworks WHERE Assign = ?", (assign,))
        students = c.fetchall()  # Se obțin toți studenții pentru asignare
        students = [s[0] for s in students]  # Extragem numele studenților

        # Pentru fiecare pereche de studenți
        for i in range(len(students)):
            for j in range(i + 1, len(students)):
                s1 = students[i]  # Numele primului student din pereche
                s2 = students[j]  # Numele celui de-al doilea student din pereche

                # Interogare pentru a obține n-gramele pentru primul student
                c.execute("SELECT Ngrams FROM Homeworks WHERE Assign = ? AND Student = ?", (assign, s1))
                result_s1 = c.fetchone()
                # Interogare pentru a obține n-gramele pentru al doilea student
                c.execute("SELECT Ngrams FROM Homeworks WHERE Assign = ? AND Student = ?", (assign, s2))
                result_s2 = c.fetchone()

                # Verificare dacă există date pentru ambele n-grame
                if result_s1 is not None and result_s2 is not None:
                    # Parsare și convertirea n-gramelor din format JSON pentru primul student
                    ngrams_s1 = [tuple(gram) for gram in json.loads(result_s1[0])]
                    # Parsare și convertirea n-gramelor din format JSON pentru al doilea student
                    ngrams_s2 = [tuple(gram) for gram in json.loads(result_s2[0])]

                    # Calcularea similarității Jaccard între cei doi studenți
                    intersection = len(set(ngrams_s1) & set(ngrams_s2))
                    union = len(set(ngrams_s1) | set(ngrams_s2))
                    jaccard_similarity = intersection / union if union != 0 else 0

                    # Adăugarea perechii și similarității sale în lista top_similar_pairs
                    top_similar_pairs.append((assign, s1, s2, jaccard_similarity))

    # Sortarea listei în funcție de similaritatea Jaccard în ordine descrescătoare
    top_similar_pairs.sort(key=lambda x: x[3], reverse=True)
    # Returnarea primelor 500 de perechi
    return top_similar_pairs[:500]


# Scrierea rezultatelor într-un fișier text
def write_results_to_file(results, file_path):
    with open(file_path, 'w') as file:
        for i, pair in enumerate(results, 1):
            file.write(f"{i}. Assignment: {pair[0]}, Student 1: {pair[1]}, Student 2: {pair[2]}, Similaritate: {pair[3]}\n")


# Scrierea rezultatelor pentru baza de date filtrată într-un fișier text
filtered_file_path = 'top_similar_pairs_filtered.txt'
if not os.path.exists(filtered_file_path):
    top_similar_pairs_filtered = calculate_all_similarity(filtered_database_path)
    write_results_to_file(top_similar_pairs_filtered, filtered_file_path)
    print("Fișierul pentru rezultatele filtrate există a fost creat.")
else:
    print("Fișierul pentru rezultatele filtrate există deja. Nu se va crea altul.")

# Scrierea rezultatelor pentru baza de date brută într-un fișier text
raw_file_path = 'top_similar_pairs_raw.txt'
if not os.path.exists(raw_file_path):
    top_similar_pairs_raw = calculate_all_similarity(raw_database_path)
    write_results_to_file(top_similar_pairs_raw, raw_file_path)
    print("Fișierul pentru rezultatele brute a fost creat.")
else:
    print("Fișierul pentru rezultatele brute există deja. Nu se va crea altul.")

# Analiza ----------------------------------------------------------------

# Funcția pentru a calcula procentajul de similaritate pentru perechile cu o similaritate de peste un anumit prag
# def calculate_similarity_percentage_above_threshold(top_similar_pairs, threshold):
#     similarity_percentage = {}  # Dicționar pentru a stoca procentajul de similaritate pentru fiecare asignare
#     assignment_counts = {}  # Dicționar pentru a număra câte perechi de studenți sunt în fiecare asignare
#
#     # Pentru fiecare pereche similară cu o similaritate mai mare decât pragul
#     for assign, _, _, similarity in top_similar_pairs:
#         if similarity >= threshold:
#             if assign not in similarity_percentage:
#                 similarity_percentage[assign] = []
#                 assignment_counts[assign] = 0
#             similarity_percentage[assign].append(similarity)
#             assignment_counts[assign] += 1
#
#     return similarity_percentage, assignment_counts

# # Pragul de similaritate
# threshold = 0.9
#
# top_similar_pairs_filtered = calculate_all_similarity(filtered_database_path)
# top_similar_pairs_raw = calculate_all_similarity(raw_database_path)
#
# # Calcularea procentajului de similaritate pentru baza de date filtrată peste pragul specificat
# similarity_percentage_above_threshold_filtered, assignment_counts_filtered = calculate_similarity_percentage_above_threshold(top_similar_pairs_filtered, threshold)
#
# # Calcularea procentajului de similaritate pentru baza de date brută peste pragul specificat
# similarity_percentage_above_threshold_raw, assignment_counts_raw = calculate_similarity_percentage_above_threshold(top_similar_pairs_raw, threshold)
#
# # Crearea unui subplot cu două axe pentru a afișa ambele grafice
# fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
#
# # Graficul pentru baza de date filtrată
# for assign, similarities in similarity_percentage_above_threshold_filtered.items():
#     ax1.plot(sorted(similarities), range(1, len(similarities) + 1), marker='', linestyle='-', label=assign, linewidth=2, markeredgewidth=2, markersize=8)
#
# ax1.set_xlabel('Procentaj de plagiat')
# ax1.set_ylabel('Număr de studenți')
# ax1.set_title(f'Distribuția numărului de studenți & procentajul de plagiat (Baza de date filtrată)')
# ax1.legend()
# ax1.grid(True)  # Adăugarea gridului
#
# # Graficul pentru baza de date brută
# for assign, similarities in similarity_percentage_above_threshold_raw.items():
#     ax2.plot(sorted(similarities), range(1, len(similarities) + 1), marker='', linestyle='-', label=assign, linewidth=2, markeredgewidth=2, markersize=8)
#
# ax2.set_xlabel('Procentaj de plagiat')
# ax2.set_ylabel('Număr de studenți')
# ax2.set_title(f'Distribuția numărului de studenți & procentajul de plagiat (Baza de date brută)')
# ax2.legend()
# ax2.grid(True)  # Adăugarea gridului
#
# plt.tight_layout()
# plt.show()

# Ex3 ----------------------------------------------------------------

# Funcția pentru calcularea similarității Jaccard pe baza unui număr de asignări și identificatori de studenți
def sim2(db):
    assign = input("Introduceți numele asignării: ")
    s1 = input("Introduceți primul identificator de student: ")
    s2 = input("Introduceți al doilea identificator de student: ")

    conn = sqlite3.connect(db)  # Conectare la baza de date
    c = conn.cursor()  # Inițializare cursor pentru interogare

    # Interogarea bazei de date pentru a obține n-gramele corespunzătoare asignării și primului identificator de student
    c.execute("SELECT Ngrams FROM Homeworks WHERE Assign = ? AND Student = ?", (assign, s1))
    result_s1 = c.fetchone()  # Se obține primul rezultat

    # Interogarea bazei de date pentru a obține n-gramele corespunzătoare asignării și celui de-al doilea identificator de student
    c.execute("SELECT Ngrams FROM Homeworks WHERE Assign = ? AND Student = ?", (assign, s2))
    result_s2 = c.fetchone()  # Se obține al doilea rezultat

    # Verificarea dacă s-au găsit date pentru ambele identificatoare de student
    if result_s1 is not None and result_s2 is not None:
        # Parsarea și convertirea n-gramelor din format JSON pentru primul student
        ngrams_s1 = [tuple(gram) for gram in json.loads(result_s1[0])]
        # Parsarea și convertirea n-gramelor din format JSON pentru al doilea student
        ngrams_s2 = [tuple(gram) for gram in json.loads(result_s2[0])]

        # Calcularea similarității Jaccard
        intersection = len(set(ngrams_s1) & set(ngrams_s2))
        union = len(set(ngrams_s1) | set(ngrams_s2))
        jaccard_similarity = intersection / union if union != 0 else 0

        return jaccard_similarity  # Se returnează similaritatea Jaccard calculată
    else:
        return 0  # Se returnează 0 dacă unul dintre identificatorii de student nu există în baza de date

# Funcția pentru calcularea similarității Jaccard pe baza a două hash-uri primite
def sim1(db):
    h1 = input("Introduceți primul hash: ")
    h2 = input("Introduceți al doilea hash: ")

    while True:
        conn = sqlite3.connect(db)  # Conectare la baza de date
        c = conn.cursor()  # Inițializare cursor pentru interogare

        # Interogarea bazei de date pentru a obține n-gramele corespunzătoare hash-urilor primite
        c.execute("SELECT Ngrams FROM Homeworks WHERE Hash = ? OR Hash = ?", (h1, h2))
        results = c.fetchall()  # Se obțin toate rândurile care corespund interogării

        # Verificarea dacă s-au găsit date pentru ambele hash-uri
        if len(results) == 2:
            # Parsarea și convertirea n-gramelor din format JSON
            ngrams1 = [tuple(gram) for gram in json.loads(results[0][0])]
            ngrams2 = [tuple(gram) for gram in json.loads(results[1][0])]

            # Calcularea similarității Jaccard
            intersection = len(set(ngrams1) & set(ngrams2))
            union = len(set(ngrams1) | set(ngrams2))
            jaccard_similarity = intersection / union if union != 0 else 0

            return jaccard_similarity  # Se returnează similaritatea Jaccard calculată
        else:
            return 0

# Solicitarea utilizatorului pentru alegerea funcției sau pentru a ieși din program
while True:
    choice = input("Alegeți funcția pentru calcularea similarității Jaccard (sim1/sim2) sau scrieți 'exit' pentru a încheia programul: ").lower()
    if choice == 'sim1':
        similarity_hash = sim1(filtered_database_path)
        print("Similaritatea Jaccard între hash-uri:", similarity_hash)
    elif choice == 'sim2':
        similarity_assign = sim2(filtered_database_path)
        print("Similaritatea Jaccard pentru asignarea dată între cei doi studenți:", similarity_assign)
    elif choice == 'exit':
        print("Programul a fost încheiat.")
        break
    else:
        print("Opțiune invalidă! Vă rugăm să alegeți din nou.")