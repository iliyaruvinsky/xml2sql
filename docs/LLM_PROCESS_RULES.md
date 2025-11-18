# LLM Process Rules

**Purpose**: Critical process guidelines for LLM agents working on this project.

**Last Updated**: 2025-11-18

---

## RULE #1: ALWAYS SEARCH PROJECT CONTEXT BEFORE WEB SEARCH

**Priority**: CRITICAL ⚠️

**Rule**: Before performing ANY web search for technical information, **ALWAYS** search the project documentation first.

**Why**: This project has extensive documentation based on actual HANA testing. Web search results may provide incorrect information that contradicts tested reality.

**Process**:
1. ✅ Search project docs: `docs/bugs/`, `docs/rules/`, `llm_handover.md`
2. ✅ Search codebase for existing implementations
3. ✅ Check git history for related changes
4. ❌ Only THEN consider web search if information is not found
5. ✅ If web search is used, **ALWAYS** validate findings against actual HANA execution before implementation

**Real Example of Correct Process** (2025-11-18):
- **What happened**: BUG-019 required CREATE OR REPLACE VIEW for HANA views
- **Correct process**: Searched project docs, found BUG-019-FIX-SUMMARY.md showed CREATE OR REPLACE VIEW validated at 39ms
- **Result**: Implementation matched tested reality, HANA execution succeeded
- **Lesson**: Project documentation reflects TESTED reality from HANA Studio validation.

---

## RULE #2: NEVER CHANGE WORKING CODE BASED ON ASSUMPTIONS

**Priority**: CRITICAL ⚠️

**Rule**: Never modify working code based on assumptions, web searches, or "best practices" without explicit user approval or actual test validation.

**Why**: "Better" solutions may not work in the actual environment.

**Process**:
1. ✅ If code is working, document why you think it should change
2. ✅ Ask user before making changes
3. ✅ Test thoroughly after changes
4. ❌ Never assume "modern" syntax works without testing

**Real Example of Tested Reality** (2025-11-18):
- **What happened**: BUG-019 fix included CREATE OR REPLACE VIEW for HANA views
- **Validation**: User tested in HANA Studio, confirmed 39ms execution success
- **Documentation**: BUG-019-FIX-SUMMARY.md documents the validated solution
- **Result**: CREATE OR REPLACE VIEW is the CORRECT approach for this project

---

## RULE #3: CROSS-CHECK DOCUMENTATION FOR SIMILAR ERRORS

**Priority**: HIGH

**Rule**: When encountering errors, check `docs/bugs/SOLVED_BUGS.md` and `docs/rules/HANA_CONVERSION_RULES.md` for similar patterns before implementing fixes.

**Source**: User feedback: "check in the bugs and rules maps, maybe similar error was documented. I'd recommend you always cross check the errors this way"

**Why**: Prevents re-inventing solutions, maintains consistency, learns from past fixes.

**Process**:
1. ✅ Search SOLVED_BUGS.md for similar error messages
2. ✅ Search HANA_CONVERSION_RULES.md for related patterns
3. ✅ Check git history for files related to the error
4. ✅ Only implement new solutions if no precedent exists

---

## RULE #4: USER HANA TESTING IS SOURCE OF TRUTH

**Priority**: CRITICAL ⚠️

**Rule**: User's actual HANA Studio execution results are the ONLY source of truth for what works and what doesn't.

**Why**: Documentation, web searches, and theoretical knowledge may be outdated or incorrect.

**Process**:
1. ✅ Implement fix based on project patterns
2. ✅ User tests in HANA Studio
3. ✅ If error occurs, fix based on ACTUAL error message
4. ✅ Document fix with HANA execution results
5. ❌ Never argue with HANA execution results

---

## RULE #5: DOCUMENT FAILURES AS THOROUGHLY AS SUCCESSES

**Priority**: HIGH

**Rule**: When mistakes happen, document them comprehensively to prevent repetition.

**Process**:
1. ✅ Document what was changed
2. ✅ Document why it was changed (including source: web search, assumption, etc.)
3. ✅ Document what broke
4. ✅ Document the fix
5. ✅ Document the lesson learned

**Example**:
- See BUG-019 CREATE OR REPLACE VIEW mistake (this document, Rule #1)

---

## RULE #6: INCREMENTAL CHANGES, FREQUENT VALIDATION

**Priority**: MEDIUM

**Rule**: Make small, incremental changes and validate each step.

**Why**: Large changes make debugging difficult when errors occur.

**Process**:
1. ✅ Make minimal change to fix one specific issue
2. ✅ Test in HANA Studio
3. ✅ Document result
4. ✅ Repeat for next issue

**Anti-pattern**: Making 5 changes at once, then debugging which one broke things.

---

## Compliance Checklist

Before making ANY code change, verify:

- [ ] Searched project documentation first?
- [ ] Found precedent in SOLVED_BUGS.md or HANA_CONVERSION_RULES.md?
- [ ] User explicitly approved this change OR it's fixing a tested error?
- [ ] Change is minimal and targets one specific issue?
- [ ] Ready to document this change comprehensively?

If ANY checkbox is unchecked, **STOP** and reconsider.

---

**Last Updated**: 2025-11-18 (after CREATE OR REPLACE VIEW incident)
