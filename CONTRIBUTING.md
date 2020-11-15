# Contributing to the project

First off, thanks for taking the time to contribute!

The project is open to contributions from everyone!

The following is a set of guidelines for contributing to the Sami project, 
which are hosted in the [Sami Organization on Github](https://github.com/sami-dca).
\
There are mostly guidelines, not rules.
\
Use your best judgment, and feel free to propose changes to this document in a pull request.

## Table of contents

## Code of conduct

This project and everyone participating in it is governed by the [Sami Code of Conduct]().
\
By participating, you are expected to uphold this code.
\
Please report unacceptable behavior to the core team.

## I don't want to read this whole thing I just have a question!!!

> Note: Please don't file a GitHub issue to ask a question. 
> You'll get faster results by using the resources below.

We have an official message board with a detailed FAQ and where 
the community chimes in with helpful advice if you have questions.

- Sami forum (*will be available soon!*)
- Sami FAQ (*will be available soon!*)

If chat is more your speed, you can join the [Sami Discord server](https://discord.gg/Hcc6YTkpYV).

> Even though Discord is a chat service, 
> it can sometimes take several hours for community members to respond - please be patient !

## What should I know before I get started ?

### Sami and its ecosystem

The Sami project is made of different repositories:
- [sami/sami](https://github.com/sami-dca/sami) - Sami core.
- [sami/sami.github.io](https://sami-dca.github.io) - Sami website source.

They are all hosted in the [Sami Organization on Github](https://github.com/sami-dca).

## How can I contribute ?

### Reporting bugs

This section will guide you through submitting a bug report for Sami.
Following these guidelines helps maintainers and the community understand your report, 
reproduce the behavior, and find related reports.

Before creating bug reports, 
please check in the [Issues section](https://github.com/sami-dca/sami/issues) 
if a similar report doesn't already exist.
When creating a new bug report, please include as many details as possible!

> Note: If you find a Closed issue describing a similar problem you're experiencing, 
> open a new issue and include a link to the one you found.

### Before submitting a bug report

- Check the FAQ and the known bugs section. 
  You might be able to find the cause of the problem and fix things yourself.
  Most importantly, check if you can reproduce the problem in the latest version of Sami, 
  and if you can get the desired behavior by changing the client settings.

### How do I submit a (good) bug report ?

Bugs are tracked as GitHub issues.

Explain the problem and include additional details to help maintainers reproduce the problem:
- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps to reproduce the problem** in as many details as possible. 
  For example, start by explaining how you started the software, 
  e.g. which command exactly you used in the terminal, 
  or how you started it otherwise.
  When listing steps, **don't just say what you did, but explain how you did it**.
  For example, if you moved the cursor on a button, explain if you used the mouse, 
  or a keyboard shortcut, and if so which one ?
- **Provide specific examples to demonstrate the steps**. 
  Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples.
  If you're providing snippets in the issue, please use 
  [Markdown code blocks](https://docs.github.com/en/free-pro-team@latest/github/writing-on-github/getting-started-with-writing-and-formatting-on-github#multiple-lines).
- **Describe the behavior you observed after following the steps** 
  and point out what exactly is the problem with that behavior.
- **Explain which behavior you expected to see instead** and why.
- **Include screenshots and animated GIFs** which show you 
  following the described steps and clearly demonstrate the problem.
  You can use [this tool](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, 
  and [this tool](https://github.com/colinkeenan/silentcast) on Linux.
- **If you're reporting that Sami crashed**, include a crash report with a stack trace from the operating system.
  Include the crash report in the issue in a code block, 
  a file attachment, or put it in a gist and provide link to that gist.
- **If the problem is related to performance or memory**, include a CPU profile capture with your report.
- **If the problem wasn't triggered by a specific action**, 
  describe what you were doing before the problem happened and share more information using the guidelines below.

Provide more context by answering these questions:

- **Did the problem start happening recently** (e.g. after updating to a new version of Sami) 
  or was this always a problem?
- **If the problem started happening recently**, 
  can you reproduce the problem in an older version of Sami? 
  What's the most recent version in which the problem doesn't happen? 
  You can download older versions of Sami from the releases page.
- **Can you reliably reproduce the issue?** 
  If not, provide details about how often the problem happens and under which conditions it normally happens.

Include details about your configuration and environment:

- **Which version of Sami are you using?** 
  You can get the exact version by running ``sami -v`` in your terminal, 
  or by starting Sami and going in the ``About`` section.
- **What's the name and version of the OS you're using?**
- **Are you running Sami in a virtual machine?** 
  If so, which VM software are you using and which operating systems and versions are used for the host and the guest?
- **Include you configuration file**.

## Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Sami, 
including completely new features as well as minor improvements to an existing functionality. 
Following these guidelines helps maintainers and the community understand your suggestion and find related suggestions.

### Before Submitting An Enhancement Suggestion

Before creating enhancement suggestions, please check the 
[GitHub issues](https://github.com/sami-dca/sami/issues?q=is%3Aopen+label%3Aenhancement+label%3Anew%20feature) 
which are tagged as ``new feature`` and ``enhancement`` as you might find out that you don't need to create one. 
When you are creating an enhancement suggestion, please include as many details as possible. 
Fill in the template, including the steps that you imagine you would take if the feature you're requesting existed.

### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as GitHub issues. 
After you've determined which repository your enhancement suggestion is related to, 
create an issue on that repository and provide the following information:

- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
- **Provide specific examples to demonstrate the steps**. 
  Include copy/pasteable snippets which you use in those examples, as 
  [Markdown code blocks](https://docs.github.com/en/free-pro-team@latest/github/writing-on-github/getting-started-with-writing-and-formatting-on-github#multiple-lines).
- **Describe the current behavior and explain which behavior you would like to see instead** and why.
- **Include screenshots and animated GIFs** which help you demonstrate the steps or point out 
  the part of Sami which the suggestion is related to. You can use [this tool](https://www.cockos.com/licecap/) 
  to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) on Linux.
- **Explain why this enhancement would be useful to most Sami users** and 
  isn't something that can or should be implemented as a community package.
- **List some other applications where this enhancement exists**.
- **Specify which version of Sami you're using**. 
  You can get the exact version by running ``sami -v`` in your terminal, 
  or by starting Sami and going in the ``About`` section.
- **Specify the name and version of the OS you're using**.

## Your First Code Contribution

Unsure where to begin contributing to Sami? 
You can start by looking through these beginner and help-wanted issues:

- [Beginner issues](https://github.com/sami-dca/sami/labels/good%20first%20issue) - 
  issues which should only require a few lines of code, and a test or two.
- [Help wanted issues](https://github.com/sami-dca/sami/labels/help%20wanted) - 
  issues which should be a bit more involved than beginner issues.

You might want to check issues with the most comments first. 
While not perfect, number of comments is a reasonable proxy for impact a given change will have.

## Pull Requests

The process described here has several goals:

- Maintain Sami's quality.
- Fix problems that are important to users.
- Engage the community in working toward the best possible Sami.
- Enable a sustainable system for Sami's maintainers to review contributions.

Please follow these steps to have your contribution considered by the maintainers:

- Follow all instructions in the [template]().
- Follow the [styleguide]().
- After you submit your pull request, verify that all status checks are passing
  <details>
  <summary>
    - What if the status checks are failing?
  </summary>
    - If a status check is failing, and you believe that the failure is unrelated to your change, 
      please leave a comment on the pull request explaining why you believe the failure is unrelated. 
      A maintainer will re-run the status check for you. 
      If we conclude that the failure was a false positive, 
      then we will open an issue to track that problem with our status check suite.
  </details>

While the prerequisites above must be satisfied prior to having your pull request reviewed, 
the reviewer(s) may ask you to complete additional design work, tests, 
or other changes before your pull request can be ultimately accepted.

## Styleguide

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
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

### Python Styleguide

All code must respect [PEP8](https://pep8.org/).

#### Imports

Imports must be made at the beginning of the file.

We differentiate five blocks:

1. Built-in full import
2. Built-in partial import
3. Dependency full import
4. Dependency partial import
5. Local package import

Example:
```python
# Built-in full import
import os
import sys

# Built-in partial import
from random import randint

# Dependency full import
import requests

# Dependency partial import
from Crypto.Hash import SHA256

# Local package import
from .config import Config
```

In each block, imports are organized from the shortest to the longest.
If two lines are the same length, they are arranged alphabetically.
Comma-separated partial imports are also arranged alphabetically.

Example:
```python
import os
import sys
import random
import urllib
import functools

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
```

#### Functions, variables and class names

Class names are CamelCased.
\
Variables are lower case and joined with underscores ; 
same goes for functions.

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

Type hinting is strongly recommended.
\
It is only useful on a variable when there is a lot of intricate processing with it.
\
Please type hint your functions' arguments and returns, with the only exception of magic methods' return values.

### Documentation Styleguide

- Use Markdown.
- Reference methods and classes in markdown with the custom {} notation:
  - Reference classes with {ClassName}
  - Reference instance methods with {ClassName::method_name}
  - Reference class methods with {ClassName.method_name}
