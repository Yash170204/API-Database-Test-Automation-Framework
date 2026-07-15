# Screenshot Strategy & Capture Guide

To make this framework look highly professional and ready for recruiters, we recommend capturing five key screenshots of the framework's execution. These images will be displayed in the `README.md` to instantly showcase the framework's features.

Follow the instructions below to capture each screenshot, crop out any personal identifiers (like local user directory paths or local usernames), and save them in the `screenshots/` directory.

---

### 1. Full Automated Test Suite Passing
* **Purpose**: Demonstrates that the entire framework compiles, starts the server, executes the complete suite, and passes.
* **How to Capture**:
  1. Open a terminal (PowerShell, Command Prompt, or terminal of choice) and navigate to the project directory.
  2. Run the command:
     ```bash
     pytest -v
     ```
  3. Capture the terminal screen showing the summary section where all 30 tests pass.
* **Filename**: `test-suite-passed.png`
* **Target Location**: `screenshots/test-suite-passed.png`
* **Markdown Reference**: Used in `README.md` under the **Screenshots / Demo** section.

---

### 2. API Test Execution
* **Purpose**: Demonstrates running only functional API tests using Pytest markers.
* **How to Capture**:
  1. In the terminal, run the command:
     ```bash
     pytest -m api -v
     ```
  2. Capture the output showing only the product and order API tests running and passing.
* **Filename**: `api-tests.png`
* **Target Location**: `screenshots/api-tests.png`
* **Markdown Reference**: Used in `README.md` under the **Screenshots / Demo** section.

---

### 3. Database Validation Tests
* **Purpose**: Demonstrates running direct database tests using SQL validation.
* **How to Capture**:
  1. In the terminal, run the command:
     ```bash
     pytest -m database -v
     ```
  2. Capture the output showing only the database constraint and schema tests running and passing.
* **Filename**: `database-tests.png`
* **Target Location**: `screenshots/database-tests.png`
* **Markdown Reference**: Used in `README.md` under the **Screenshots / Demo** section.

---

### 4. Interactive HTML Test Report
* **Purpose**: Showcases professional HTML-based QA test reporting.
* **How to Capture**:
  1. Run the command to generate the HTML report:
     ```bash
     pytest -v --html=reports/report.html --self-contained-html
     ```
  2. Open `reports/report.html` in your web browser.
  3. Expand some test cases to show details, and take a screenshot of the browser dashboard showing the pie chart/summaries.
* **Filename**: `test-report.png`
* **Target Location**: `screenshots/test-report.png`
* **Markdown Reference**: Used in `README.md` under the **Screenshots / Demo** section.

---

### 5. GitHub Actions Successful Workflow
* **Purpose**: Proves that the framework runs continuously in a CI/CD environment.
* **How to Capture**:
  1. Commit and push the repository to GitHub.
  2. Navigate to your repository page on GitHub and click the **Actions** tab.
  3. Select the **Automated Test Suite** workflow and click on a successful green run.
  4. Capture the screen showing the successful run, green checkmarks on steps, and the uploaded `test-execution-report` artifact.
* **Filename**: `github-actions-success.png`
* **Target Location**: `screenshots/github-actions-success.png`
* **Markdown Reference**: Used in `README.md` under the **Screenshots / Demo** section.

---

> [!WARNING]
> **Privacy Reminder**
> Before saving any screenshot, verify that it does not show any:
> - Private API keys or environment passwords.
> - Private computer path details (e.g. `C:\Users\yashk\...)`. If necessary, crop the terminal window to hide terminal path prompts.
