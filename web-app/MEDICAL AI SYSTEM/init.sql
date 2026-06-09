-- =========================================================================
-- MEDICAL AI SYSTEM - PRODUCTION DATABASE DEPLOYMENT SCHEMA
-- =========================================================================

-- Enable core extension for distributed UUID handling
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================================================================
-- 1. ENUMERATED TYPES & STATE MACHINES
-- =========================================================================
CREATE TYPE user_role AS ENUM ('STUDENT', 'LECTURER');
CREATE TYPE submission_status AS ENUM ('PENDING', 'PROCESSING', 'FAILED', 'COMPLETED', 'APPROVED');
CREATE TYPE step_status AS ENUM ('NOT_STARTED', 'RUNNING', 'SUCCESS', 'FAILED');

-- =========================================================================
-- 2. CORE SYSTEM TABLES
-- =========================================================================

-- USERS TABLE
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role user_role NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- SUBMISSIONS TABLE (Includes full async pipeline lifecycle state machine)
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    file_url TEXT NOT NULL,
    status submission_status NOT NULL DEFAULT 'PENDING',
    
    -- Real-time progress tracking indicators for Front-End UI dashboards
    detection_step step_status NOT NULL DEFAULT 'NOT_STARTED',
    ocr_step step_status NOT NULL DEFAULT 'NOT_STARTED',
    verification_step step_status NOT NULL DEFAULT 'NOT_STARTED',
    explainability_step step_status NOT NULL DEFAULT 'NOT_STARTED',
    scoring_step step_status NOT NULL DEFAULT 'NOT_STARTED',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================================
-- 3. PIPELINE METADATA & ARTIFACT TABLES
-- =========================================================================

-- DETECTION RESULTS (YOLO Bounding Boxes & Attention U-Net Segmentations)
CREATE TABLE detection_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL UNIQUE REFERENCES submissions(id) ON DELETE RESTRICT,
    crop_urls TEXT[] NOT NULL DEFAULT '{}',
    mask_urls TEXT[] NOT NULL DEFAULT '{}',
    overlay_urls TEXT[] NOT NULL DEFAULT '{}',
    raw_detections JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- OCR RESULTS (EasyOCR Core Extractions)
CREATE TABLE ocr_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL UNIQUE REFERENCES submissions(id) ON DELETE RESTRICT,
    extracted_text TEXT,
    raw_ocr_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- MULTIMODAL VERIFICATION RESULTS (CLIP, SBERT embeddings & Ontologies)
CREATE TABLE multimodal_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL UNIQUE REFERENCES submissions(id) ON DELETE RESTRICT,
    similarity_scores JSONB NOT NULL DEFAULT '{}'::jsonb,
    label_matches JSONB NOT NULL DEFAULT '{}'::jsonb,
    spatial_validation JSONB NOT NULL DEFAULT '{}'::jsonb,
    verification_results JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- EXPLAINABILITY METADATA (GradCAM, Attributions & Heatmaps)
CREATE TABLE explainability_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL UNIQUE REFERENCES submissions(id) ON DELETE RESTRICT,
    gradcam_url TEXT,
    attention_map_url TEXT,
    heatmap_url TEXT,
    attribution_scores JSONB NOT NULL DEFAULT '{}'::jsonb,
    explanation_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================================
-- 4. FRONT-END EVALUATION & EVALUATION RESULTS
-- =========================================================================

-- FINAL SCORING & INSTRUCTOR REVIEWS TABLE
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL UNIQUE REFERENCES submissions(id) ON DELETE RESTRICT,
    ai_score NUMERIC(5, 2) NOT NULL CHECK (ai_score >= 0.00 AND ai_score <= 100.00),
    scores_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb,
    lecturer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    lecturer_feedback TEXT,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Rule: If approval timestamp exists, an evaluation lecturer ID MUST be assigned
    CONSTRAINT check_approval_requires_lecturer 
        CHECK ( (approved_at IS NULL) OR (approved_at IS NOT NULL AND lecturer_id IS NOT NULL) )
);

-- =========================================================================
-- 5. PERFORMANCE OPTIMIZATION INDEXES
-- =========================================================================

-- Relational Foreign Key Indexes
CREATE INDEX idx_submissions_student ON submissions(student_id);
CREATE INDEX idx_submissions_status ON submissions(status);
CREATE INDEX idx_results_lecturer ON results(lecturer_id);

-- GIN Indexes for fast, deep-nested JSON searching by microservices/analytics
CREATE INDEX idx_detection_raw_json ON detection_results USING gin (raw_detections);
CREATE INDEX idx_multimodal_verification_json ON multimodal_verifications USING gin (verification_results);
CREATE INDEX idx_scoring_breakdown_json ON results USING gin (scores_breakdown);

-- =========================================================================
-- 6. BUSINESS LOGIC ROLE INTEGRITY ENFORCEMENT
-- =========================================================================

-- DB Function to validate that a grading user actually holds the LECTURER role
CREATE OR REPLACE FUNCTION verify_user_is_lecturer()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lecturer_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM users 
            WHERE id = NEW.lecturer_id AND role = 'LECTURER'
        ) THEN
            RAISE EXCEPTION 'Database Integrity Violation: Assigned lecturer (User ID: %) does not possess the LECTURER application role.', NEW.lecturer_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger binding to watch rows during insert or administrative evaluation overrides
CREATE TRIGGER enforce_lecturer_role_integrity
    BEFORE INSERT OR UPDATE ON results
    FOR EACH ROW
    EXECUTE FUNCTION verify_user_is_lecturer();