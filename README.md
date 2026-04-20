# Automatic Short Answer Grading System for STEM Education

## 3. Approach / Methodology

### 3.1 Description

This project follows an **iterative, model-driven software development methodology** structured around five distinct phases. The methodology emphasizes systematic literature grounding, modular architecture design, robust implementation of BERT-based components, rigorous evaluation, and comprehensive documentation.

### Project Phases

#### Phase 1 – Literature Review and Requirements Analysis
- Systematic review of existing BERT-based Automatic Short Answer Grading (ASAG) literature
- Identification and analysis of relevant public datasets
- Specification of system requirements, including:
  - Component score definitions (semantic similarity + terminology coverage)
  - User interface and experience requirements
  - Evaluation protocols and success metrics

#### Phase 2 – System Design
- High-level architecture design of the **multi-component scoring pipeline**
- Selection of appropriate BERT-based models
- Design of fine-tuning strategy for STEM short-answer tasks
- Design of the **semantic scoring module**
- Design of the **terminology extraction/coverage module**
- Definition of score aggregation logic
- Creation of UML diagrams to document system architecture

#### Phase 3 – Development and Implementation
- Fine-tuning of BERT models on STEM short-answer datasets
- Implementation of the **semantic scoring module** using cosine similarity of BERT sentence embeddings
- Implementation of the **terminology coverage module** using:
  - Domain ontology / keyword lists
  - Contextual BERT token-level analysis
- Integration of both modules into a unified scoring pipeline
- Development of a **web-based user interface** for instructors and students

#### Phase 4 – Evaluation and Testing
**Quantitative Evaluation:**
- Benchmark datasets: **SciEntsBank** and **Beetle**
- Comparison against human-graded responses
- Metrics: Pearson correlation, Cohen's Kappa, F1-score, Mean Absolute Error (MAE)

**Qualitative Evaluation:**
- User study with domain instructors
- Assessment of interpretability and practical utility of the component score outputs

#### Phase 5 – Documentation and Reporting
- Comprehensive system and API documentation
- Final project report
- Dissemination of findings (academic paper, repository, etc.)

---

## Key Features of the Methodology

- **Iterative Development**: Allows continuous refinement based on evaluation results
- **Model-Driven**: Strong emphasis on BERT-based language models tailored for educational assessment
- **Multi-Component Scoring**: Combines semantic understanding with domain-specific terminology coverage
- **Explainable AI Focus**: Provides component-level scores instead of a single black-box grade
- **Education-Oriented**: Designed specifically for STEM short-answer grading with instructor-friendly outputs

This structured approach ensures the development of a reliable, interpretable, and pedagogically useful Automatic Short Answer Grading system.