from __future__ import annotations

# =============================================================================
# ACRONYM EXPANSION MAPS (per domain)
# =============================================================================
# Key   = acronym as student might write it
# Value = full expansion (acronym kept alongside for embedding coverage)

ACRONYM_MAP: dict[str, str] = {
    # Networking
    "TCP":   "Transmission Control Protocol TCP",
    "UDP":   "User Datagram Protocol UDP",
    "IP":    "Internet Protocol IP",
    "HTTP":  "Hypertext Transfer Protocol HTTP",
    "HTTPS": "Hypertext Transfer Protocol Secure HTTPS",
    "DNS":   "Domain Name System DNS",
    "OSI":   "Open Systems Interconnection OSI",
    "MAC":   "Media Access Control MAC",
    "LAN":   "Local Area Network LAN",
    "WAN":   "Wide Area Network WAN",
    "NAT":   "Network Address Translation NAT",
    "DHCP":  "Dynamic Host Configuration Protocol DHCP",
    "FTP":   "File Transfer Protocol FTP",
    "SMTP":  "Simple Mail Transfer Protocol SMTP",
    "ARP":   "Address Resolution Protocol ARP",
    "ICMP":  "Internet Control Message Protocol ICMP",
    "VPN":   "Virtual Private Network VPN",
    "SSL":   "Secure Sockets Layer SSL",
    "TLS":   "Transport Layer Security TLS",

    # Operating Systems
    "OS":    "Operating System OS",
    "CPU":   "Central Processing Unit CPU",
    "RAM":   "Random Access Memory RAM",
    "ROM":   "Read Only Memory ROM",
    "BIOS":  "Basic Input Output System BIOS",
    "PCB":   "Process Control Block PCB",
    "MMU":   "Memory Management Unit MMU",
    "TLB":   "Translation Lookaside Buffer TLB",
    "FIFO":  "First In First Out FIFO",
    "LIFO":  "Last In First Out LIFO",
    "FCFS":  "First Come First Served FCFS",
    "SJF":   "Shortest Job First SJF",
    "RR":    "Round Robin RR",
    "IPC":   "Inter Process Communication IPC",
    "DMA":   "Direct Memory Access DMA",
    "I/O":   "Input Output IO",

    # Object Oriented Programming
    "OOP":   "Object Oriented Programming OOP",
    "OOD":   "Object Oriented Design OOD",
    "UML":   "Unified Modeling Language UML",
    "API":   "Application Programming Interface API",
    "SOLID": "Single Responsibility Open Closed Liskov Interface Dependency SOLID",
    "DRY":   "Do not Repeat Yourself DRY",
    "KISS":  "Keep It Simple KISS",

    # General CS
    "DB":    "Database DB",
    "SQL":   "Structured Query Language SQL",
    "DBMS":  "Database Management System DBMS",
    "GUI":   "Graphical User Interface GUI",
    "CLI":   "Command Line Interface CLI",
    "IDE":   "Integrated Development Environment IDE",
    "SDK":   "Software Development Kit SDK",
    "VM":    "Virtual Machine VM",
    "JSON":  "JavaScript Object Notation JSON",
    "XML":   "Extensible Markup Language XML",
    "HTML":  "Hypertext Markup Language HTML",
    "CSS":   "Cascading Style Sheets CSS",
}

# =============================================================================
# SYNONYM MAPS (per domain)
# When a student uses a synonym, expand it to include the canonical term
# =============================================================================

SYNONYM_MAP: dict[str, str] = {
    # Networking synonyms
    "ensures":      "guarantees ensures",
    "transfers":    "transmits transfers",
    "link":         "connection link",
    "packet":       "datagram packet",
    "message":      "packet message datagram",

    # OOP synonyms
    "subclass":     "child class subclass derived class",
    "superclass":   "parent class superclass base class",
    "child class":  "subclass child class derived class",
    "parent class": "superclass parent class base class",
    "base class":   "parent class superclass base class",
    "derived class":"child class subclass derived class",
    "acquires":     "inherits acquires",
    "attributes":   "properties attributes fields",
    "behaviours":   "methods behaviours functions",
    "function":     "method function procedure",

    # OS synonyms
    "blocked":      "waiting blocked suspended",
    "suspended":    "blocked waiting suspended",
    "task":         "process task thread",
    "program":      "process program application",
    "assets":       "resources assets",
    "storage":      "memory storage",
    "swap":         "page swap",
    "processor":    "CPU processor",
}

