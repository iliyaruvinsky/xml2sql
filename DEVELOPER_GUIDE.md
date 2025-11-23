# 🛠️ Developer Guide

> **Welcome, Developers!** This guide will help you set up, use, and extend the XML to SQL converter tool.

---

## 👋 Who This Is For

- **Developers** who want to use the converter tool to convert XML files
- **Contributors** who want to extend or modify the codebase
- **Technical users** who need to understand the architecture and internals

---

## ⏱️ What You'll Accomplish

By following this guide, you will:
1. Set up the development environment
2. Learn how to use the converter tool
3. Understand the codebase architecture
4. Run tests and verify functionality
5. Extend the tool with new features

**Estimated Time:** 15-30 minutes for initial setup

---

## 📖 Step-by-Step Reading Path

Follow these steps in order to get started as a developer.

### ✅ Step 1: Quick Setup (5 minutes)

**File:** [QUICK_START.md](QUICK_START.md)

**What you'll learn:**
- How to install dependencies
- How to run tests
- How to convert your first XML file
- Basic CLI usage

**Action:** Open `QUICK_START.md` and follow the 5-minute test.

---

### ✅ Step 2: Understand the Architecture (10-15 minutes)

**Files:** Technical documentation in `docs/`

**What you'll learn:**
- Intermediate Representation (IR) design
- Conversion pipeline architecture
- How XML parsing works
- How SQL generation works

**Action:** Read these documents in order:
1. [docs/ir_design.md](docs/ir_design.md) - Understand the data structures
2. [docs/CONVERSION_FLOW_MAP.md](docs/CONVERSION_FLOW_MAP.md) - Understand the pipeline and flow

---

### ✅ Step 3: Testing and Verification (10-15 minutes)

**File:** [docs/TESTING.md](docs/TESTING.md)

**What you'll learn:**
- How to run unit tests
- How to run integration tests
- How to test specific scenarios
- How to verify output quality

**Action:** Open `docs/TESTING.md` and follow the testing procedures.

---

### ✅ Step 4: Extend the Tool (As Needed)

**Files:** Code in `src/xml_to_sql/` and documentation in `docs/`

**What you'll learn:**
- How to add new node types
- How to extend function translation
- How to add new features
- Code structure and conventions

**Action:** Explore the codebase and refer to technical documentation.

---

## 📚 Document Index

Here's what each developer document contains and when to read it:

### Essential Documents (Read These)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **DEVELOPER_GUIDE.md** (this file) | Navigation guide for developers | **First!** You're reading it now. |
| **QUICK_START.md** | Quick setup and first conversion | Step 1 - Get up and running in 5 minutes |
| **README.md** | Project overview and features | Understand what the tool does |
| **docs/TESTING.md** | Testing procedures | Step 3 - Verify everything works |

### Technical Documentation (Read When Needed)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **docs/ir_design.md** | Intermediate Representation design | When you need to understand data structures |
| **docs/CONVERSION_FLOW_MAP.md** | Conversion pipeline architecture and flow | When you need to understand the pipeline and flow |
| **docs/llm_handover.md** | Project status and handover | When you need project context |

### Code Structure

| Location | Purpose |
|----------|---------|
| **src/xml_to_sql/** | Main source code |
| **src/xml_to_sql/parser/** | XML parsing logic |
| **src/xml_to_sql/sql/** | SQL generation logic |
| **src/xml_to_sql/cli/** | Command-line interface |
| **src/xml_to_sql/config/** | Configuration management |
| **src/xml_to_sql/domain/** | Intermediate Representation models |
| **tests/** | Unit and integration tests |

---

## 🔗 Quick Links

### Most Important Documents

- 🚀 **[QUICK_START.md](QUICK_START.md)** - Start here for quick setup
- 📗 **[README.md](README.md)** - Project overview
- 🧪 **[docs/TESTING.md](docs/TESTING.md)** - Testing procedures
- 📁 **[docs/](docs/)** - Technical documentation

### Common Tasks

- **I want to convert XML files** → Read [QUICK_START.md](QUICK_START.md)
- **I want to run tests** → See [docs/TESTING.md](docs/TESTING.md)
- **I want to understand the architecture** → Read [docs/CONVERSION_FLOW_MAP.md](docs/CONVERSION_FLOW_MAP.md)
- **I want to extend the tool** → Explore `src/xml_to_sql/` and technical docs
- **I want to understand data structures** → Read [docs/ir_design.md](docs/ir_design.md)

---

## 🆘 Getting Help

### If You Get Stuck

1. **Check the Troubleshooting Section** in [README.md](README.md)
2. **Review Technical Documentation** - Most architecture questions are covered in `docs/`
3. **Check Test Files** - Tests in `tests/` show how to use the APIs
4. **Contact Support** - Provide the following information:
   - Which step you're on
   - What error message you see (if any)
   - Your environment details (Python version, OS)
   - Relevant code snippets (if applicable)

### What Information to Provide When Asking for Help

- The document you were following
- The step number where you encountered the issue
- The exact error message (copy/paste if possible)
- Your Python version and OS
- Relevant code or configuration

---

## ✅ Quick Checklist

Before you start, make sure you have:

- [ ] Python 3.11 or higher installed
- [ ] Git installed (for cloning the repository)
- [ ] A code editor (VS Code, PyCharm, etc.)
- [ ] About 15-30 minutes of time

---

## 🎯 Next Steps

**Ready to begin?** Follow the reading path above:

1. **First:** Read [QUICK_START.md](QUICK_START.md) (5 minutes)
2. **Then:** Explore [docs/](docs/) for technical details (10-15 minutes)
3. **Finally:** Start coding or converting!

---

## 📝 Notes

### For Contributors

- Follow the code structure in `src/xml_to_sql/`
- Add tests for new functionality in `tests/`
- Update documentation when adding features
- Follow Python best practices and type hints

### For Users

- If you just want to convert XML files, [QUICK_START.md](QUICK_START.md) is all you need
- If you want to understand how it works, read the technical docs in `docs/`
- If you want to modify the code, start with the architecture docs

---

**Happy coding! 🚀**

