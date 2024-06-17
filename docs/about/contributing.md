# Contributing

We are happy to see you here! 🚀

Looking for a way to contribute to db-ally? Check-out our issues with a [good first issue](https://github.com/deepsense-ai/db-ally/labels/good%20first%20issue) label.

You can also suggest new features or report bugs by [opening an issue](https://github.com/deepsense-ai/db-ally/issues).

## Contributor guide

1. Fork the repository and clone it locally.

2. Install the development dependencies:

    ```bash
    ./setup_dev_env.sh
    ```

    It will create a virtual environment and install all necessary dependencies.
    Make sure that you have Python 3.8 or higher installed on your machine.

3. Make your changes and write tests for them if necessary.

4. Run the tests:

    ```bash
    pytest tests/
    ```

5. If creating new feature, don't forget to update the documentation.

    You can run the documentation locally by executing:

    ```bash
    mkdocs serve
    ```

6. Push your changes to your fork and create a pull request from there.


## Commits convention

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for our commit messages.

In practice that means that each commit message should be prefixed with one of the following types:

```
feat:     A new feature
fix:      A bug fix
docs:     Documentation only changes
refactor: A code change that neither fixes a bug nor adds a feature
test:     Adding missing tests or correcting existing tests
chore:    Changes to the build process or repo setup
```

For example:
```
feat: add text2sql views code generation
```

Breaking changes should be indicated by adding an exclamation mark to the prefix:
```
feat!: change collection.ask method API
```
