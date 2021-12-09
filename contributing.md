# Contributing to tidy_tweet

Issues (both bug reports and feature requests/discussions) are always welcome on our GitHub, as are pull
requests!

We very much appreciate any help with our documentation - if you found an error or something was unclear
to you, we'd love either an issue for us to fix or a pull request with your own changes :)

## Filing an issue

Please file [issues on our GitHub](https://github.com/QUT-Digital-Observatory/tidy_tweet/issues) if you
encounter any bugs in tidy_tweet, if our documentation is unclear or missing information, or if you have
a feature request!

We will do our best to respond to all issues, and appreciate your time and feedback.

## Development notes

### Version numbers

We use [setuptools_scm](https://github.com/pypa/setuptools_scm/) to manage our version numbers, so hopefully
the only place we ever have to enter a version number is when we create a tag in git.

This does mean that when running tidy_tweet from code (as opposed to installing it with pip), the version
number may not be easily visible or programmatically accessible - most notably, this impacts the metadata
generated when data is processed.

To ensure the version number is available when working from code, we recommend the following workflow:

```bash
# In your shell/terminal, in the root folder of your local tidy_tweet repository
# Ensure you have all the tags fetched (this assumes your git remote is called 'origin')
git fetch origin --tags
# Install your local tidy_tweet in editable mode (note the dot at the end)
pip install -e .
```

This installs tidy_tweet in [development mode](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode),
meaning that you can still make changes to the code and have them used when you run it, but you also have
the benefits of installation. 

Most notably, after installing tidy_tweet in development mode, the version will be available in
`src/tidy_tweet/_version.py` for visibility and programmatic use. Please do not commit `_version.py` to git.
