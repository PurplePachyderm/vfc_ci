# Helper script to set up Verificarlo CI on the current branch

import git

import sys
import os
from jinja2 import Environment, FileSystemLoader

################################################################################


    # Helper functions

def gen_readme(dev_branch, ci_branch):

    # Init template loader
    path = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(path))
    template = env.get_template("workflow_templates/ci_README.j2.md")

    # Render template
    render = template.render(dev_branch=dev_branch, ci_branch=ci_branch)

    # Write template
    with open("README.md", "w") as fh:
        fh.write(render)


def gen_workflow(git_host, dev_branch, ci_branch):

    # Init template loader
    path = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(path))


    if git_host == "github":
        # Load template
        template = env.get_template("workflow_templates/vfc_test_workflow.j2.yml")

        # Render it
        render = template.render(dev_branch=dev_branch, ci_branch=ci_branch)

        # Write the file
        filename = ".github/workflows/vfc_test_workflow.yml"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as fh:
            fh.write(render)


    if git_host == "gitlab":
        template = env.get_template("workflow_templates/gitlab-ci.j2.yml")

        # Ask for the user that will run the jobs (Gitlab specific)
        user = input("Enter the name of the user who will run the CI jobs:")
        render = template.render(dev_branch=dev_branch, ci_branch=ci_branch)

        filename = ".gitlab-ci.j2.yml"
        with open(filename, "w") as fh:
            fh.write(render)


################################################################################

def setup(git_host):

        # Init repo and make sure that setup is possible

    repo = git.Repo(".")
    repo.remotes.origin.fetch()

    # Make sure that repository is clean
    assert(not repo.is_dirty()), "Unstaged changes detected in your work tree."

    dev_branch = repo.active_branch
    dev_branch_name = str(dev_branch)
    dev_remote = dev_branch.tracking_branch()

    # Make sure that the active branch (on which to setup the workflow) has a remote
    assert(dev_remote != None), "The current branch doesn't have a remote."

    # Make sure that we are not behind the remote (so we can push safely later)
    rev = "%s...%s" % (dev_branch_name, str(dev_remote))
    commits_behind = list(repo.iter_commits(rev))
    assert(commits_behind == []), "The local branch seems to be at least one commit behind remote."


        # Commit the workflow on the current (dev) branch

    ci_branch_name = "vfc_ci_%s" % dev_branch_name
    gen_workflow(git_host, dev_branch_name, ci_branch_name)
    repo.git.add(".")
    repo.index.commit("[auto] Set up Verificarlo CI on this branch")
    repo.remote(name="origin").push()


        # Create the CI branch (orphan branch with a readme on it)
        # (see : https://github.com/gitpython-developers/GitPython/issues/615)

    repo.head.reference = git.Head(repo, "refs/heads/"+ ci_branch_name)

    repo.index.remove(["*"])
    gen_readme(dev_branch_name, ci_branch_name)
    repo.index.add(["README.md"])

    repo.index.commit(
        "[auto] Create the Verificarlo CI branch for %s" % dev_branch_name,
        parent_commits=None
    )
    repo.remote(name="origin").push(refspec="%s:%s" % (ci_branch_name, ci_branch_name))

    # Force checkout back to the original (dev) branch
    repo.git.checkout(dev_branch_name, force=True)


    print("A Verificarlo CI workflow has been setup on %s." % dev_branch_name)
    print("Make sure that you have a vfc_tests_config.json on this branch.")

    if git_host == "gitlab":
        print("Since you are using GitLab, make sure that you have created a CI_PUSH_TOKEN for the user you specified.")
