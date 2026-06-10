-- ============================================================
-- CAT 1 - Networking Essentials Sample Test
-- Mixed: Short Answer + MCQ | Time Limit: 45 minutes
-- ============================================================

USE asag_db;

-- ============================================================
-- INSERT TEST
-- ============================================================
INSERT INTO tests (subject_id, title, description, time_limit, is_active, created_by)
VALUES (
    (SELECT id FROM subjects WHERE code = 'NET101'),
    'CAT 1',
    'Continuous Assessment Test 1 covering TCP/IP, OSI Model, Network Protocols and Addressing.',
    45,
    1,
    (SELECT id FROM users WHERE role = 'admin' LIMIT 1)
);

-- Store the test ID for reference
SET @test_id = LAST_INSERT_ID();

-- ============================================================
-- QUESTION 1 — Short Answer
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'Explain the difference between TCP and UDP protocols. In your answer, mention at least two key characteristics of each.',
    'short_answer',
    'TCP is a connection-oriented protocol that guarantees reliable, ordered delivery of packets through a three-way handshake and acknowledgement mechanisms. UDP is a connectionless protocol that sends datagrams without establishing a connection, offering faster transmission but no guarantee of delivery or ordering.',
    4,
    1
);

-- ============================================================
-- QUESTION 2 — MCQ
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'Which layer of the OSI model is responsible for logical addressing and routing of packets between different networks?',
    'multiple_choice',
    'C',
    1,
    2
);
SET @q2_id = LAST_INSERT_ID();
INSERT INTO question_options (question_id, option_key, option_text, is_correct) VALUES
    (@q2_id, 'A', 'Data Link Layer',    0),
    (@q2_id, 'B', 'Transport Layer',    0),
    (@q2_id, 'C', 'Network Layer',      1),
    (@q2_id, 'D', 'Session Layer',      0);

-- ============================================================
-- QUESTION 3 — Short Answer
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'What is the purpose of the Domain Name System (DNS)? Explain how it resolves a domain name to an IP address.',
    'short_answer',
    'DNS is a hierarchical naming system that translates human-readable domain names such as www.google.com into IP addresses that computers use to identify each other on a network. When a user enters a domain name, the DNS resolver queries a series of DNS servers starting from root servers down to authoritative name servers until the corresponding IP address is returned.',
    4,
    3
);

-- ============================================================
-- QUESTION 4 — MCQ
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'What is the default subnet mask for a Class B IP address?',
    'multiple_choice',
    'B',
    1,
    4
);
SET @q4_id = LAST_INSERT_ID();
INSERT INTO question_options (question_id, option_key, option_text, is_correct) VALUES
    (@q4_id, 'A', '255.0.0.0',       0),
    (@q4_id, 'B', '255.255.0.0',     1),
    (@q4_id, 'C', '255.255.255.0',   0),
    (@q4_id, 'D', '255.255.255.255', 0);

-- ============================================================
-- QUESTION 5 — Short Answer
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'Describe the TCP three-way handshake process. What are the three steps involved and what is the purpose of each step?',
    'short_answer',
    'The TCP three-way handshake establishes a reliable connection between client and server. Step 1: The client sends a SYN packet to the server to initiate a connection and synchronise sequence numbers. Step 2: The server responds with a SYN-ACK packet acknowledging the client SYN and sending its own SYN. Step 3: The client sends an ACK packet to acknowledge the server SYN, completing the connection establishment.',
    5,
    5
);

-- ============================================================
-- QUESTION 6 — MCQ
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'Which protocol is used to automatically assign IP addresses to devices on a network?',
    'multiple_choice',
    'A',
    1,
    6
);
SET @q6_id = LAST_INSERT_ID();
INSERT INTO question_options (question_id, option_key, option_text, is_correct) VALUES
    (@q6_id, 'A', 'DHCP — Dynamic Host Configuration Protocol', 1),
    (@q6_id, 'B', 'DNS — Domain Name System',                   0),
    (@q6_id, 'C', 'ARP — Address Resolution Protocol',          0),
    (@q6_id, 'D', 'FTP — File Transfer Protocol',               0);

-- ============================================================
-- QUESTION 7 — Short Answer
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'What is the difference between a hub, a switch, and a router? Explain the role of each device in a network.',
    'short_answer',
    'A hub is a basic networking device that broadcasts incoming data to all connected devices regardless of the destination, operating at the Physical layer. A switch is an intelligent device that forwards data only to the intended recipient by learning MAC addresses, operating at the Data Link layer. A router connects different networks and routes packets between them using IP addresses, operating at the Network layer.',
    5,
    7
);

-- ============================================================
-- QUESTION 8 — MCQ
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'Which of the following best describes a MAC address?',
    'multiple_choice',
    'B',
    1,
    8
);
SET @q8_id = LAST_INSERT_ID();
INSERT INTO question_options (question_id, option_key, option_text, is_correct) VALUES
    (@q8_id, 'A', 'A logical address assigned by a DHCP server',                     0),
    (@q8_id, 'B', 'A unique hardware address permanently assigned to a network interface card', 1),
    (@q8_id, 'C', 'An address used to identify a website on the internet',            0),
    (@q8_id, 'D', 'A temporary address used during the TCP handshake',                0);

-- ============================================================
-- QUESTION 9 — MCQ
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'At which OSI layer does the SSL/TLS protocol primarily operate?',
    'multiple_choice',
    'C',
    1,
    9
);
SET @q9_id = LAST_INSERT_ID();
INSERT INTO question_options (question_id, option_key, option_text, is_correct) VALUES
    (@q9_id, 'A', 'Network Layer',       0),
    (@q9_id, 'B', 'Transport Layer',     0),
    (@q9_id, 'C', 'Presentation Layer',  1),
    (@q9_id, 'D', 'Application Layer',   0);

-- ============================================================
-- QUESTION 10 — Short Answer
-- ============================================================
INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
VALUES (
    @test_id,
    'Explain what NAT (Network Address Translation) is and why it is used in modern networks.',
    'short_answer',
    'NAT is a technique used by routers to translate private IP addresses of devices within a local network into a single public IP address when communicating with external networks. It is used primarily to conserve the limited pool of public IPv4 addresses, allowing multiple devices on a private network to share one public IP address. It also provides a basic level of security by hiding internal IP addresses from the outside world.',
    4,
    10
);

-- ============================================================
-- VERIFY
-- ============================================================
SELECT
    q.order_index   AS 'No',
    q.question_type AS 'Type',
    LEFT(q.question_text, 60) AS 'Question',
    q.marks         AS 'Marks'
FROM questions q
WHERE q.test_id = @test_id
ORDER BY q.order_index;

SELECT
    CONCAT('Total Questions: ', COUNT(*))                              AS Summary FROM questions WHERE test_id = @test_id
UNION ALL SELECT CONCAT('Total Marks: ',    SUM(marks))               FROM questions WHERE test_id = @test_id
UNION ALL SELECT CONCAT('Short Answer: ',   COUNT(*))                 FROM questions WHERE test_id = @test_id AND question_type = 'short_answer'
UNION ALL SELECT CONCAT('MCQ: ',            COUNT(*))                 FROM questions WHERE test_id = @test_id AND question_type = 'multiple_choice';