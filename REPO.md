# Tasks
1. Unpack the project MLForensics.zip. (1%)
2. Put the names and emails of your teammate in this spreadsheet (1%)
3. Upload project as a GitHub repo on github.com. Format of the repo name is TEAMNAME-FALL2024-SQA (1%)
4. In your project repo create README.md listing your team name and team members. (2%)
5. Apply the following activities related to software quality assurance:
- 5.a. Create a Git Hook that will run and report all security weaknesses in the project in a CSV file whenever a Python file is changed and committed. (20%)
- 5.b. Create a fuzz.py file that will automatically fuzz 5 Python methods of your choice. Report any bugs you discovered by the fuzz.py file. fuzz.py will be automatically executed from GitHub actions. (20%)
- 5.c. Integrate forensics by modifying 5 Python methods of your choice. (20%)
- 5.d. Integrate continuous integration with GitHub Actions. (20%)
6. Report your activities and lessons learned. Put the report in your repo as REPO.md (15%)

### Deliverables
A repo hosted on GitHub. Name of the repo will be TEAMNAME-FALL2024-SQA
Full completion of all activities as recorded on the GitHub repository
Report describing what activities your performed and what you have learned
Logs and screenshots that show execution of forensics, fuzzing, and static analysis

----

# Report
### Project Objective
The objective of this project is to integrate software quality assurance activities into an existing Python project "MLForensics". Whatever we learned from our workshops will be integrated in the project.

### Task 1-4
We successfully unpacked the project and have set up a shared GitHub repository. The link to the repository is available in the shared signup sheet under the name "Defect Hunters". Additionally, a README.md file is included, which contains our team name and a list of team members.

### Task 5
#### 5.a. Git Hook
A pre-commit Git hook was implemented as a security step to automatically review Python files staged for commit, flagging potential security vulnerabilities. The hook utilizes static analysis with the Bandit tool to identify issues. The result is printed in a file named [bandit-report.csv](5a_hooks/bandit-report.csv).

Usually, the pre-commit hook is not part of the Git history. For this reason, we have also coppied the [pre-commit](5a_hooks/pre-commit) Git hook file from '.git/hooks/' into '5a_hooks/'. Users need to ensure that Bandit is installed.

In the following image, you can see that the Git hook works with Bandit:
![Commit Command](5a_hooks/5a_pre-commit_with_bandit_0.png)

Here is the generated report: [bandit-report.csv](5a_hooks/bandit-report.csv)
![Commit Command](5a_hooks/5a_pre-commit_result.png)

#### 5.b. Fuzz
Report describing activities.
Logs and screenshots that show execution of fuzzing.

#### 5.c. Forensics
Files altered:
[git.repo.miner.py](MLForensics/MLForensics-farzana/mining/git.repo.miner.py)

Functions Altered:
deleteRepo: Added logging for deletion and errors.
makeChunks: Integrated logging for chunk operations.
cloneRepo: Replaced print statements with logging.
dumpContentIntoFile: Enhanced with logging and error handling.
getPythonCount: Added logging for file counts.

#### 5.d. Continuous Integration
Github Actions were utilized along with the Codacy static analysis tools to help with continuous integration and maintaining code quality. Utilizing a .yml file in the .github/workflows/ directory, we were able to add Codacy to scan through the source code.

As you can see here, Codacy ran completely and exited without error.
![Commit Command](5d_github_actions/codacy_overview.png)

![Commit Command](5d_github_actions/codacy_beginning_logs.png)

Finally, Codacy gives an overall metric of what kind of errors, issues, or warnings there are with the code to ensure that security measures are correctly implemented, as you can see here.
![Commit Command](5d_github_actions/codacy_ending_metrics_summary.png)

### 6. Final Report
=> Report about what activities we have performed and what we have learned.

In Task 5a, we implemented a pre-commit Git hook, demonstrating how straightforward it is to add hooks that enhance code quality. For instance, we used static code analysis to automatically test changes before they are committed, reducing the risk of unknowingly introducing bugs. This approach ensures a higher quality standard for the main/master branch.

In Task 5d, we implemented the Codacy static analysis tool in combination with Github Actions to scan our codebase whenever anything is pushed to our main branch. By implementing this, we are ensuring that our code quality is higher and there are fewer bugs and security issues within our codebase everytime anything is changed. When doing this specific project I learned more syntax with Github Actions and Codacy by implementing it to only scan the source directory.
