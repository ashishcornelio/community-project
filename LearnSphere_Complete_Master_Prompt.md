# MASTER PROMPT: BUILD LEARNSPHERE --- ADAPTIVE LEARNING AND MASTERY SYSTEM

## 1. ROLE AND OBJECTIVE

Act as an expert full-stack developer, educational technology designer,
learning-science specialist, UI/UX designer, and machine-learning
engineer.

Design and develop a complete, functional, user-friendly educational web
application named **LearnSphere --- Adaptive Learning and Mastery
System**.

**Tagline: Learn at Your Level. Practise at Your Pace. Master It
Yourself.**

LearnSphere is designed for both school and college students. Its
primary purpose is to help students understand concepts, practise
independently, identify their learning gaps, improve memory, prepare for
examinations, and track their academic progress.

The platform must support:

-   Students who require additional explanations and foundational
    practice.
-   Students who understand concepts at an average pace and need regular
    practice.
-   Students who learn quickly and want advanced challenges.
-   Teachers who need to monitor student progress and identify common
    learning difficulties.

The platform must use **structured educational content, rule-based
personalization, conventional algorithms, and learning-science
techniques as its foundation**. AI should be used only when it provides
meaningful additional value.

Do not create a simple chatbot, static website, or dashboard containing
fake information. Build an integrated learning application in which the
major features work together.

------------------------------------------------------------------------

## 2. CORE DESIGN PRINCIPLE

The system must teach students how to understand and solve problems
rather than simply giving them answers.

Follow this learning cycle:

**Assess → Understand Learning Needs → Simplify → Visualize → Learn →
Practise → Identify Mistakes → Improve → Revise → Master → Track
Progress**

Every major feature should support this learning cycle.

Two defining principles of LearnSphere are **"One Topic, Many Ways to
Learn"** and **"Understand the Student, Not Just Their Marks."** The
system must adapt both how content is presented and what the student
should do next.

Students must not be permanently classified as weak or intelligent.
Their learning needs must be evaluated separately for each subject and
topic.

Students should be able to learn at their own pace without being
embarrassed, compared publicly, or restricted by a permanent ability
label.

------------------------------------------------------------------------

## 3. USER ROLES

Create three main user roles.

### A. Student

Students can:

-   Access their personalized dashboard.
-   Select their education level, class or semester, and subjects.
-   Read subject-wise notes.
-   Learn concepts through simple explanations.
-   Access diagrams, illustrations, and worked examples.
-   Complete diagnostic assessments and practice quizzes.
-   Receive hints and explanations for mistakes.
-   View their progress through charts and graphs.
-   Receive personalized revision recommendations.
-   Download available learning materials.
-   Switch between supported learning languages.
-   View assignments, study schedules, and upcoming examinations.
-   Access Foundation, Standard, and Challenge learning modes.

### B. Teacher

Teachers can:

-   Create and manage classes.
-   Add or organize subjects, chapters, and topics.
-   Upload or prepare study materials.
-   Create assignments, quizzes, and examinations.
-   Add questions, correct answers, hints, and explanations.
-   Review student scores and topic-level mastery.
-   View class-wide performance charts.
-   Identify common misconceptions.
-   Identify students who may need additional support.
-   Identify students ready for advanced practice.
-   Recommend revision activities.
-   Review individual progress where authorized.

### C. Administrator

Administrators can:

-   Manage users and roles.
-   Manage subjects, education levels, and classes.
-   Maintain the subject and chapter structure.
-   Manage access permissions.
-   Review application activity.
-   Configure supported languages.
-   Manage approved educational resources.
-   Monitor system health.

Use role-based authentication and ensure each user can access only the
features and records permitted for their role.

------------------------------------------------------------------------

## 4. COMPLETE STUDENT DASHBOARD

The student dashboard is one of the most important parts of the project.

Create a modern, attractive, responsive dashboard with a clean layout
and simple navigation.

### Dashboard header

Display:

-   Student's first name or preferred display name.
-   Education level.
-   Class or semester.
-   Current date.
-   Notification icon.
-   Profile and settings.
-   Language selector.

### Dashboard summary cards

Display the following information using real data from the database:

1.  Subjects Enrolled
2.  Topics Completed
3.  Overall Learning Progress
4.  Average Quiz Score
5.  Topics Requiring Practice
6.  Revision Tasks Due Today
7.  Assignments Pending
8.  Current Learning Streak

Calculate each value from actual records. Do not hardcode statistics.

If no data is available, show an appropriate empty state instead of
fabricated results.

### Dashboard graphical representation

Use interactive charts and graphs to visualize academic performance.

Include:

**1. Subject-Wise Performance --- Bar Chart**

Show the student's average quiz performance for each subject.

Example subjects:

-   Mathematics
-   Science
-   English
-   Social Science
-   Computer Science
-   Programming
-   Data Structures

Display only subjects relevant to the student's selected education level
and enrolled courses.

**2. Learning Progress --- Line Chart**

Show performance over time using dated quiz attempts or assessments.

Allow the student to change the time range when sufficient data is
available.

**3. Topic Mastery --- Horizontal Bar Chart**

