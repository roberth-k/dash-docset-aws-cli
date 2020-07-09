dash-docset-aws-cli
===================

_AWS-CLI.docset for the [Dash](https://kapeli.com/dash) documentation browser._

This docset is available as a User-Contributed Docset. Download it from Dash directly.

Generated from [AWS CLI](https://github.com/aws/aws-cli) documentation (v2 branch).

Instructions for building Dash docsets are available on the [Dash website](https://kapeli.com/docsets#dashDocset).

The official version of this documentation is hosted [here](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html).
_The maintainer of this repository is not affiliated with AWS._

![Screenshot](static/screenshot.png)

## Building the docset

The system must provide the following:

- git
- GNU Make
- Python 3.8

To build the docset, run:

```bash
$ make .build/2.0.29/AWS-CLI.tgz
```

Replace 2.0.29 with a version of AWS CLI v2. 

The docset will be available at `.build/2.0.29/AWS-CLI.docset`, along with a
compressed variant at `.build/2.0.29/AWS-CLI.tgz`.
