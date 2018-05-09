# Development guideline for the PERCIVAL characterization software framework

You are highly welcomed to get involved in the development of the PERCIVAL characterization software framework.
This guide intends to explain how to effectively contribute to the project.

## Getting started

For contributing, please:
* Make sure that you have a [GitHub](http://www.github.com) account
* 'Fork' the main project on GitHub [using the button on the page of the main repository](https://github.com/percival-desy/percival-characterization#fork-destination-box)
* Follow our recommendations for sharing your code

## Coding style guide

The PERCIVAL characterization software framework is developed in Python 3.
We try as much as we can to follow the PEP-8 recommendations. 
Please, try as much as you can to follow these recommendations.
A complete style guide for python can be found here: [PEP8 -- syle guide for python code here](https://www.python.org/dev/peps/pep-0008/).
There are some tools developed which will check if your code is PEP-8 compatible and if not it will suggest some modifications.
As an example, you can either [pycodestyle](https://pypi.org/project/pycodestyle/) use or [pylint](https://www.pylint.org).

N.B.: Pull Request not following the Python coding style guide might be rejected.

## General guidelines

* Please commit as often as possible
* To make any modification (fixing a bug, developing a new method) please do not work on the master branch, but create a feature branch
* Use descriptive commits
* Follow the style of the existing coding (see PEP8 recommendations)

## Making changes

Would you like to enhance the framework or to fix a bug? Please follow these instructions:

* 'Fork' the main project on GitHubt [using the button on the page of the main repository](https://github.com/percival-desy/percival-characterization#fork-destination-box). If you have cloned the main project repository on your computer, please add the newly forked repository and renamed the main project repository to 'upstream':

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

* Commit often using a descriptive message. If you are working on an issue, please specify the issue number in your commit
* When your fix or enhancement is done, go on your GitHub repository and clik on the 'compare & pull request' button
* Summarize your changes and click on 'send'
* Your modification will be reviewed and a discussion might be opened





