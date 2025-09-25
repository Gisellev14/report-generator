# Configuration Files

This directory contains configuration files for the GitHub Report Generator.

## Initiative Patterns (`initiatives.yaml`)

The `initiatives.yaml` file defines patterns for categorizing pull requests into initiatives based on their branch names. Each pattern is a regular expression that matches branch names.

### Format
```yaml
initiative_name: pattern
```

### Default Patterns
- `Features`: `^feature/|^feat/` - Feature branches
- `Bug Fixes`: `^fix/|^bugfix/|^hotfix/` - Bug fixes and hotfixes
- `Documentation`: `^docs/|^documentation/` - Documentation updates
- `Testing`: `^test/|^testing/` - Test additions or improvements
- `Refactoring`: `^refactor/` - Code refactoring
- `Dependencies`: `^deps/|^dependencies/` - Dependency updates
- `CI/CD`: `^ci/|^cd/` - CI/CD pipeline changes
- `Performance`: `^perf/` - Performance improvements
- `Security`: `^security/` - Security fixes
- `UI/UX`: `^ui/|^ux/` - User interface changes
- `Analytics`: `^analytics/` - Analytics features
- `API`: `^api/` - API changes
- `Infrastructure`: `^infra/` - Infrastructure changes
- `Configuration`: `^config/` - Configuration changes
- `Tooling`: `^tools/|^tooling/` - Development tools
- `Maintenance`: `^chore/|^maint/` - General maintenance
- `Experiments`: `^exp/|^experimental/` - Experimental features

### Custom Patterns
You can customize these patterns by editing the `initiatives.yaml` file. Each pattern is a regular expression that will be matched against branch names in a case-insensitive manner.

Example custom pattern:
```yaml
Mobile Features: '^mobile/|^ios/|^android/'
Backend: '^backend/|^server/'
Frontend: '^frontend/|^client/'
```

### Pattern Matching
- Patterns are matched using Python's `re.match` in case-insensitive mode
- Multiple patterns can match the same branch name
- The first part of the branch name (before the first `/`) is typically used for categorization
- Patterns should start with `^` to match from the beginning of the branch name

### Metrics
For each initiative, the report generator tracks:
- Number of PRs
- Contributors and their contributions
- Average lead time (time from first commit to merge)
- Average cycle time (time from PR creation to merge)

### Best Practices
1. Keep patterns simple and clear
2. Use descriptive initiative names
3. Avoid overlapping patterns unless intended
4. Consider your team's branching strategy
5. Update patterns as your workflow evolves