Show topic-level mastery estimates, clearly distinguishing mastered
topics from topics that require further practice.

**4. Time Distribution --- Doughnut Chart**

Show the distribution of recorded learning activity across subjects.

Do not interpret time spent as proof of understanding.

**5. Quiz Accuracy --- Line or Bar Chart**

Display correct and incorrect responses over time.

**6. Learning Activity --- Calendar Heatmap**

Display completed lessons, quizzes, and revision sessions by date.

**7. Learning Gap Visualization**

Display topics needing attention, grouped by subject.

**8. Confidence vs. Correctness --- Comparison Chart**

When confidence ratings are available, visualize the relationship
between student confidence and quiz accuracy.

Use clear labels, legends, tooltips, accessible colours, and responsive
layouts.

Do not display misleading graphs when the underlying dataset is
insufficient.

### Dashboard learning recommendations

Include sections such as:

-   Continue Learning
-   Recommended for You
-   Revise Today
-   Practise Difficult Topics
-   Explore Advanced Questions
-   Recently Studied
-   Upcoming Assignments

Each recommendation must connect to an actual lesson, quiz, revision
activity, or topic.

------------------------------------------------------------------------

## 5. COMPLETE SUBJECT-WISE LEARNING LIBRARY

Create a comprehensive learning library organized by education level,
subject, chapter, and topic.

The library must support both school and college curricula.

### School subjects

Provide a configurable structure for subjects such as:

-   Mathematics
-   Science
-   Physics
-   Chemistry
-   Biology
-   English
-   Hindi
-   Kannada
-   Social Science
-   History
-   Geography
-   Civics
-   Computer Science

The exact subject list must be configurable according to the student's
board, class, and curriculum.

### College subjects

Support configurable subjects such as:

-   Engineering Mathematics
-   Programming in C
-   Python Programming
-   Data Structures and Algorithms
-   Database Management Systems
-   Operating Systems
-   Computer Networks
-   Artificial Intelligence
-   Machine Learning
-   Statistics
-   Electronics
-   Physics
-   Chemistry
-   Other degree-specific subjects

Do not force school and college students to use the same syllabus
structure.

### Subject navigation

Organize content using this hierarchy:

Education Level → Class or Semester → Subject → Chapter or Unit → Topic
→ Learning Material → Practice Questions.

Provide:

-   Search by subject.
-   Search by chapter.
-   Search by topic.
-   Filter by education level.
-   Filter by difficulty.
-   Bookmarking.
-   Recently viewed topics.
-   Completed topics.
-   Downloadable materials when permitted.
-   A notes-format selector for simple notes, point-wise notes, detailed
    notes, exam-ready notes, visual notes, practice, teach-back, and
    revision.
-   Engagement trends shown separately from topic mastery.
-   Visual learning activities suited to the selected subject and topic.

### Requirements for study notes

Every subject should support detailed, structured study notes.

Each topic page should contain, where appropriate:

1.  Topic introduction.
2.  Learning objectives.
3.  Simple explanation.
4.  Detailed conceptual explanation.
5.  Important definitions.
6.  Key terms.
7.  Formulas and their meanings.
8.  Step-by-step worked examples.
9.  Real-world applications.
10. Diagrams and labelled illustrations.
11. Tables and comparisons.
12. Important points for revision.
13. Common mistakes.
14. Frequently asked questions.
15. Practice questions.
16. Quick revision summary.
17. Flashcards.
18. Further reading or teacher-provided references.
19. Simple notes in easy-to-understand language.
20. Point-wise notes with organized headings and bullet points.
21. Exam-oriented notes based on the supplied syllabus and
    teacher-approved material.
22. Visual notes using suitable flowcharts, mind maps, timelines,
    concept maps, diagrams, and comparison tables.
23. One-page summaries, formula sheets, key takeaways, and quick
    revision sheets.

Provide separate content sections for:

-   Quick Revision Notes.
-   Detailed Study Notes.
-   Important Definitions.
-   Important Formulas.
-   Worked Examples.
-   Examination Preparation.
-   Practice Questions.
-   Advanced Concepts.

Use readable formatting, proper mathematical notation, tables, diagrams,
and code blocks where relevant.

For programming subjects, support syntax-highlighted code examples and
explanations.

For science subjects, support labelled diagrams and concept
illustrations.

For mathematics, support equations, worked solutions, and step-by-step
problem solving.

For social sciences, support timelines, maps, comparisons, key events,
and summaries.

For languages, support vocabulary, grammar, comprehension, writing
exercises, and examples.

### Content accuracy

Use teacher-reviewed content, verified educational resources, and
curriculum-aligned materials.

Do not fabricate textbooks, citations, official syllabus requirements,
or examination questions.

Clearly distinguish teacher-provided content, externally sourced
content, and automatically generated assistance.

Do not claim to provide every subject's complete syllabus unless the
content has actually been supplied or verified.

Build a content management system that allows teachers to add and update
lessons without modifying the source code.

------------------------------------------------------------------------

## 5A. MULTI-FORMAT NOTES GENERATOR --- ONE TOPIC, MANY WAYS TO LEARN

