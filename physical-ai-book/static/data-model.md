# Data Model: 1-ai-textbook-platform

**Branch**: `1-ai-textbook-platform` | **Date**: 2025-12-10 | **Spec**: specs/1-ai-textbook-platform/spec.md

## Entities and Relationships

### User
*   **Description**: Represents a user of the platform (student or instructor).
*   **Fields**:
    *   `id`: Primary Key, unique identifier (UUID).
    *   `username`: Unique username (String).
    *   `email`: Unique email address (String), used for login.
    *   `password_hash`: Hashed password (String).
    *   `profile_data`: JSONB/Text field for personalization preferences from signup survey and ongoing activity (e.g., learning style, interests, progress).
    *   `language_preference`: User's preferred display language (String, e.g., 'en', 'ur').
*   **Relationships**:
    *   One-to-many with `Submission` (a user can make many submissions).

### Course
*   **Description**: Represents a complete textbook course.
*   **Fields**:
    *   `id`: Primary Key, unique identifier (UUID).
    *   `title`: Title of the course (String).
    *   `description`: Brief description of the course (Text).
    *   `duration_weeks`: Expected duration of the course in weeks (Integer).
*   **Relationships**:
    *   One-to-many with `Chapter` (a course has many chapters).

### Chapter
*   **Description**: Represents a single chapter within a course.
*   **Fields**:
    *   `id`: Primary Key, unique identifier (UUID).
    *   `course_id`: Foreign Key to `Course` (UUID).
    *   `title`: Title of the chapter (String).
    *   `content`: The full content of the chapter in MDX format (Text/JSONB).
    *   `order`: Display order within the course (Integer).
*   **Relationships**:
    *   Many-to-one with `Course`.
    *   One-to-many with `Assessment` (chapters can have assessments).
    *   One-to-many with `VectorEmbedding` (chapter content can be embedded).

### Assessment
*   **Description**: Represents an assessment (MCQ, Capstone, etc.) related to a chapter or course.
*   **Fields**:
    *   `id`: Primary Key, unique identifier (UUID).
    *   `chapter_id`: Foreign Key to `Chapter` (UUID), optional for course-level assessments.
    *   `type`: Type of assessment (String, e.g., 'MCQ', 'Capstone').
    *   `title`: Title of the assessment (String).
    *   `data`: JSONB field containing questions/rubric specific to the assessment type.
*   **Relationships**:
    *   Many-to-one with `Chapter`.
    *   One-to-many with `Submission` (an assessment can have many submissions).

### Submission
*   **Description**: Records a user's submission for an assessment.
*   **Fields**:
    *   `id`: Primary Key, unique identifier (UUID).
    *   `assessment_id`: Foreign Key to `Assessment` (UUID).
    *   `user_id`: Foreign Key to `User` (UUID).
    *   `submission_data`: JSONB field containing the user's answers or submitted files/links.
    *   `score`: Score obtained by the user (Float/Integer, nullable until graded).
    *   `feedback`: Text field for feedback on the submission (Text, nullable).
*   **Relationships**:
    *   Many-to-one with `Assessment`.
    *   Many-to-one with `User`.

### VectorEmbedding
*   **Description**: Stores vector embeddings of content for RAG.
*   **Fields**:
    *   `id`: Primary Key, unique identifier (UUID).
    *   `content_id`: Foreign Key to the source content (e.g., `Chapter` ID, `Assessment` ID) (UUID).
    *   `vector_data`: The actual vector embedding (Array of Float).
    *   `source_text`: The original text segment that was embedded (Text).
*   **Relationships**:
    *   Many-to-one with various content entities (e.g., `Chapter`).

### Translation
*   **Description**: Stores translated text segments for multilingual support.
*   **Fields**:
    *   `id`: Primary Key, unique identifier (UUID).
    *   `original_text_hash`: Hash of the original English text for lookup (String).
    *   `language`: Target language code (String, e.g., 'ur' for Roman Urdu).
    *   `translated_text`: The translated text (Text).
*   **Relationships**:
    *   None explicitly defined, acts as a lookup table.

## Data Flow (High-level)

1.  **User Signup/Login**: Better-Auth handles user creation and authentication, `User` entity stores profile and preferences.
2.  **Content Retrieval**: Frontend fetches `Course` and `Chapter` data, including MDX content.
3.  **RAG Chatbot**: User query is embedded, Qdrant searches `VectorEmbedding` for relevant `source_text`, which is then sent to OpenAI for response generation.
4.  **Assessment Submission**: User input for assessments is stored in `Submission` entity.
5.  **Translation**: Frontend fetches `Translation` for UI and content based on `language_preference`.
6.  **Content Management (Instructor)**: Instructor interacts with API to create/update `Course`, `Chapter`, `Assessment` entities.
