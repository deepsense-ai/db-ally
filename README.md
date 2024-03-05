# db-ally

Repository is created with deepsense.ai project template boilerplate. Adapt to your needs.
Documentation is available at [https://deepsense-ai.github.io/ds-template/](https://deepsense-ai.github.io/ds-template/).


# Setup developer environment

To start, you need to setup your local machine.

## Setup venv

You need to setup virtual environment, simplest way is to run from project root directory:

```bash
$ . ./setup_dev_env.sh
$ source venv/bin/activate
```
This will create a new venv and run `pip install -r requirements-dev.txt`.
Last line shows how to activate the environment.

## Install pre-commit

To ensure code quality we use pre-commit hook with several checks. Setup it by:

```
pre-commit install
```

All updated files will be reformatted and linted before the commit.

To reformat and lint all files in the project, use:

`pre-commit run --all-files`

The used linters are configured in `.pre-commit-config.yaml`. You can use `pre-commit autoupdate` to bump tools to the latest versions.

## Autoreload within notebooks

When you install project's package add below code (before imports) in your notebook:
```
# Load the "autoreload" extension
%load_ext autoreload
# Change mode to always reload modules: you change code in src, it gets loaded
%autoreload 2
```
Read more about different modes in [documentation](https://ipython.org/ipython-doc/3/config/extensions/autoreload.html).

All code should be in `src/` to make reusability and review straightforward, keep notebooks simple for exploratory data analysis.
See also [Cookiecutter Data Science opinion](https://drivendata.github.io/cookiecutter-data-science/#notebooks-are-for-exploration-and-communication).

# Command line interface
The library provides a command line interface (CLI) to interact with the database. To use it, you need to install the package in editable mode:

```bash
$ pip install -e .
```

After that, you can use the `dbally` command to interact with the database. To see the available commands, run:

```bash
$ dbally --help
```

# Project documentation

In `docs/` directory are Sphinx RST/Markdown files.

To build documentation locally, in your configured environment, you can use `build_docs.sh` script:

```bash
$ ./build_docs.sh
```

Then open `public/index.html` file.

Please read the official [Sphinx documentation](https://www.sphinx-doc.org/en/master/) for more details.



### GitLab Pages Documentation

By default **Gitlab** pipelines have `pages` step which will build sphinx documentation automatically on main branch - and it will push it to **GitLab Pages** to be statically hosted.

To access it, you need to have a link, which can be found on **GitLab -> Settings -> Pages** page.

Only people with repository access can view it.

Please read more about it [here](https://docs.gitlab.com/ee/user/project/pages/index.html).# Semantic version bump

To bump version of the library please use `bump2version` which will update all version strings.

NOTE: Configuration is in `.bumpversion.cfg` and **this is a main file defining version which should be updated only with bump2version**.

For convenience there is bash script which will create commit, to use it call:

```bash
# to create a new commit by increasing one semvar:
$ ./bump_version.sh minor
$ ./bump_version.sh major
$ ./bump_version.sh patch
# to see what is going to change run:
$ ./bump_version.sh --dry-run major
```
Script updates **VERSION** file and setup.cfg automatically uses that version.

You can configure it to update version string in other files as well - please check out the bump2version configuration file.



On GitLab CI, you can build development, test package and upload it manually as minor.major.patch-dev{BUILD_NUMBER} to PIP registry.

Every MR keeps package for 7 days each (check `package` artifact).

On the main branch you can trigger _release_ which uploads minor.major.patch version to PIP registry.