Create a dedicated notes-format selector for every supported topic.
Students must be able to switch formats without losing their place.

Provide these formats:

1.  **Simple Notes:** Explain concepts in easy-to-understand language,
    break complex ideas into smaller steps, define unfamiliar terms, and
    use suitable everyday examples.
2.  **Point-Wise Notes:** Convert content into organized headings,
    subheadings, bullet points, definitions, formulas, and key facts.
3.  **Detailed Notes:** Provide complete conceptual explanations,
    reasoning, examples, and connections between ideas.
4.  **Exam-Ready Notes:** Organize material into syllabus-aligned
    definitions, short-answer points, long-answer structures, formulas,
    diagrams, and examples. Use the supplied syllabus and approved
    materials; do not invent official requirements or past examination
    questions.
5.  **Visual Notes:** Represent ideas through accurate diagrams,
    flowcharts, mind maps, timelines, comparison tables, concept maps,
    graphs, and labelled illustrations where suitable.
6.  **Quick Revision:** Provide one-page summaries, key takeaways,
    flashcards, important formulas, definitions, and frequently confused
    concepts.
7.  **Worked Examples:** Show step-by-step methods and explain why each
    step is performed.
8.  **Practice Mode:** Provide questions, hints, answers, and
    explanations appropriate to the topic and the student's demonstrated
    mastery.

Use structured, verified educational content as the primary source.
Teachers must be able to create, edit, review, approve, and publish
notes. Clearly label AI-generated content that has not been reviewed.
Never fabricate facts, formulas, textbook references, citations,
syllabus requirements, or official examination questions.

Where appropriate, let students compare the formats and choose their
preferred one. Use later quiz performance, retention checks, and
independent problem-solving to estimate whether a format helped with a
particular topic. Do not assume that a student has one fixed learning
style across all subjects.

------------------------------------------------------------------------

## 5B. VISUAL LEARNING WORKSPACE

Create a dedicated visual learning workspace that chooses
representations suited to the subject and concept.

Examples include:

-   Mathematics: function graphs, geometric diagrams, formula
    demonstrations, and worked-solution steps.
-   Science: labelled scientific diagrams, process illustrations,
    circuit diagrams, and chemical representations.
-   Social Science: timelines, maps, historical comparisons, and
    cause-and-effect diagrams.
-   Programming and Computer Science: flowcharts, algorithm traces,
    data-structure diagrams, code execution steps, and system
    architecture diagrams.
-   Languages: sentence structures, vocabulary maps, grammar tables, and
    concept examples.

Prefer structured diagrams, SVG, Canvas, mathematical graphing, and
verified educational assets when accuracy matters. Do not rely
exclusively on AI-generated images for technical or scientific diagrams.
Provide labels, legends, accessible descriptions, and explanations. If a
suitable visual is unavailable, show a clear text explanation rather
than a misleading or decorative image.

Visual learning should be connected to the topic lesson, notes, practice
questions, and mastery tracking rather than existing as an unrelated
gallery.

------------------------------------------------------------------------

## 5C. ADAPTIVE STUDENT ENGAGEMENT --- ACTIVE, MODERATE, AND LOW ENGAGEMENT

Track **engagement separately from knowledge, performance, and topic
mastery**. Use three flexible descriptions of recent engagement
patterns:

-   **Active Engagement:** The student regularly attempts questions,
    participates in practice, reviews mistakes, revisits difficult
    topics, or explains concepts.
-   **Moderate Engagement:** The student completes some learning
    activities but participates inconsistently or benefits from
    occasional guidance.
-   **Low or Passive Engagement:** The student mainly consumes material,
    frequently skips available practice, or rarely responds to
    interactive activities.

These descriptions are temporary, topic-sensitive indicators, not fixed
identities or measures of intelligence. A student may show active
engagement in one subject and lower engagement in another. Do not infer
motivation or ability from screen time, login frequency, or limited
activity alone. Allow students to correct preferences and choose their
own pace.

Use observable application events such as lesson completion, practice
attempts, attempts before viewing a solution, use of hints, responses to
feedback, revision activity, and voluntary confidence ratings. Explain
the indicators used and avoid unsupported psychological conclusions.

Adapt the next activity thoughtfully:

-   **For active engagement:** When mastery supports it, recommend
    advanced questions, real-world applications, cross-topic problems,
    projects, and teach-back activities.
-   **For moderate engagement:** Offer guided practice, short
    interactive tasks, worked examples, focused feedback, and manageable
    learning sessions.
-   **For low or passive engagement:** Offer smaller steps, simple
    explanations, visual alternatives, one-question check-ins, guided
    exercises, and optional reminders. Encourage participation without
    shame, punishment, or negative labels.

Do not confuse engagement with correctness. A highly engaged student may
need foundational help, while a quiet student may understand the
material well. Select Foundation, Standard, or Challenge activities
primarily from demonstrated understanding and prerequisite mastery,
using engagement only to shape the activity's presentation and support.

------------------------------------------------------------------------

## 5D. PERSONALIZED FORMAT SELECTOR

For each topic, provide the following student-controlled options:

