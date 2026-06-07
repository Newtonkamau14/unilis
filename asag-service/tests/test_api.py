import requests
import json

BASE = "http://127.0.0.1:8000"

tests = [
    # NETWORKING
    {"label": "NET - SA Correct",   "payload": {"question_context": "Networking Essentials - Network Protocols", "reference_answer": "TCP ensures reliable data transmission by establishing a connection through a three-way handshake, guaranteeing packet delivery and ordering.", "student_answer": "TCP is a connection-oriented protocol that uses a three-way handshake to establish connections and guarantees reliable delivery of packets.", "question_type": "short_answer"}},
    {"label": "NET - SA Partial",   "payload": {"question_context": "Networking Essentials - Network Protocols", "reference_answer": "TCP ensures reliable data transmission by establishing a connection through a three-way handshake, guaranteeing packet delivery and ordering.", "student_answer": "TCP makes sure data is delivered correctly between computers.", "question_type": "short_answer"}},
    {"label": "NET - SA Wrong",     "payload": {"question_context": "Networking Essentials - Network Protocols", "reference_answer": "TCP ensures reliable data transmission by establishing a connection through a three-way handshake, guaranteeing packet delivery and ordering.", "student_answer": "TCP is a fast protocol that sends data without checking if it arrives.", "question_type": "short_answer"}},
    {"label": "NET - MCQ Correct",  "payload": {"question_context": "Which OSI layer routes packets?", "reference_answer": "C", "student_answer": "C", "question_type": "multiple_choice", "mcq_options": ["A. Physical", "B. Data link", "C. Network", "D. Transport"]}},
    {"label": "NET - MCQ Wrong",    "payload": {"question_context": "Which OSI layer routes packets?", "reference_answer": "C", "student_answer": "D", "question_type": "multiple_choice", "mcq_options": ["A. Physical", "B. Data link", "C. Network", "D. Transport"]}},
    # OOP
    {"label": "OOP - SA Correct",   "payload": {"question_context": "Object Oriented Programming - Core Concepts", "reference_answer": "Inheritance is a mechanism where a child class acquires the properties and methods of a parent class, promoting code reuse and establishing an is-a relationship.", "student_answer": "Inheritance allows a subclass to inherit attributes and methods from a parent class, enabling code reuse and representing an is-a relationship.", "question_type": "short_answer"}},
    {"label": "OOP - SA Partial",   "payload": {"question_context": "Object Oriented Programming - Core Concepts", "reference_answer": "Polymorphism allows objects of different classes to be treated as objects of a common superclass, enabling the same method to behave differently based on the object that calls it.", "student_answer": "Polymorphism means one method can do different things.", "question_type": "short_answer"}},
    {"label": "OOP - SA Wrong",     "payload": {"question_context": "Object Oriented Programming - Core Concepts", "reference_answer": "Encapsulation is the bundling of data and methods that operate on that data within a single unit called a class, restricting direct access to some components.", "student_answer": "Encapsulation is when you use loops to repeat code multiple times in a program.", "question_type": "short_answer"}},
    {"label": "OOP - MCQ Correct",  "payload": {"question_context": "Which OOP concept allows same method name with different parameters?", "reference_answer": "B", "student_answer": "B", "question_type": "multiple_choice", "mcq_options": ["A. Inheritance", "B. Method overloading", "C. Encapsulation", "D. Abstraction"]}},
    {"label": "OOP - MCQ Wrong",    "payload": {"question_context": "Which OOP concept allows same method name with different parameters?", "reference_answer": "B", "student_answer": "A", "question_type": "multiple_choice", "mcq_options": ["A. Inheritance", "B. Method overloading", "C. Encapsulation", "D. Abstraction"]}},
    # OS
    {"label": "OS  - SA Correct",   "payload": {"question_context": "Operating Systems - Process Management", "reference_answer": "A deadlock occurs when two or more processes are blocked forever, each waiting for a resource held by the other, satisfying all four Coffman conditions: mutual exclusion, hold and wait, no preemption, and circular wait.", "student_answer": "A deadlock happens when two or more processes are permanently blocked because each is waiting for a resource that the other holds, meeting the conditions of mutual exclusion, hold and wait, no preemption and circular wait.", "question_type": "short_answer"}},
    {"label": "OS  - SA Partial",   "payload": {"question_context": "Operating Systems - Process Management", "reference_answer": "Virtual memory is a memory management technique that gives processes the illusion of having more memory than physically available by using disk space as an extension of RAM through paging or segmentation.", "student_answer": "Virtual memory allows programs to use more memory than the computer physically has by using the hard drive.", "question_type": "short_answer"}},
    {"label": "OS  - SA Wrong",     "payload": {"question_context": "Operating Systems - Process Management", "reference_answer": "A semaphore is a synchronization primitive used to control access to shared resources by multiple processes, using wait and signal operations to prevent race conditions.", "student_answer": "A semaphore is a type of memory storage used to speed up CPU processing in modern computers.", "question_type": "short_answer"}},
    {"label": "OS  - MCQ Correct",  "payload": {"question_context": "Which scheduling algorithm selects shortest burst time?", "reference_answer": "B", "student_answer": "B", "question_type": "multiple_choice", "mcq_options": ["A. FCFS", "B. Shortest Job First", "C. Round Robin", "D. Priority"]}},
    {"label": "OS  - MCQ Wrong",    "payload": {"question_context": "Which scheduling algorithm selects shortest burst time?", "reference_answer": "B", "student_answer": "C", "question_type": "multiple_choice", "mcq_options": ["A. FCFS", "B. Shortest Job First", "C. Round Robin", "D. Priority"]}},
]

print(f"{'Label':<22} {'Type':<14} {'Score':<8} {'Semantic':<10} {'Terminology':<12} Feedback")
print("="*90)

for test in tests:
    r = requests.post(f"{BASE}/grade", json=test["payload"])
    d = r.json()
    sem  = d["semantic_score"]["score"]    if d.get("semantic_score")    else "-"
    term = d["terminology_score"]["score"] if d.get("terminology_score") else "-"
    fb   = d["feedback_report"].split("\n")[0]
    print(f"{test['label']:<22} {d['question_type']:<14} {d['final_weighted_score']:<8} {str(sem):<10} {str(term):<12} {fb}")