# =============================================================================
# DOMAIN KEYWORD LISTS
# =============================================================================

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "networking": [
        "TCP", "UDP", "IP", "HTTP", "DNS", "OSI", "MAC", "LAN", "WAN",
        "router", "switch", "hub", "packet", "datagram", "protocol",
        "handshake", "three-way handshake", "connection", "socket",
        "bandwidth", "latency", "throughput", "firewall", "subnet",
        "gateway", "routing", "switching", "encapsulation", "frame",
        "transmission", "reliable", "unreliable", "connectionless",
        "connection-oriented", "port", "address", "broadcast", "unicast",
        "multicast", "NAT", "DHCP", "ARP", "ICMP", "VPN", "SSL", "TLS",
    ],
    "computer_science": [
        "algorithm", "complexity", "recursion", "iteration", "stack",
        "queue", "array", "linked list", "binary", "hash", "sorting",
        "searching", "inheritance", "polymorphism", "encapsulation",
        "abstraction", "class", "object", "method", "attribute",
        "constructor", "destructor", "interface", "abstract class",
        "overloading", "overriding", "subclass", "superclass",
        "OOP", "API", "UML", "SOLID", "design pattern",
    ],
    "operating_systems": [
        "process", "thread", "deadlock", "semaphore", "mutex",
        "scheduling", "FCFS", "SJF", "round robin", "priority",
        "virtual memory", "paging", "segmentation", "page fault",
        "thrashing", "kernel", "system call", "interrupt", "context switch",
        "race condition", "critical section", "synchronization",
        "CPU", "RAM", "memory management", "file system", "I/O",
        "buffering", "caching", "spooling", "DMA", "PCB", "TLB",
        "starvation", "livelock", "preemption", "dispatcher",
    ],
    "biology": [
        "photosynthesis", "chlorophyll", "mitosis", "meiosis", "osmosis",
        "diffusion", "respiration", "enzyme", "catalyst", "chromosome",
        "nucleus", "ribosome", "mitochondria", "ATP", "DNA", "RNA",
    ],
    "chemistry": [
        "oxidation", "reduction", "covalent", "ionic", "bond", "molecule",
        "atom", "electron", "proton", "neutron", "valence", "equilibrium",
        "catalyst", "reaction", "enthalpy", "entropy",
    ],
    "default": [],
}

# Domain detection hints
DOMAIN_HINTS: dict[str, list[str]] = {
    "networking": [
        "network", "TCP", "UDP", "IP", "HTTP", "DNS", "router",
        "packet", "protocol", "socket", "bandwidth", "OSI", "LAN", "WAN"
    ],
    "computer_science": [
        "class", "object", "OOP", "inheritance", "polymorphism",
        "encapsulation", "method", "function", "algorithm", "code",
        "program", "software", "interface", "abstract"
    ],
    "operating_systems": [
        "process", "thread", "OS", "kernel", "deadlock", "semaphore",
        "scheduling", "memory", "CPU", "virtual", "paging", "interrupt",
        "system call", "mutex", "synchronization"
    ],
    "biology": ["cell", "organism", "plant", "animal", "gene", "species", "protein"],
    "chemistry": ["element", "compound", "reaction", "acid", "base", "solution", "mole"],
}


def load_keywords(context: str) -> list[str]:
    """
    Detect subject domain from question context and return relevant keywords.
    """
    context_lower = context.lower()
    for domain, hints in DOMAIN_HINTS.items():
        if any(hint.lower() in context_lower for hint in hints):
            return DOMAIN_KEYWORDS.get(domain, [])
    return DOMAIN_KEYWORDS["default"]


def expand_acronyms(text: str) -> str:
    """
    Expand acronyms and synonyms in text so BERT can match them correctly.

    Example:
        "TCP uses three-way handshake" 
        → "Transmission Control Protocol TCP uses three-way handshake"
    """
    import re
    result = text

    # Expand acronyms (whole word match, case sensitive for acronyms)
    for acronym, expansion in ACRONYM_MAP.items():
        pattern = r'\b' + re.escape(acronym) + r'\b'
        if re.search(pattern, result):
            result = re.sub(pattern, expansion, result)

    # Expand synonyms (case insensitive)
    for synonym, expansion in SYNONYM_MAP.items():
        pattern = r'\b' + re.escape(synonym) + r'\b'
        if re.search(pattern, result, re.IGNORECASE):
            result = re.sub(pattern, expansion, result, flags=re.IGNORECASE)

    return result