-   **Read It:** Detailed explanations and structured notes.
-   **Quick Notes:** Concise, point-wise notes.
-   **See It:** Diagrams, flowcharts, graphs, and mind maps.
-   **Practise It:** Questions, worked examples, and progressive hints.
-   **Explain It:** Teach-back activities and interactive questions.
-   **Revise It:** Flashcards, formulas, summaries, and scheduled
    review.

Recommend a format using the student's stated preference and previous
outcomes, but always allow the student to switch formats. Evaluate
usefulness through later understanding checks, retention, and
independent application---not merely clicks or time spent. Do not
describe these options as fixed psychological learning styles.

------------------------------------------------------------------------

## 5E. INTEGRATION WITH STUDENT AND TEACHER DASHBOARDS

Add these elements to the student dashboard:

-   Subject-wise notes library with simple, point-wise, detailed,
    exam-ready, and visual formats.
-   Topic mastery map and prerequisite gaps.
-   Engagement and participation trends displayed separately from
    mastery.
-   Quiz accuracy and improvement graphs.
-   Common mistakes and misconception tracking.
-   Recommended next activity with a short explanation of why it was
    recommended.
-   Revision planner, flashcards, and topics due for review.
-   Pending practice, completed activities, and recently studied topics.
-   A clear control to choose the preferred learning format.

Add these elements to the teacher dashboard:

-   Class-level engagement and participation trends.
-   Topic-level mastery and learning gaps.
-   Common misconceptions and frequently missed questions.
-   Students who may benefit from additional support or advanced
    practice.
-   Filters by class, subject, chapter, topic, and date range.

Teacher dashboards must support teacher judgment rather than
automatically diagnose students. Individual student records must be
available only to authorized users. Use real database records for all
charts, and display honest empty states when data is insufficient.

------------------------------------------------------------------------

## 5F. IMPLEMENTATION RULES FOR ADAPTIVE NOTES AND ENGAGEMENT

Implement routine behaviour with transparent application logic wherever
possible:

-   Notes-format selection and navigation.
-   Quiz scoring and correctness calculations.
-   Engagement indicators based on recorded learning actions.
-   Topic mastery and prerequisite checks.
-   Hint progression and misconception matching.
-   Revision scheduling.
-   Dashboard calculations and charts.
-   Recommendation rules.

Use AI selectively for simplifying approved content, creating
alternative explanations, optional translation, or providing feedback on
open-ended responses. Provide teacher review for important educational
content and clearly distinguish reviewed content from unreviewed
generated assistance. The application must continue to provide its core
learning features when an AI service is unavailable.

Do not claim that personalization or engagement classification is
effective until it has been evaluated. Do not show fabricated
statistics, fake learning histories, or unsupported predictions. Protect
student privacy and send only the minimum necessary information to any
optional external AI service.

The final product must help students understand concepts, practise
independently, correct misconceptions, revise effectively, and
demonstrate mastery---not merely consume notes or receive generated
answers.

------------------------------------------------------------------------

## 6. ADAPTIVE LEARNING ENGINE

Implement three learning paths.

### A. Foundation Mode

For students who need additional conceptual support.

Features:

-   Prerequisite concept review.
-   Simple explanations.
-   Everyday examples.
-   Visual representations.
-   Basic questions.
-   Guided practice.
-   Additional hints.
-   Gradually increasing difficulty.

If a student struggles repeatedly, check whether the difficulty may be
caused by a missing prerequisite.

Recommend the prerequisite lesson instead of simply repeating the same
question.

### B. Standard Mode

For students who understand the fundamentals but need practice.

Features:

-   Structured explanations.
-   Worked examples.
-   Moderate-difficulty questions.
-   Guided hints.
-   Conceptual questions.
-   Application-based problems.
-   Regular revision.

### C. Challenge Mode

For students who demonstrate sufficient mastery.

Features:

-   Advanced problems.
-   Multi-step reasoning.
-   Real-world applications.
-   Higher-order thinking questions.
-   Programming challenges where relevant.
-   Cross-topic questions.
-   Case studies.
-   Optional timed practice.

Allow students to choose a different mode even when the system
recommends one.

### Adaptive selection logic

Use quiz correctness, question difficulty, prerequisite mastery,
repeated mistakes, and previous performance to recommend suitable
activities.

Do not change learning difficulty based on a single answer alone.

Use configurable rules and document how the recommendation engine works.

Keep all recommendations explainable.

For example:

"You are practising equivalent fractions because your recent answers
suggest that this concept needs additional practice."

Do not display unsupported psychological conclusions or permanent
ability labels.

------------------------------------------------------------------------

## 7. MISTAKE DETECTIVE

Create a dedicated misconception-detection feature.

The system must do more than display "Correct" or "Incorrect."

For selected questions, store:

-   The correct answer.
-   Common incorrect answers.
-   Likely misconceptions.
-   Explanations of those misconceptions.
-   Targeted follow-up questions.

Example:

Question: Solve 2(x + 3) = 14.

If a student answers using an incorrect distribution of multiplication,
the system should identify the matching error pattern when possible.

It should then:

