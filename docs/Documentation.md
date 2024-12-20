# Project Instructions🧪

## Table of Contents📑
1. [Build Raw Database](#build-raw-database)
2. [Filter Raw Database](#filter-raw-database)
3. [Jaccard Similarity Functions](#jaccard-similarity-functions)
4. [Pairwise Similarity Analysis](#pairwise-similarity-analysis)

---

## Build Raw Database📂

### Problem  
Construct an SQLite database `features_raw.db` containing a table `Homeworks` with the following columns:
- **Hash**: File hash (MD5, SHA-1, or SHA-256)
- **Assign**: Assignment number
- **Student**: Student identifier
- **Ngrams**: A blob containing a sorted list of extracted n-grams from the file. Each n-gram is represented as an unsigned 32-bit integer.

### Solution: Function `build_raw_database`
1. Accepts the path to a folder and the path to the raw database as parameters.
2. Establishes a connection to the specified SQLite database.
3. Initializes a cursor to execute database queries.
4. Creates a table named `Homeworks` with columns: `Hash`, `Assign`, `Student`, and `Ngrams` (if it doesn’t already exist).
5. Iterates through the files in the folder and extracts raw n-grams from executable files.
6. Calculates the hash of the n-grams for each executable file and stores them alongside the assignment name and student name in the raw database.

### Result  
The number of entries in the database equals the number of files in the target folder, equal to 946.

<p align="center">
  <img src="example1.png" alt="Database" width="500">
  <br>
  <em>Ex1: Database</em>
</p>

---

## Filter Raw Database🗑️

### Problem  
Based on the collection from the previous exercise, construct a new SQLite database `features.db` with the same structure. Remove n-grams that appear in more than **T = 30** files.

### Solution: Function `filter_and_build_database`
1. Accepts the paths to the raw and filtered databases as parameters.
2. Creates connections to both databases.
3. Initializes cursors for executing queries in both databases.
4. Creates a table `Homeworks` in the filtered database with the same structure as the raw database.
5. Selects raw data from the raw database.
6. Filters out n-grams exceeding the threshold of 30 occurrences and stores the remaining data in the filtered database.

### Result  
After verification:
- The sequence `"mov", "add", "mov", "mov", "mov"` is removed as it appears in more than 30 files for the same assignment.

<p align="center">
  <img src="example2.1.png" alt="something" width="500">
  <br>
  <em>Ex2: "mov", "add", "mov", "mov", "mov"</em>
</p>

- Sequences like `"mov", "call", "movabs", "hlt", "push"` remain unchanged as they occur less frequently.

<p align="center">
  <img src="example2.2.png" alt="something" width="500">
  <br>
  <em>Ex2: "mov", "call", "movabs", "hlt", "push"</em>
</p>

---

## Jaccard Similarity Functions🧮

### Problem  
Implement two functions for calculating Jaccard similarity:
1. `sim1(db, h1, h2)`: Calculates Jaccard similarity based on two hash values.
2. `sim2(db, assign, s1, s2)`: Calculates Jaccard similarity based on an assignment number and two student identifiers. Returns 0 if either student doesn’t exist in the database.

### Solution  
#### Function `sim1`
1. Accepts the path to the SQLite database and two hashes as parameters.
2. Connects to the database and retrieves n-grams for each hash.
3. Calculates Jaccard similarity between the two sets of n-grams.
4. Returns the calculated similarity.

#### Function `sim2`
1. Accepts the database path, assignment number, and two student identifiers.
2. Retrieves n-grams corresponding to the assignment and each student.
3. Calculates and returns the Jaccard similarity between the two sets of n-grams.

### Jaccard Similarity Formula
The Jaccard similarity is calculated as the size of the intersection of two sets divided by the size of the union of the two sets.

For sets \( A \) and \( B \), the Jaccard similarity \( J(A, B) \) is given by:

$$
J(A, B) = \frac{|A \cap B|}{|A \cup B|}
$$

Where:
- \( |A \cap B| \) is the number of common elements in both sets.
- \( |A \cup B| \) is the total number of unique elements across both sets.

### Results  
- For assignment 1, students 37 and 47 (identical): Jaccard similarity = **1.0**.

<p align="center">
  <img src="example3.png" alt="something" width="500">
  <br>
  <em>Ex3: Function sim1</em>
  <br>
  <br>
  <img src="example3.1.png" alt="something" width="500">
  <br>
  <em>Ex3: Function sim2</em>
</p>

- For different entries: Similarity is small.

<p align="center">
  <img src="example3.2.png" alt="something" width="500">
  <br>
  <em>Ex3: Function sim1</em>
  <br>
  <br>
  <img src="example3.3.png" alt="something" width="500">
  <br>
  <em>Ex3: Function sim2</em>
</p>

- Non-existent database entries: Similarity = **0**.

<p align="center">
  <img src="example3.4.png" alt="something" width="500">
  <br>
  <em>Ex3: Function sim1</em>
  <br>
  <br>
  <img src="example3.5.png" alt="something" width="500">
  <br>
  <em>Ex3: Function sim2</em>
</p>

---

## Pairwise Similarity Analysis🔍

### Problem  
For each assignment, calculate Jaccard similarity between all pairs of submissions. Generate a top 500 most similar pairs for each of the two databases. Analyze the source code for 10 pairs from each top list.

### Solution: Function `calculate_all_similarity`
1. Accepts the database path as a parameter.
2. For each assignment:
   - Select all students who submitted assignments.
   - Compute Jaccard similarity between all pairs of submissions.
3. Store results in a list of tuples: `(assignment, student1, student2, similarity)`.
4. Sort the list in descending order by similarity.
5. Return the top 500 pairs.

### Jaccard Similarity Formula
For each pair of submissions \( (s1, s2) \), calculate Jaccard similarity using the formula:

$$
J(A_{s1}, A_{s2}) = \frac{|A_{s1} \cap A_{s2}|}{|A_{s1} \cup A_{s2}|}
$$

Where:
- \( A_{s1} \) is the set of n-grams for student 1.
- \( A_{s2} \) is the set of n-grams for student 2.
- \( A_{s1} \cap A_{s2} \) is the intersection of n-grams from both students.
- \( A_{s1} \cup A_{s2} \) is the union of n-grams from both students.

You can then store these similarities and sort them in descending order to find the top 500 most similar pairs.

### Result  
Top 500 similarities are written to two separate `.txt` files for raw and filtered data.  

<p align="center">
  <img src="example4.png" alt="something" width="500">
  <br>
  <em>Ex4: Raw VS Filtered Data</em>
</p>

#### Example Analysis:
1. **Assignment a01, Students s0037 & s0047, Similarity = 1.0**:
   - **Total Commander** and a comparison tool confirm that differences are limited to comments.

<p align="center">
  <img src="example4.1.png" alt="something" width="500">
  <br>
  <em>Ex4: Total Commander</em>
  <br>
  <br>
  <img src="example4.2.png" alt="something" width="200">
  <br>
  <em>Ex4: Comparison Tool</em>
</p>

2. **Assignment a02, Students s0060 & s0147, Similarity = 1.0**:
   - Confirmed identical code.

<p align="center">
  <img src="example4.3.png" alt="something" width="500">
  <br>
  <em>Ex4: Total Commander</em>
  <br>
  <br>
  <img src="example4.4.png" alt="something" width="200">
  <br>
  <em>Ex4: Comparison Tool</em>
</p>

### Graph Analysis
1. **Threshold 50%**: Broad distribution includes many false positives.

<p align="center">
  <img src="example5.png" alt="something" width="500">
  <br>
  <em>Threshold 50%</em>
</p>


2. **Threshold 80%**: Concentrated distribution, optimal sensitivity/specificity trade-off.

<p align="center">
  <img src="example5.1.png" alt="something" width="500">
  <br>
  <em>Threshold 80%</em>
</p>

3. **Threshold 90%**: Misses genuine plagiarism cases.

<p align="center">
  <img src="example5.2.png" alt="something" width="500">
  <br>
  <em>Threshold 90%</em>
</p>

#### Conclusion
Threshold **80%** provides the best compromise between sensitivity and specificity.

---
