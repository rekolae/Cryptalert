# Cryptalert

Provide alerts based on cryptocurrency movements

Everyone is welcome to take part in the project, but please read through the following

# Commit messages and format

Commit messages should be clearly written in english and be compact to ensure easy reading e.g.
* `"[258-ESC-BSOD-FIX] Fixed BSOD when pressing ESC exactly 666 times"`

When it comes to commits the more the merrier compared to one huge commit with a message that spans 5 rows.

To automate adding the `[<Issue ID>-<branch description>]` to the beginning of a commit messages have a look at [this gist](https://gist.github.com/rekolae/28b2b0d27cff688b77f1642989e1cc24).

It can be installed by renaming `.git/hooks/prepare-commit-msg.sample` to `prepare-commit-msg` and pasting the script in the gist to the file and making it executable (if needed). 

This way `$ git commit -m "[<Issue ID>-<branch description>] Fixed this and..."` can be written without the issue id and branch part as: `$ git commit -m "Fixed this and..."` saving many many key presses and your nerves.


# Branching

## Quick Legend

<table>
    <thead>
        <tr>
            <th>Instance</th>
            <th>Branch</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Stable</td>
            <td>stable</td>
            <td>Accepts merges from Working and Hotfixes</td>
        </tr>
        <tr>
            <td>Working</td>
            <td>master</td>
            <td>Accepts merges from Features and Bugfixes</td>
        </tr>
        <tr>
            <td>Feature</td>
            <td>feature/&lt;Issue ID&gt;-&lt;short description&gt;</td>
            <td>Always branch off HEAD of Working</td>
        </tr>
        <tr>
            <td>Bugfix</td>
            <td>bugfix/&lt;Issue ID&gt;-&lt;short description&gt;</td>
            <td>Always branch off HEAD of Working</td>
        </tr>
        <tr>
            <td>Hotfix</td>
            <td>hotfix/&lt;Issue ID&gt;-&lt;short description&gt;</td>
            <td>Always branch off Stable</td>
        </tr>
    </tbody>
</table>

Couple of example branch names:
* `feature/123-GUI-refactoring` 
* `bugfix/666-fix-BSOD-on-click`


## Main Branches

The main repository will always hold two evergreen branches:

* `master`
* `stable`

The main branch should be considered `origin/master` and will be the main branch where the source code of `HEAD` always reflects a state with the latest delivered development changes for the next release.

Consider `origin/stable` to always represent the latest code which could be deployed to production.

When the source code in the `master` branch is considered stable, all of the changes will be merged into `stable`. If `stable` has gained enough significant changes, the changes are tagged with a release number.


## Supporting Branches

Supporting branches are used to aid parallel development, ease tracking of features, and to assist in quickly fixing production problems. Unlike the main branches, these branches always have a limited life time, since they will be removed eventually.

The different types of branches used are:

* Feature branches
* Bug branches
* Hotfix branches

Each of these branches have a specific purpose and are bound to strict rules as to which branches may be their originating branch and which branches must be their merge targets.


## Tagging releases and hotfixes

When a stable branch has gotten to the point that a release should be made, it has to be tagged with a corresponding version number. The version number should follow semantic versioning format i.e. `MAJOR.MINOR.PATCH` where incrementing conforms to the following:

* `MAJOR` number increment when you make incompatible API changes
* `MINOR` number increment when you add functionality in a backwards compatible manner
* `PATCH` number increment when you make backwards compatible bug fixes

See [Semantic Versioning](https://semver.org/) for more infomation.

In practise tagging works as follows:

```
$ git checkout stable                               // Change to the stable branch
$ git merge --no-ff master                          // Forces creation of commit object during merge
$ git tag                                           // List tags to check latest version number
V1.0.0
V1.0.1
$ git tag -a <V1.1.0> -m <msg, e.g "Release...">    // Tags the fix
$ git push origin stable --tags                     // Push tag changes
```

or when a hotfix was issued:

```
$ git commit -m "Hotfix for..."                     // Commit changes
$ git checkout stable                               // Change to the stable branch
$ git merge --no-ff <hotfix-branch-name>            // Forces creation of commit object during merge
$ git tag                                           // List tags to check latest version number
V1.0.0
V1.0.1
V1.1.0
$ git tag -a V1.1.1 -m <msg, e.g "Hotfix...">       // Tags the fix
$ git push origin stable --tags                     // Push tag changes
```


## Working with a feature branch

If the branch does not exist yet, create the branch locally and then push to GitHub. A feature branch should always be 'publicly' available. That is, development should never exist in just one developer's local branch.

```
$ git checkout -b <feature-branch-name>             // Creates a local branch for the new feature
$ git push origin <feature-branch-name>             // Makes the new feature remotely available
```

Periodically, changes made to `master` (if any) should be merged back into the current feature branch.

```
$ git merge master                                  // Merges changes from master into feature branch
```

When development on the feature is complete, the lead (or engineer in charge) should merge changes into `master` and then make sure the remote branch is deleted.

```
$ git checkout master                               // Change to the master branch  
$ git merge --no-ff <feature-branch-name>           // Makes sure to create a commit object during merge
$ git push origin master                            // Push merge changes
$ git push origin :<feature-branch-name>            // Deletes the remote branch, git push origin --delete <feature-branch-name> works as well
```


## Working with a hotfix branch

If the branch does not exist yet, create the branch locally and then push to GitHub. A hotfix branch should always be 'publicly' available. That is, development should never exist in just one developer's local branch.

```
$ git checkout -b <hotfix-branch-name> stable       // Creates a local branch for the new hotfix
$ git push origin <hotfix-branch-name>              // Makes the new hotfix remotely available
```

When development on the hotfix is complete, merge changes into `stable` and then update the tag.

```
$ git checkout stable                               // Change to the stable branch
$ git merge --no-ff <hotfix-branch-name>            // Forces creation of commit object during merge
$ git tag -a <tag> -m <msg>                         // Tags the fix
$ git push origin stable --tags                     // Push tag changes
```

Merge changes into `master` so not to lose the hotfix and then delete the remote hotfix branch.

```
$ git checkout master                               // Change to the master branch
$ git merge --no-ff <hotfix-branch-name>            // Forces creation of commit object during merge
$ git push origin master                            // Push merge changes
$ git push origin :<hotfix-branch-name>             // Deletes the remote branch, git push origin --delete <hotfix-branch-name> works as well
```