1.  Explain the mistake.
2.  Show the correct reasoning.
3.  Provide a similar example.
4.  Offer another practice question.
5.  Record whether the student improves.

Implement this initially using predefined rules and teacher-authored
error patterns.

Do not claim to know why a student made an error when the available
answer does not support that conclusion.

------------------------------------------------------------------------

## 8. HINT LADDER

Create a progressive assistance system.

When a student gets stuck, provide these assistance levels:

-   Hint 1: Recall a relevant concept.
-   Hint 2: Suggest the next step.
-   Hint 3: Provide a partial solution.
-   Hint 4: Show a worked example.
-   Final Explanation: Show the full solution with reasoning.

Students should be able to request help in simple language.

Record which hints were used so the student can review their learning
process.

Do not reveal complete solutions immediately when a small hint may be
sufficient.

Teachers must be able to configure hint levels for their questions.

------------------------------------------------------------------------

## 9. CONFIDENCE VS. KNOWLEDGE TRACKER

After selected questions, allow students to indicate confidence using
simple options:

-   Not Sure
-   Somewhat Sure
-   Very Sure

Combine confidence ratings with correctness to guide subsequent
practice.

Examples:

Correct with high confidence: Recommend more advanced practice when
supported by other assessment results.

Incorrect with high confidence: Recommend checking the underlying
concept and possible misconceptions.

Correct with low confidence: Recommend additional practice and retrieval
exercises.

Incorrect with low confidence: Offer foundation explanations and guided
practice.

Display these results as learning indicators rather than psychological
diagnoses.

Use rule-based logic. No AI model is required for this feature.

------------------------------------------------------------------------

## 10. LEARNING GAP MAP AND PREREQUISITE TRACKING

Represent topic dependencies using a graph or structured prerequisite
relationships.

Example:

Fractions → Algebraic Operations → Linear Equations → Quadratic
Equations.

If a student struggles with a topic, examine their performance on the
prerequisite topics.

Recommend the most relevant missing concept.

Show a visual learning map with states such as:

-   Not Started.
-   In Progress.
-   Needs Practice.
-   Demonstrated Mastery.

Use a clear visual distinction between completed topics and recommended
next steps.

Do not permanently block students from exploring advanced topics.

Allow teachers to configure prerequisite relationships for each subject.

------------------------------------------------------------------------

## 11. SMART REVISION AND SPACED REPETITION

Implement a revision scheduler based on previous performance and time
since the last review.

Provide:

-   Daily revision tasks.
-   Topic review reminders.
-   Flashcards.
-   Short quizzes.
-   Forgotten Concepts List.
-   Revision calendar.
-   Revision history.
-   Review recommendations.

A possible initial schedule is Day 1, Day 2, Day 5, Day 10, and Day 20,
but the intervals must adjust according to performance and should not be
treated as universally optimal.

If a student struggles during review, schedule earlier revision.

If the student consistently recalls concepts correctly, gradually
increase the review interval.

Allow students to mark tasks completed, but use assessment results to
estimate understanding.

Display revision tasks directly on the dashboard.

Implement this using conventional scheduling algorithms rather than AI.

------------------------------------------------------------------------

## 12. TEACH-BACK MODE

Create an activity in which students explain a concept in their own
words.

For example:

"Explain photosynthesis as if you were teaching it to a friend."

Evaluate the response using:

-   Teacher-defined rubrics.
-   Required concepts.
-   Important terminology.
-   Explanation completeness.
-   Logical consistency, where assessable.

Provide constructive feedback such as:

"You explained the role of sunlight, but you should also mention how
water and carbon dioxide contribute to the process."

Start with rule-based evaluation and concept matching.

Allow optional AI-based feedback for open-ended answers when needed.

Do not evaluate students solely on exact keyword matches, and do not
claim that automated feedback is always correct.

Give students the option to compare their explanation with a
teacher-reviewed model answer.

------------------------------------------------------------------------

## 13. MULTILINGUAL LEARNING

Begin with English and Kannada support, with the ability to add more
languages later.

Provide:

-   Language selection.
-   Bilingual explanations.
-   Subject-specific terminology.
-   Translated glossary entries.
-   Language-aware notes.
-   Explanations in a selected language.
-   Examination practice in the required language.

Allow a student to learn a concept in Kannada and then practise writing
the answer in English.

Use teacher-reviewed translations for important educational content
wherever possible.

Use optional machine translation only where appropriate and clearly
identify content that requires verification.

Keep language selection consistent across the dashboard, lesson pages,
and supported activities.

------------------------------------------------------------------------

## 14. EXAMINATION PREPARATION CENTRE

Create a separate section for examination preparation.

Include:

-   Chapter-wise question practice.
-   Topic-wise revision.
-   Previous examination questions when legitimately available.
-   Teacher-created model questions.
-   Timed mock tests.
-   Practice papers.
-   Formula sheets.
-   Important definitions.
-   Short-answer revision.
-   Long-answer preparation.
-   Mistake review.
-   Exam countdown.
-   Personalized revision schedules.

Allow teachers to organize questions by marks, topic, and difficulty.

Do not fabricate official previous-year questions.

