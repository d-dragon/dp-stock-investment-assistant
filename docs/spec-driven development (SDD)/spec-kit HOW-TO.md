

# Spec-Kit HOW-TO

This guide describes how to apply the Spec-Kit methodology for Spec-Driven Development (SDD) in the `dp-stock-investment-assistant` project, following best practices from the [Spec-Kit official documentation](https://github.com/github/spec-kit/blob/main/README.md) and [spec-driven development guide](https://github.com/github/spec-kit/blob/main/spec-driven.md).

---

## Table of Contents

- [Spec-Kit HOW-TO](#spec-kit-how-to)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
  - [Spec-Kit Workflow](#spec-kit-workflow)
    - [Step 1: Author a Specification](#step-1-author-a-specification)
    - [Step 2: Review and Approve](#step-2-review-and-approve)
    - [Step 3: Implement to Spec](#step-3-implement-to-spec)
    - [Step 4: Validate and Test](#step-4-validate-and-test)
    - [Step 5: Maintain and Evolve](#step-5-maintain-and-evolve)
  - [Extensions Guideline](#extensions-guideline)
    - [Installing Extensions](#installing-extensions)
    - [Using Extensions in This Project](#using-extensions-in-this-project)
    - [Best Practices for Extensions](#best-practices-for-extensions)
  - [Best Practices](#best-practices)
  - [Troubleshooting](#troubleshooting)
  - [References](#references)
  - [Additional Resources](#additional-resources)

---

## Overview

Spec-Kit enables a spec-first workflow, ensuring that features, APIs, and components are defined, reviewed, and versioned before implementation. This approach increases clarity, reduces ambiguity, and aligns code, tests, and documentation.

## Prerequisites

- Access to this repository and its documentation
- Familiarity with markdown and the project's [spec format](../specs/spec-template.md)
- [Spec-Kit CLI](https://github.com/github/spec-kit#cli) installed (optional but recommended)

## Spec-Kit Workflow

### Step 1: Author a Specification

- Create a new spec file under `docs/spec-driven development (SDD)/specs/` using the [spec template](../specs/spec-template.md).
- Clearly define the feature, API, or component, including purpose, requirements, and acceptance criteria.
- Use markdown for structure and clarity.

### Step 2: Review and Approve

- Submit the spec as a pull request.
- Request feedback from stakeholders, technical leads, and reviewers.
- Iterate on the spec until it is clear, complete, and approved.
- Optionally, use the Spec-Kit CLI to lint and validate the spec for completeness.

### Step 3: Implement to Spec

- Treat the approved spec as the single source of truth.
- Reference the spec in code comments and PR descriptions.
- Ensure all implementation work directly maps to the requirements and acceptance criteria in the spec.

### Step 4: Validate and Test

- Write tests that directly correspond to the spec's requirements.
- Use automated tools (including Spec-Kit CLI, if available) to check for compliance.
- Review the implementation against the spec before merging.

### Step 5: Maintain and Evolve

- Update specs as requirements change, following versioning best practices.
- Document changes in the spec file and keep code/tests in sync.
- Regularly review and refactor specs to reflect the current state of the system.


## Extensions Guideline

Spec-Kit supports extensions to enhance spec authoring, validation, and integration with other tools. Extensions can automate checks, add custom linting rules, or enable advanced workflows tailored to the `dp-stock-investment-assistant` project.

### Installing Extensions

- Review available extensions in the [Spec-Kit Extensions documentation](https://github.com/github/spec-kit/blob/main/extensions/README.md).
- See also the [Spec-Kit CLI Extensions User guide](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-USER-GUIDE.md) for installation and usage details.
- Install extensions globally or in your project environment using the Spec-Kit CLI. For example:
    ```sh
    spec-kit extension install <extension-name>
    ```
- List installed extensions with:
    ```sh
    spec-kit extension list
    ```

### Using Extensions in This Project

- Extensions can be configured in a `.spec-kitrc` or `spec-kit.config.js` file at the project root.
- Recommended extensions for this project may include:
    - **spec-kit-lint**: Enforces spec formatting and style.
    - **spec-kit-validate-links**: Checks for broken links in specs and documentation.
    - **spec-kit-schema**: Validates specs against custom schemas (useful for API or data model specs).
- To enable an extension, add it to your config file and follow any project-specific setup instructions.

### Best Practices for Extensions

- Use extensions to automate repetitive checks and maintain spec quality.
- Document any required or recommended extensions in the project README or this guide.
- Keep extensions up to date to benefit from improvements and security updates.
- Refer to the [official extensions guide](https://github.com/github/spec-kit/blob/main/extensions/README.md) and [CLI Extensions Guide](https://github.com/github/spec-kit/blob/main/docs/extensions.md) for advanced usage and troubleshooting.

---

**Related updates:**  
- Add any required extensions to your local setup and document them in the project’s onboarding or README.
- When introducing new extensions, communicate their purpose and usage to the team.

    - **spec-kit-lint**: Enforces spec formatting and style.
    - **spec-kit-validate-links**: Checks for broken links in specs and documentation.
    - **spec-kit-schema**: Validates specs against custom schemas (useful for API or data model specs).
- To enable an extension, add it to your config file and follow any project-specific setup instructions.


## Best Practices

- Keep specs concise, unambiguous, and versioned.
- Link related specs, code, and documentation.
- Use diagrams, tables, or examples for complex logic.
- Regularly audit code and tests for alignment with specs.
- Use the Spec-Kit CLI for validation and linting where possible.

## Troubleshooting

- **Spec drift**: Periodically compare code/tests to specs and resolve discrepancies.
- **Ambiguity**: Clarify unclear requirements with stakeholders before implementation.
- **Outdated specs**: Promptly update and version specs as requirements evolve.

## References

- [Spec Template](../specs/spec-template.md)
- [Project Architecture](../../.github/instructions/architecture.instructions.md)
- [Testing Guidelines](../../.github/instructions/testing.instructions.md)
- [Spec-Kit README](https://github.com/github/spec-kit/blob/main/README.md)
- [Spec-Driven Development Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Spec-Kit Extensions](https://github.com/github/spec-kit/blob/main/extensions/README.md)

## Additional Resources

- [Spec-Kit Official Repository](https://github.com/github/spec-kit)
- [Spec-Kit CLI Usage](https://github.com/github/spec-kit#cli)
- [Spec-Kit Documentation](https://github.com/github/spec-kit#readme)

For advanced usage, configuration, and community support, refer to the [Spec-Kit official documentation](https://github.com/github/spec-kit/blob/main/README.md) and [spec-driven development guide](https://github.com/github/spec-kit/blob/main/spec-driven.md).