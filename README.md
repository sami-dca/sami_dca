<p align="center">
    <img src="https://gravatar.com/avatar/3c7bb98e5004a55cd6d0c990bfb6d0c9?s=512" />
</p>

![License](https://img.shields.io/github/license/sami-dca/sami_dca)
[![Discord server](https://img.shields.io/discord/777126677795831828.svg?label=Discord)](https://discord.gg/Hcc6YTkpYV)
![Code coverage](https://img.shields.io/codecov/c/github/sami-dca/sami_dca)

Sami is a decentralized communication application, written in Python,
and available for free on [GitHub](https://github.com/sami-dca/sami_dca).

For a detailed description of how the system works,
please refer to the [Sami Paper](https://github.com/sami-dca/sami_dca/blob/master/PAPER.md)

## Installation

### Standard user

Stable and ready-to-use versions are available in the 
[releases section](https://github.com/sami-dca/sami_dca/releases).

<hr />

To set up Sami, you will need Python 3.7 or above.
You can download a copy from https://python.org

*Note: if you're already using Python, we advise you use a virtual environment 
for this next part, otherwise no worries !*

Finally, to get it to work, we need to install the dependencies.
For that, run the script ``setup_windows.bat``.

After that, you should be able to run `sami.py`.

If despite these information you encounter difficulties, hop on the [Discord
server](https://discord.gg/Hcc6YTkpYV), we'd be happy to help !

*PS: we are currently working on providing executables (e.g. `.exe`) to 
simplify the installation process*

## Contributing

If you wish to contribute to the project, please first review our 
[guidelines](https://github.com/sami-dca/sami_dca/blob/master/CONTRIBUTING.md).

Our team is available on the [Discord server](https://discord.gg/Hcc6YTkpYV)
if we can help with your contributions.

### Development

To start working on the project, clone the repo with:

    git clone https://github.com/sami-dca/sami_dca

***For this next part, using a Python virtual environment is strongly recommended.***

Next, install the usual dependencies using

    pip install -r requirements.txt

and the development dependencies with

    pip install -r requirements_dev.txt
