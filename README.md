## 3. Methodology

### 3.1 Project Design

The project adopts a **Design and Implementation** research methodology, which is particularly suitable for developing and evaluating innovative technological artifacts that solve real-world educational problems (Peffers et al., 2015). 

This approach focuses on both the **creation** of a practical artifact — in this case, an **AI-enhanced Medical Diagram Assessment System** — and its rigorous empirical evaluation in terms of accuracy, usability, and pedagogical effectiveness.

The primary goal of the system is to:

1. Accurately segment, detect, and recognize components in medical diagrams.
2. Extract textual labels and verify their semantic association with visual elements.
3. Provide clear, interpretable feedback to both students and instructors.
4. Integrate seamlessly into existing Learning Management Systems (LMS).

### 3.1.1 Iterative Development Approach

The project follows an **iterative design and development cycle**, allowing continuous refinement based on empirical feedback and testing results. Each phase builds upon the previous one, ensuring the final artifact aligns with both technical feasibility and educational objectives.

#### Phases of the Project:

**1. Problem Analysis**
- Identify key challenges in automated medical diagram assessment, such as style variability, incomplete drawings, and semantic verification (as discussed in Chapter 2).
- Review existing AI models, educational technologies, and LMS capabilities to identify limitations and opportunities.
- Define critical performance metrics, including segmentation accuracy, object detection precision, OCR accuracy, and feedback interpretability.

**2. System Requirements Specification**
- Define **functional requirements**: diagram segmentation, anatomical component detection, text label extraction, multimodal reasoning, and feedback generation.
- Define **non-functional requirements**: scalability, real-time performance, LMS compatibility, and explainability.
- Specify data requirements, including the need for annotated medical diagrams, labels, and metadata for training and evaluation.

**3. Modular System Design**
- Adopt a **modular architecture** with interdependent yet independent components:
  - **Preprocessing Module**: Image normalization, noise removal, and perspective correction.
  - **Segmentation Module**: Pixel-level extraction of diagram components using U-Net or Attention U-Net.
  - **Object Detection Module**: Identification and localization of anatomical structures using **YOLOv8**.
  - **OCR Module**: Extraction of textual labels from diagram regions (using PaddleOCR or similar).
  - **Multimodal Reasoning Module**: Alignment of visual components with textual labels using embedding models such as **CLIP**.
  - **Explainability Module**: Generation of heatmaps, attention maps, or feature attributions for transparent feedback.
- The modular design enhances scalability, maintainability, and future extensibility (e.g., integration with various LMS platforms).

**4. Implementation of AI Modules**
- Develop each module using state-of-the-art deep learning frameworks (**PyTorch**, **TensorFlow**, or **PaddleOCR**).
- Apply **transfer learning** by leveraging pre-trained models and fine-tuning them on domain-specific medical diagram datasets.
- Integrate all modules into a unified pipeline ensuring smooth data flow from preprocessing through segmentation, detection, OCR, multimodal reasoning, and explainability.

**5. Technical and Educational Evaluation**
- **Quantitative Evaluation**:
  - Segmentation: Dice Coefficient and Intersection over Union (IoU)
  - Object Detection: Mean Average Precision (mAP)
  - OCR: Text extraction accuracy and label verification rates
- **Qualitative Evaluation**: Gather instructor and student feedback on interpretability, usability, and learning enhancement.
- Iterate on the system design based on evaluation results to improve accuracy and quality of feedback.

**6. Deployment and Validation**
- Deploy the system in a controlled educational environment or integrated LMS platform for pilot testing.
- Validate performance using real student-submitted medical diagrams.
- Document lessons learned, system limitations, and recommendations for broader academic adoption.

### 3.1.2 Rationale for Design and Implementation Approach

The **Design and Implementation** methodology is well-suited for this project because:

- It enables the construction of a novel AI artifact specifically tailored for automated medical diagram assessment.
- It supports rigorous empirical evaluation, allowing both quantitative performance measurement and qualitative pedagogical assessment.
- The iterative nature facilitates continuous refinement to address complex challenges such as diagram variability and multimodal reasoning.
- It effectively bridges the gap between cutting-edge AI research and real-world pedagogical practice, ensuring the system is both technically sound and educationally valuable.

---

This structured methodology ensures the development of a robust, accurate, explainable, and pedagogically effective AI system for assessing medical diagrams in higher education.