Clearly label generated practice questions as practice questions rather
than authentic examination papers.

After each mock test, display:

-   Score.
-   Correct and incorrect responses.
-   Topic-level performance.
-   Time taken.
-   Mistake analysis.
-   Recommended revision topics.

Use the student's actual results to generate recommendations.

------------------------------------------------------------------------

## 15. GAMIFICATION AND MOTIVATION

Add optional, educationally meaningful gamification.

Include:

-   Learning points.
-   Topic mastery badges.
-   Revision streaks.
-   Milestones.
-   Personal progress goals.
-   Weekly learning targets.
-   Completion celebrations.

Reward consistent effort, revision, and improvement, not only high marks
or speed.

Do not publicly rank students by intelligence or academic weakness.

Avoid excessive animations, distracting notifications, and features that
encourage unhealthy competition.

Allow students to disable gamification.

------------------------------------------------------------------------

## 16. TEACHER DASHBOARD

Create a separate dashboard for teachers.

Display:

-   Number of students in each class.
-   Assignment completion.
-   Average assessment performance.
-   Subject-wise performance.
-   Topic-wise mastery.
-   Common mistakes.
-   Students requiring additional support.
-   Students ready for advanced practice.
-   Topics with high failure rates.
-   Learning progress over time.
-   Revision completion.
-   Class-level engagement and participation trends, interpreted
    cautiously and separately from academic mastery.
-   Students who may benefit from additional support, based on
    transparent indicators rather than permanent labels.
-   Assessment history.

### Teacher graphs

Include:

-   Class performance bar chart.
-   Subject-wise comparison chart.
-   Topic mastery chart.
-   Assessment performance trend.
-   Correct-versus-incorrect response chart.
-   Assignment completion chart.
-   Common misconception chart.
-   Class-level learning gap map.

Allow filtering by:

-   Class.
-   Subject.
-   Chapter.
-   Topic.
-   Assessment.
-   Date range.

### Teacher intervention recommendations

Provide explainable recommendations such as:

"Many students struggled with finding a common denominator. Consider
revisiting equivalent fractions."

Allow teachers to assign remedial practice or advanced exercises.

Ensure the dashboard helps teachers make decisions rather than replacing
teacher judgment.

Do not expose student records to unauthorized teachers or students.

------------------------------------------------------------------------

## 17. ADMINISTRATOR DASHBOARD

Create a functional administrative interface.

Include:

-   User management.
-   Teacher and student accounts.
-   Class management.
-   Subject management.
-   Chapter and topic management.
-   Content moderation.
-   Role and permission management.
-   System usage statistics.
-   Database health indicators.
-   Import and export options where appropriate.

Protect administrative actions using role-based permissions.

------------------------------------------------------------------------

## 18. GRAPHICAL REPRESENTATION AND VISUAL LEARNING

In addition to dashboard graphs, make educational content visual.

Support:

-   Concept diagrams.
-   Flowcharts.
-   Mind maps.
-   Timelines.
-   Mathematical graphs.
-   Science illustrations.
-   Labelled diagrams.
-   Process diagrams.
-   Comparison tables.
-   Topic dependency graphs.
-   Interactive question visualizations.

Examples:

Mathematics:

-   Function graphs.
-   Geometric diagrams.
-   Formula demonstrations.

Science:

-   Human body diagrams.
-   Chemical reaction representations.
-   Electricity circuit diagrams.
-   Scientific process illustrations.

Social Science:

-   Timelines.
-   Maps.
-   Historical comparisons.

Computer Science:

-   Flowcharts.
-   Algorithm visualizations.
-   Data structure diagrams.
-   Programming execution traces.

Use appropriate rendering libraries or verified educational assets.

Do not generate decorative images when an accurate diagram or functional
visualization is required.

------------------------------------------------------------------------

## 19. SEARCH, BOOKMARKS, AND STUDY ORGANIZATION

Provide a global search bar.

Students should be able to search:

-   Subjects.
-   Chapters.
-   Topics.
-   Definitions.
-   Formulas.
-   Notes.
-   Questions.
-   Bookmarked materials.

Include:

-   Saved notes.
-   Bookmarks.
-   Recently viewed lessons.
-   Personal study planner.
-   Daily study goals.
-   Revision checklist.
-   Downloadable study materials where permitted.

Search results should link directly to the relevant lesson or resource.

------------------------------------------------------------------------

## 20. OPTIONAL AI ASSISTANT WITH LIMITED USAGE

Include an optional learning assistant, but do not make the entire
application dependent on AI.

Use conventional algorithms and prepared educational content for most
activities.

The AI assistant may help with:

-   Explaining unfamiliar concepts in simpler language.
-   Answering selected open-ended doubts.
-   Providing alternative explanations.
-   Giving feedback on flexible written explanations.
-   Translating selected explanations.
-   Offering additional examples when the approved content library is
    insufficient.

### AI usage rules

1.  Search the approved learning content before calling AI.
2.  Use predefined hints and explanations whenever available.
3.  Avoid AI calls for score calculations, revision scheduling, basic
    feedback, or dashboard analytics.
