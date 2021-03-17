#!/usr/bin/env bash

# Sets up Verificarlo CI on the current branch

# Get name of both current and new CI branch
dev_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
ci_branch="vfc_ci_${dev_branch}"


# Create test workflow on the dev branch
echo "Creating Verificarlo test workflow on the current branch..."
mkdir -p .github/workflows
python setup_test_workflow.py $dev_branch $ci_branch

git add .github/workflows/vfc_test_workflow.yml
git commit -m "[auto] Set up Verificarlo CI on this branch"
echo "Pushing changes to remote : you might have to enter your Github credentials..."
git push origin $dev_branch


# Create report generation workflow (for the new CI branch)
echo "Creating report generation workflow on the CI branch..."
if [ -f "README.md" ]; then # Backup original readme if there is one
    mv README.md README.md.tmp
fi
python setup_ci_readme.py $dev_branch $ci_branch


# Create Verificarlo CI branch
echo "Creating the Verificarlo CI branch (${ci_branch})..."
git checkout --orphan $ci_branch
git rm --cached -r -f .
git add README.md gen_dummy_report.py report.j2
git commit -m "[auto] Create the Verificarlo CI branch for ${dev_branch}"
echo "Pushing changes to remote : you might have to enter your Github credentials..."
git push -u origin $ci_branch


# Cleanup and print termination message
rm README.md
if [ -f "README.md.tmp" ]; then
    mv README.md.tmp README.md
fi
git add .
git checkout $dev_branch

echo
echo
echo "The Verificarlo CI workflow has been set up on this branch !"
echo "When pushing on ${dev_branch}, the ${ci_branch} branch will be automatically updated with your Verificarlo test results and report."
echo
echo
