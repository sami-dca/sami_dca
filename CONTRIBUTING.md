# Contributing to the project

First off, thanks for taking the time to contribute !

The project is open to contributions from everyone !

The following is a set of guidelines for contributing to the Sami project,
which is hosted on [Github](https://github.com/sami-dca).
These are mostly guidelines, not rules.
Use your best judgment, and feel free to propose changes to this document in a pull request.

# Table of contents

[I don't want to read this whole thing I just have a question!!!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)
[What should I know before I get started ?](#what-should-i-know-before-i-get-started-)
&emsp;[Sami and its ecosystem](#sami-and-its-ecosystem)
[How can I contribute ?](#how-can-i-contribute-)
&emsp;[Reporting bugs](#reporting-bugs)
&emsp;&emsp;[Before submitting a bug report](#before-submitting-a-bug-report)
&emsp;&emsp;[How do I submit a (good) bug report ?](#how-do-i-submit-a-good-bug-report-)
&emsp;[Suggesting enhancements](#suggesting-enhancements)

# I don't want to read this whole thing I just have a question!!!

> Note: Please don't file a GitHub issue to ask a question.
> You'll get faster results by using the resources below.

We have two main channels to answer all your questions:

- The [Sami FAQ](./FAQ.md)

# What should I know before I get started ?

## Sami and its ecosystem

The Sami project is made of different repositories:
- [sami/sami](https://github.com/sami-dca/sami_dca) - The actual Sami application, implemented in Python
- [sami/sami.github.io](https://github.com/sami-dca/sami-dca.github.io) - The Sami website source.

They are all hosted in the [Sami Organization on Github](https://github.com/sami-dca).

# How can I contribute ?

## Reporting bugs

This section will guide you through submitting a bug report for Sami.
Following these guidelines helps maintainers understand your issue and
reproduce the behavior.

> Note: If you find a Closed issue describing a similar problem you're experiencing,
> open a new issue and include a link to the one you found.

### Before submitting a bug report

Check the [FAQ](./FAQ.md) and the [issues section](https://github.com/sami-dca/sami/issues).
You might be able to find the cause of the problem and fix things yourself.
Most importantly, check if you can reproduce the problem in the latest version of Sami,
and if you can get the desired behavior by changing the client settings.

### How do I submit a (good) bug report ?

Bugs are tracked as GitHub issues.

Explain the problem and include additional details to help maintainers reproduce the problem:
- **Use a clear and descriptive title** for the issue
- **Describe the exact steps to reproduce the problem** in as many details as possible
- **Describe the behavior you observed after following the steps**
  and point out what exactly is the problem with that behavior
- **Explain which behavior you expected to see instead**
- **Include screenshots and animated GIFs** which show you
  following the described steps and clearly demonstrate the problem
  To record GIFs, you can use [this tool](https://www.cockos.com/licecap/) on macOS and Windows,
  and [this tool](https://github.com/colinkeenan/silentcast) on Linux
- **If you're reporting that Sami crashed**, include a crash report
- **If the problem is related to performance or memory**, include a CPU profile capture with your report
- **If the problem wasn't triggered by a specific action**,
  describe what you were doing before the problem happened and share more information using the guidelines below

Provide context by answering these questions:

- **Did the problem started happening recently** (e.g. after updating to a new version of Sami)
  or was this always a problem?
- **If the problem started happening recently**,
  can you reproduce the problem in an older version of Sami?
  What's the most recent version in which the problem doesn't happen?
  You can download older versions of Sami from the [releases page](https://github.com/sami-dca/sami_dca/releases).
- **Can you reliably reproduce the issue?**
  If not, provide details about how often the problem happens and under which conditions it normally happens

Include details about your configuration and environment:

- **Which version of Sami are you using?**
  You can get the exact version by running ``sami -v`` in your terminal,
  or by starting Sami and going in the ``About`` section
- **What's the name and version of the OS you're using?**
- **Are you running Sami in a virtual machine?**
  If so, which VM software are you using and which operating systems and versions are used for the host and the guest?
- **Include your Sami configuration file**

## Suggesting enhancements

This section guides you through submitting an enhancement suggestion for Sami,
from minor improvements to completely new features.
Following these guidelines helps maintainers and the community understand your suggestion.

### Before submitting an enhancement suggestion

Before creating enhancement suggestions, please check the
[issues section](https://github.com/sami-dca/sami/issues?q=is%3Aopen+label%3Aenhancement+label%3Anew%20feature)
which are tagged as ``new feature`` and ``enhancement`` as you might find out that this enhancement was already submitted.
When you are creating an enhancement suggestion, please include as many details as possible.

Also, check the improvement was not already implemented in more recent versions of Sami.

### How do I submit a (good) enhancement suggestion?

Enhancement suggestions are tracked as GitHub issues.

Explain what is the enhancement / feature and how you imagine it:
- **Use a clear and descriptive title** for the issue
- **Provide a description of the suggested enhancement** in as many details as possible
- **Provide specific examples to demonstrate the steps**
  Include copy/pasteable snippets which you use in those examples - put these in
  [Markdown code blocks](https://www.tutorialsandyou.com/markdown/how-to-write-code-blocks-in-markdown-8.html)
- **Describe the current behavior and explain which behavior you would like to see instead**
- **Explain why this enhancement would be useful to most Sami users**
- **List some other applications where this enhancement exists**

## Your First Code Contribution

Unsure where to begin contributing to Sami?
You can start by looking through these beginner and help-wanted issues:

- [Beginner issues](https://github.com/sami-dca/sami/labels/good%20first%20issue) -
  issues which should only require a few lines of code.
- [Help wanted issues](https://github.com/sami-dca/sami/labels/help%20wanted) -
  issues which should be a bit more involved than beginner issues.

You might want to check issues with the most comments first.
While not perfect, number of comments is a reasonable proxy for impact a given change will have.

## Pull Requests

The process described here has several goals:

- Maintain Sami's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible Sami
- Enable a sustainable system for Sami's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

- Follow all instructions in the [template]().
- Follow the [styleguide]().
- After you submit your pull request, verify that all status checks are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed,
the reviewer(s) may ask you to complete additional design work, tests,
or other changes before your pull request can be ultimately accepted.

## Styleguide

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- When only changing documentation, include ``[ci skip]`` in the commit title
- Consider starting the commit message with an applicable emoji:
  - :art: ``:art:`` when improving the format/structure of the code
  - :racehorse: ``:racehorse:`` when improving performance
  - :non-potable_water: ``:non-potable_water:`` when plugging memory leaks
  - :memo: ``:memo:`` when writing docs
  - :penguin: ``:penguin:`` when fixing something on Linux
  - :apple: ``:apple:`` when fixing something on macOS
  - :checkered_flag: ``:checkered_flag:`` when fixing something on Windows
  - :bug: ``:bug:`` when fixing a bug
  - :fire: ``:fire:`` when removing code or files
  - :green_heart: ``:green_heart:`` when fixing the CI build
  - :white_check_mark: ``:white_check_mark:`` when adding tests
  - :lock: ``:lock:`` when dealing with security
  - :arrow_up: ``:arrow_up:`` when upgrading dependencies
  - :arrow_down: ``:arrow_down:`` when downgrading dependencies
  - :shirt: ``:shirt:`` when removing linter warnings

### Python code

All code must respect [PEP8](https://pep8.org/) and be formatted with
[black](https://black.readthedocs.io/en/stable/index.html).

The code is automatically formatted with pre-commit hooks.

#### Functions, variables and class names

Class names are `CamelCased`.
Variables and functions are `snake_cased`.

Example:

```python
class ExampleClass:

    def __init__(self):
        self.attribute_x = None

    def set_attribute(self, some_value) -> None:
        var_name = some_value
        self.attribute_x = var_name

```

#### Type hinting

The use of type hinting is strongly encouraged.
It is only useful on a variable when there is a lot of intricate processing with it.
Please type hint your functions' arguments and returns, with the only exception of magic methods' return values.

### Documentation Styleguide

- Use Markdown.