4.  Allow students to request help explicitly.
5.  Limit repeated requests to prevent unnecessary usage.
6.  Do not generate a complete assignment answer when guided learning
    would better support the activity.
7.  Do not present uncertain answers as verified facts.
8.  Use curriculum and grade context when providing educational
    assistance.
9.  Keep API keys on the server, never in frontend code.
10. Provide a useful experience even when the AI service is unavailable.
11. Do not send unnecessary personal or sensitive student information to
    external AI services.
12. Track AI requests and errors without unnecessarily retaining
    sensitive conversation content.

AI should support learning rather than replace the student's effort.

------------------------------------------------------------------------

## 21. OFFLINE AND LOW-CONNECTIVITY SUPPORT

Where feasible, provide an offline-friendly learning experience.

Allow students to:

-   Access downloaded notes.
-   Read saved lessons.
-   Complete locally available practice questions.
-   Review previously downloaded flashcards.
-   Save activity results locally.
-   Synchronize progress when internet access returns.

Use suitable web technologies, such as a service worker and local
storage, where appropriate.

Explain which features require an internet connection.

Do not claim full offline functionality unless it has actually been
implemented and tested.

------------------------------------------------------------------------

## 22. USER INTERFACE AND DESIGN REQUIREMENTS

Build a polished, professional, accessible interface suitable for
students and teachers.

### Design style

Use:

-   A clean educational dashboard.
-   A consistent spacing system.
-   Readable typography.
-   Clear headings.
-   Well-organized cards.
-   Accessible colour contrast.
-   Responsive charts.
-   Simple icons.
-   Consistent buttons.
-   Clear loading indicators.
-   Helpful error messages.
-   Empty states for new users.

The interface should look modern without being visually overwhelming.

Use a restrained, consistent colour palette and meaningful status
colours.

### Layout

Provide:

-   Sidebar navigation on desktop.
-   Collapsible navigation where appropriate.
-   Mobile-friendly navigation.
-   Responsive content cards.
-   Clear dashboard sections.
-   Consistent lesson-page layouts.

### Navigation items

Student:

-   Dashboard
-   My Subjects
-   Study Notes
-   Learn
-   Practice
-   Smart Revision
-   Examination Preparation
-   Progress Analytics
-   Bookmarks
-   Study Planner
-   Profile
-   Settings

Teacher:

-   Dashboard
-   Classes
-   Students
-   Subjects
-   Content Library
-   Assignments
-   Assessments
-   Learning Analytics
-   Reports
-   Settings

Administrator:

-   Dashboard
-   Users
-   Classes
-   Subjects
-   Content Management
-   Permissions
-   System Settings

Make every visible button functional.

Avoid decorative buttons that do nothing.

Provide accessible labels and keyboard navigation.

------------------------------------------------------------------------

## 23. RECOMMENDED TECHNOLOGY STACK

Use a simple, maintainable architecture.

Frontend:

-   HTML5.
-   CSS3.
-   JavaScript.
-   A responsive component system where useful.

Backend:

-   Python.
-   Flask.

Database:

-   SQLite for the initial prototype.
-   A migration path to PostgreSQL when needed.

Charts:

-   Chart.js or another suitable charting library.

Mathematical content:

-   MathJax or KaTeX.

Educational visualizations:

-   SVG.
-   Canvas.
-   Appropriate diagramming or graph libraries.

Authentication:

-   Secure session-based authentication.
-   Password hashing.
-   Role-based authorization.

Optional AI:

-   A server-side integration with a suitable language-model API.

Use a clean separation between:

-   Frontend interface.
-   Backend routes.
-   Learning algorithms.
-   Database models.
-   Educational content.
-   Authentication.
-   Optional AI services.

Do not introduce unnecessary technologies merely to make the
architecture appear advanced.

------------------------------------------------------------------------

## 24. DATABASE DESIGN

Create a normalized, maintainable database.

Include suitable tables for:

1.  Users.
2.  Roles and permissions.
3.  Students.
4.  Teachers.
5.  Classes.
6.  Enrollments.
7.  Subjects.
8.  Chapters.
9.  Topics.
10. Topic prerequisites.
11. Learning materials.
12. Questions.
13. Answers.
14. Hints.
15. Common misconceptions.
16. Quiz attempts.
17. Assessment results.
18. Topic mastery.
19. Confidence ratings.
20. Revision schedules.
21. Bookmarks.
22. Study plans.
23. Assignments.
24. Assignment submissions.
25. Notifications.
26. Teacher feedback.
27. AI usage records.

Use appropriate primary keys, foreign keys, timestamps, and database
constraints.

Ensure that student progress is associated with the correct student and
topic.

Do not store passwords as plain text.

Use access controls to protect student records.

------------------------------------------------------------------------

## 25. SAMPLE CONTENT AND INITIAL DEMONSTRATION

The application must contain meaningful demonstration content so that it
can be tested immediately.

Initially prepare a manageable but complete set of lessons for a few
representative subjects, such as:

### School demonstration

-   Mathematics: Fractions and Linear Equations.
-   Science: Photosynthesis or Electricity.
-   English: Grammar and Sentence Structure.

### College demonstration

