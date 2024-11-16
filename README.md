# 🤖Ngram-Similarity-Engine📚

In this project, we will use extracted n-grams to build a database of features for a collection of programs.

---

## Table of Contents 📑
1. [Introduction](#introduction-)
2. [Building the SQLite Database](#building-the-sqlite-database-)
3. [Filtering Frequent N-Grams](#filtering-frequent-n-grams-)
4. [Implemented Features](#implemented-features-)
5. [Similarity Calculation](#similarity-calculation-)
6. [Analysis and Conclusions](#analysis-and-conclusions-)

---

## Introduction 📘

In this project, we will create and analyze SQLite databases that store n-grams extracted from student files. The goal is to apply methods for storage, filtering, and similarity analysis to detect patterns and relationships between programs.

---

## Building the SQLite Database 🛠️

1. **SQLite Database `raw.db`**  
   Contains a `Homeworks` table with the following structure:  
   - `Hash` - the file hash (MD5, SHA-1, or SHA-256)  
   - `Assign` - the assignment number  
   - `Student` - the student's identifier  
   - `Ngrams` - a blob containing a sorted list of extracted n-grams. Each n-gram is represented as an unsigned 32-bit integer.  

---

## Filtering Frequent N-Grams 🗂️

2. **SQLite Database `features.db`**  
   Based on `raw.db`, this database is built with the same structure but excludes n-grams that appear in more than `T` files (where `T = 30` is suggested).  

---

## Implemented Features 🧩

3. **Functions**:  
   - `sim1(db, h1, h2)`  
     Calculates the Jaccard similarity based on two provided hashes.  
   - `sim2(db, assign, s1, s2)`  
     Calculates the Jaccard similarity based on an assignment number and two student identifiers.  
     - Returns `0` if one of the students does not exist in the database.  

---

## Similarity Calculation 📊

4. **For each assignment**:  
   - Calculate the similarity between all pairs of submissions.  
   - Create a top-500 list of the most similar pairs for each of the two databases (`raw.db` and `features.db`).  

5. **Analyze source code**:  
   - Select 10 pairs of code from each top list for further analysis.  

---

## Analysis and Conclusions 🔍

- The analysis of similar pairs provides insights into potential common patterns or plagiarism among students.  
- Using n-grams and the optimized database (`features.db`) helps reduce noise caused by frequently used elements.  

---

### Instructions for Use 💾
1. Build the `raw.db` database using the initial collection of files.  
2. Apply filtering to create the `features.db` database.  
3. Implement the `sim1` and `sim2` functions.  
4. Calculate and analyze similarities according to the requirements.
