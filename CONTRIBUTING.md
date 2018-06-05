# Development guideline for the PERCIVAL characterization software framework

You are highly welcomed to get involved in the development of the PERCIVAL characterization software framework.
This guide intends to explain how to effectively contribute to the project.

## Getting started

For contributing, please:
* Make sure that you have a [GitHub](http://www.github.com) account
* 'Fork' the main project on your GitHub repository [using the button on the page of the main repository](https://github.com/percival-desy/percival-characterization#fork-destination-box)
* Follow our recommendations for [making changes](#making-changes) and sharing your code

## Coding style guide

The PERCIVAL characterization software framework is developed in Python-3.
We try as much as possible to follow the PEP-8 recommendations.
We kindly invite you to do so. 
A complete style guide for python can be found here: [PEP8 -- syle guide for python code here](https://www.python.org/dev/peps/pep-0008/).
There are some tools developed which will check if your code is PEP-8 compatible and if not it will suggest some modifications.
As an example, you can either [pycodestyle](https://pypi.org/project/pycodestyle/) use or [pylint](https://www.pylint.org).
We would like to remind you to use docstrings for useful comments of your methods/functions.

N.B.: Pull Request not following the Python coding style guide might be rejected.

## General guidelines

* Please commit as often as possible
* Do not work on the master branch for fixing a bug or developing a new methods: **create a feature branch** 
* Use descriptive commits explaining what you have done (see commit section for more details)
* Follow the style of the existing coding (see [PEP8 recommendations]((https://www.python.org/dev/peps/pep-0008/)))

## Making changes

Would you like to enhance the framework or to fix a bug? Please follow these instructions:

* 'Fork' the main project on GitHub [using the button on the page of the main repository](https://github.com/percival-desy/percival-characterization#fork-destination-box).
If you have cloned the main project repository on your computer, please add the newly forked repository and renamed the main project repository to 'upstream':

```
  git remote rename origin usptream
  git remote add origin https://github.com/[YOUR USERNAME]/percival-characterization
``` 

* Create a new branch for developing a new feature or fixing a bug based on the ```master``` branch:
```
  git branch myFeature master
  git checkout myFeature
```

* Do your modifications on your local clone and keep it sync with the development 'upstream' repository:
```
  git pull upstream master
```

* Commit often using a descriptive message (see [commit](#git-commit) section). If you are working on an issue, please specify the issue number in your commit.
```
  git commit
```

* When your fix or enhancement is done, go on your GitHub repository and clik on the '''compare & pull request''' button
* Summarize your changes and click on 'send' (see [Pull requests](#submitting-a-pull-requests) section)
* Your modification will be reviewed and a discussion might be opened

### Git commit

This is an advice for writing your commits and make it clear for everyone:

1. Separate subject from body with a blank line
2. Limit the subject to 50 characters
3. Capitalize the subject line
4. Do not end the subject with a period
5. Use the imperative mood in the subject line
6. Wrap the body at 72 characters
7. Use the body to explain *what* and *why* instead of *how*

### Submitting a pull request

* Retrieve the latest changes from the 'upstrem' repository as explained [above](#making-changes)
* Format the code to the Python style
* Go to '''compare & pull request''' button
* Follow the instructions. If your code is only partially readyn please use the 'WIP:' prefix. Then submit the merge request
* Include screenshots and animated GIFs in your pull request whenever possible
* The maintainers will look at your proposed changes and likely provide some feedback
* Please continue to update your code with the received comments until every reviewer is happy :)
* Your merge request can now be merged in. 