-   Programming in C: Variables, Conditions, and Loops.
-   Data Structures: Stacks and Queues.
-   Mathematics: Basic Probability.

For each selected topic, include:

-   Structured study notes.
-   Learning objectives.
-   Examples.
-   Questions.
-   Correct answers.
-   Hints.
-   Common misconceptions where relevant.
-   Revision cards.
-   A brief assessment.
-   Prerequisite relationships where appropriate.

Clearly identify demonstration content.

Make it easy to add more subjects and chapters through the teacher
interface.

Do not fill the entire application with fabricated scores or fake
student activity.

Use clearly labelled sample accounts and sample data only where
necessary for demonstration.

------------------------------------------------------------------------

## 26. TESTING AND VALIDATION

Test the complete application.

Verify:

-   User registration and login.
-   Role-based access.
-   Subject and topic navigation.
-   Study notes.
-   Quiz submissions.
-   Answer evaluation.
-   Mistake detection.
-   Hint progression.
-   Learning-path recommendations.
-   Confidence recording.
-   Topic mastery updates.
-   Revision scheduling.
-   Dashboard chart calculations.
-   Teacher analytics.
-   Search.
-   Bookmarks.
-   Mobile responsiveness.
-   Offline functionality where implemented.
-   AI failure handling.
-   Database persistence.
-   Unauthorized-access protection.

Test edge cases:

-   Empty dashboards.
-   New students without assessment history.
-   Incorrect answers.
-   Repeated attempts.
-   Missing lesson content.
-   Unavailable AI services.
-   Invalid input.
-   Interrupted connections.

Do not claim that testing has passed until it has actually been
performed.

------------------------------------------------------------------------

## 27. PROJECT DELIVERABLES

Produce a complete working project, not just a design description.

Provide:

1.  Complete source code.
2.  Organized project directory.
3.  Frontend implementation.
4.  Backend implementation.
5.  Database schema and initialization.
6.  Sample educational content.
7.  Student dashboard.
8.  Teacher dashboard.
9.  Administrator dashboard.
10. Functional charts and graphs.
11. Study notes and topic pages.
12. Adaptive learning engine.
13. Mistake Detective.
14. Hint Ladder.
15. Confidence tracker.
16. Learning Gap Map.
17. Smart Revision.
18. Examination Preparation Centre.
19. Authentication and permissions.
20. Configuration example.
21. Setup instructions.
22. Requirements file.
23. Database initialization instructions.
24. Testing instructions.
25. README documentation.

Include complete code for all implemented modules.

Do not replace critical functionality with pseudocode, unexplained
placeholders, or nonfunctional UI elements.

Clearly identify any features that remain incomplete.

------------------------------------------------------------------------

## 28. IMPLEMENTATION PRIORITIES

Develop the application in this order:

### Stage 1: Functional foundation

-   Authentication.
-   Role management.
-   Subject and chapter library.
-   Study notes.
-   Quiz system.
-   Student dashboard.
-   Database integration.

### Stage 2: Adaptive learning

-   Foundation, Standard, and Challenge modes.
-   Mistake Detective.
-   Hint Ladder.
-   Topic prerequisites.
-   Confidence tracker.
-   Topic-level mastery.

### Stage 3: Revision and analytics

-   Spaced revision.
-   Student progress charts.
-   Teacher dashboard.
-   Class-level analytics.
-   Examination preparation.

### Stage 4: Additional learning features

-   Teach-Back Mode.
-   English and Kannada support.
-   Bookmarks and study planner.
-   Offline-friendly lessons.
-   Advanced educational visualizations.

### Stage 5: Optional intelligence

-   AI-assisted explanations.
-   AI-assisted open-ended feedback.
-   Optional machine-learning recommendations when sufficient suitable
    data is available.

At each stage, ensure that the application runs correctly before adding
more functionality.

------------------------------------------------------------------------

## 29. FINAL ACCEPTANCE CRITERIA

The project is considered ready for demonstration only when the
following workflow works end to end:

1.  A student signs in.
2.  The student selects their education level, subject, and topic.
3.  The student accesses relevant study notes.
4.  The student completes a diagnostic quiz.
5.  The system recommends a learning path.
6.  The student completes a lesson and practice questions.
7.  The system identifies a supported misconception when an answer
    matches a known error pattern.
8.  The student receives a progressive hint.
9.  The system records quiz performance and confidence.
10. Topic mastery and revision recommendations update.
11. The student dashboard displays the updated data in charts and
    graphs.
12. The student can review difficult concepts and track improvement.
13. A teacher can inspect authorized class-level learning analytics.
14. The system continues to provide its core learning features when the
    optional AI service is unavailable.

All dashboards must display actual application data.

All charts must use real database records.

All implemented features must be connected to the backend.

The application must be understandable to students who have little
experience with educational technology.

The system must be usable on desktops, tablets, and mobile phones.

The final objective is to create a practical, accessible,
learning-focused educational platform that helps students become
independent learners while helping teachers provide more targeted
support.

**Begin by designing the database, application structure, and student
dashboard. Then implement the complete system incrementally, verifying
each major workflow before proceeding.**
