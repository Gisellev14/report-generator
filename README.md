# GitHub Repo Contribution Report Generator

A powerful tool to analyze GitHub repository contributions including commits, pull requests, code reviews, and more. Generate comprehensive monthly reports with metrics like PR lead time, cycle time, and initiative tracking.

## Features

- **Comprehensive Metrics**: Track PRs, commits, code reviews, and more
- **Initiative Tracking**: Map work to initiatives using branch name patterns
- **Performance Analytics**: Measure lead time, cycle time, and review metrics
- **Flexible Reporting**: Generate reports in JSON, YAML, or console-friendly formats
- **Private Repo Support**: Works with both public and private repositories

## Important notes

- This tool is currently intended for academic purposes and it's capabilities are limited to accessing public repositories.
- Authenticated access is wired but for these purposes haven't been tested.
- As for the project scope, it's currently limited to generate reports for the whole repository.

## TODO

- Test access to private repositories.
- Add filter for contributors.
- Add 'reset' button so EM (Engineering Managers) can reset the report and generate a new one per contributor without having to close and open the application.
- By now these steps are just a reminder for me, as the project is not only intended for this course but also as a deliverable for my company.
- Any additional feature or change would be later evaluated with my manager.
- Evaluate if unit and component tests are needed - as wasn't required for this course I didn't implement them.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Gisellev14/report-generator.git
   cd github-report-generator
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your GitHub token (optional but recommended):
   ```bash
   cp .env.example .env
   # Edit .env and add your GitHub token
   ```

## Usage

### Basic Usage (CLI)

```bash
.venv/bin/python -m github_report_generator.application.cli owner/repo
```

### GUI Mode

```bash
.venv/bin/python -m github_report_generator.application.cli
```

### Configuration

The tool supports several configuration files:

#### 1. Initiative Patterns

Customize initiative patterns in `github_report_generator/config/initiatives.yaml`:

```yaml
# Default patterns
Features: "^feature/|^feat/"
Bug Fixes: "^fix/|^bugfix/|^hotfix/"
Documentation: "^docs/|^documentation/"
Testing: "^test/|^testing/"
Refactoring: "^refactor/"
Dependencies: "^deps/|^dependencies/"
CI/CD: "^ci/|^cd/"
Performance: "^perf/"
Security: "^security/"
UI/UX: "^ui/|^ux/"

# Custom patterns
Mobile: "^mobile/|^ios/|^android/"
Backend: "^backend/|^server/"
Frontend: "^frontend/|^client/"
```

See `github_report_generator/config/README.md` for detailed pattern configuration.

#### 2. GitHub Configuration

Create a `.github_report_config.yaml` file in your project root:

```yaml
# GitHub settings
github:
  token: ${GITHUB_TOKEN} # Use environment variable
  timezone: "America/New_York"
  api_url: "https://api.github.com" # For GitHub Enterprise

# Report settings
report:
  title: "Monthly Development Report"
  format: "html" # html or json
  output_dir: "./reports"

# Analysis settings
analysis:
  min_pr_size: 10 # Minimum changes for size calculation
  max_pr_size: 1000 # Maximum changes before marking as XL
  review_timeout: 48 # Hours before marking review as delayed
```

#### 3. GUI Configuration

GUI preferences are stored in `.github_report_gui.json`:

```json
{
  "repo": "owner/repo",
  "days": 30,
  "use_mock": false,
  "window": {
    "width": 1200,
    "height": 800
  },
  "charts": {
    "theme": "light",
    "colors": ["#4e79a7", "#f28e2c", "#e15759"]
  }
}
```

## Report Metrics

Each report includes:

- **PR Statistics**: Total, merged, open, and closed PRs
- **Contributor Activity**: PRs authored, reviews given/received
- **Performance Metrics**: Lead time, cycle time, review time
- **Initiative Breakdown**: Work categorized by branch patterns
- **Code Analysis**: Language distribution, file changes
- **Highlights**: Key insights and trends

## Authentication

For private repositories or higher rate limits, set up a GitHub Personal Access Token:

1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` scope
3. Set it in your environment or `.env` file as `GITHUB_TOKEN=your_token_here`

### Project Structure

This project follows an Hexagonal Architecture pattern aiming to separate concerns and make the codebase more maintainable and testable.
For reference on Hexagonal Architecture see [this](https://vaadin.com/blog/ddd-part-3-domain-driven-design-and-the-hexagonal-architecture).

The project is structured as follows:

```
github_report_generator/
  ├── __init__.py
  ├── application/
  │   ├── __init__.py
  │   ├── api.py
  │   ├── cli.py
  │   ├── formatters/
  │   ├── gui/
  │   │   ├── __init__.py
  │   │   ├── chart_updater.py
  │   │   ├── gui.py
  │   │   ├── gui_utils.py
  │   │   ├── input_validator.py
  │   │   ├── metrics_updater.py
  │   │   ├── tab_manager.py
  │   │   └── window_manager.py
  │   ├── services/
  │   └── utils/
  ├── config/
  │   ├── README.md
  │   └── initiatives.yaml
  ├── domain/
  │   ├── __init__.py
  │   ├── management/
  │   │   ├── __init__.py
  │   │   ├── chart_manager.py
  │   │   ├── config_manager.py
  │   │   ├── event_manager.py
  │   │   ├── metrics_manager.py
  │   │   ├── progress_manager.py
  │   │   └── report_manager.py
  │   ├── model/
  │   │   ├── __init__.py
  │   │   └── models.py
  │   └── service/
  │       ├── __init__.py
  │       ├── report_generator.py
  │       └── velocity.py
  ├── infrastructure/
  │   ├── __init__.py
  │   ├── error/
  │   │   ├── __init__.py
  │   │   └── error_handler.py
  │   ├── github/
  │   │   ├── __init__.py
  │   │   ├── github_client.py
  │   │   └── github_decorators.py
  │   └── visualization/
  │       ├── __init__.py
  │       └── visualizations.py
```
