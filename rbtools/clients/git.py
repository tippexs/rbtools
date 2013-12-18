import logging
from rbtools.clients.errors import (InvalidRevisionSpecError,
                                    TooManyRevisionsError)
from rbtools.utils.console import edit_text
    def parse_revision_spec(self, revisions=[]):
        """Parses the given revision spec.

        The 'revisions' argument is a list of revisions as specified by the
        user. Items in the list do not necessary represent a single revision,
        since the user can use SCM-native syntaxes such as "r1..r2" or "r1:r2".
        SCMTool-specific overrides of this method are expected to deal with
        such syntaxes.

        This will return a dictionary with the following keys:
            'base':        A revision to use as the base of the resulting diff.
            'tip':         A revision to use as the tip of the resulting diff.
            'parent_base': (optional) The revision to use as the base of a
                           parent diff.

        These will be used to generate the diffs to upload to Review Board (or
        print). The diff for review will include the changes in (base, tip],
        and the parent diff (if necessary) will include (parent_base, base].

        If a single revision is passed in, this will return the parent of that
        revision for 'base' and the passed-in revision for 'tip'.

        If zero revisions are passed in, this will return the current HEAD as
        'tip', and the upstream branch as 'base', taking into account parent
        branches explicitly specified via --parent.
        """
        n_revs = len(revisions)
        result = {}

        if n_revs == 0:
            # No revisions were passed in--start with HEAD, and find the
            # tracking branch automatically.
            parent_branch = self.get_parent_branch()
            head_ref = self._rev_parse(self.get_head_ref())[0]
            merge_base = self._rev_parse(
                self._get_merge_base(head_ref, self.upstream_branch))[0]

            result = {
                'tip': head_ref,
            }

            if parent_branch:
                result['base'] = self._rev_parse(parent_branch)[0]
                result['parent_base'] = merge_base
            else:
                result['base'] = merge_base

            # Since the user asked us to operate on HEAD, warn them about a
            # dirty working directory
            if self.has_pending_changes():
                logging.warning('Your working directory is not clean. Any '
                                'changes which have not been committed '
                                'to a branch will not be included in your '
                                'review request.')
        elif n_revs == 1 or n_revs == 2:
            # Let `git rev-parse` sort things out.
            parsed = self._rev_parse(revisions)

            n_parsed_revs = len(parsed)
            assert n_parsed_revs <= 3

            if n_parsed_revs == 1:
                # Single revision. Extract the parent of that revision to use
                # as the base.
                parent = self._rev_parse('%s^' % parsed[0])[0]
                result = {
                    'base': parent,
                    'tip': parsed[0],
                }
            elif n_parsed_revs == 2:
                if parsed[1].startswith('^'):
                    # Passed in revisions were probably formatted as
                    # "base..tip". The rev-parse output includes all ancestors
                    # of the first part, and none of the ancestors of the
                    # second. Basically, the second part is the base (after
                    # stripping the ^ prefix) and the first is the tip.
                    result = {
                        'base': parsed[1][1:],
                        'tip': parsed[0],
                    }
                else:
                    # First revision is base, second is tip
                    result = {
                        'base': parsed[0],
                        'tip': parsed[1],
                    }
            elif n_parsed_revs == 3 and parsed[2].startswith('^'):
                # Revision spec is diff-since-merge. Find the merge-base of the
                # two revs to use as base.
                merge_base = execute([self.git, 'merge-base', parsed[0],
                                      parsed[1]]).strip()
                result = {
                    'base': merge_base,
                    'tip': parsed[0],
                }
            else:
                raise InvalidRevisionSpecError(
                    'Unexpected result while parsing revision spec')

            pdiff_required = not execute(
                [self.git, 'branch', '-r', '--contains', result['base']])
            if pdiff_required:
                result['parent_base'] = self._get_merge_base(result['base'],
                                                             self.upstream_branch)
        else:
            raise TooManyRevisionsError

        return result
        if not check_install(['git', '--help']):
                check_install(['git.cmd', '--help'])):
    def _strip_heads_prefix(self, ref):
        """Strips prefix from ref name, if possible."""
        return re.sub(r'^refs/heads/', '', ref)

    def extract_summary(self, revision_range=None):
        """Extracts the summary based on the provided revision range."""
        if not revision_range or ":" not in revision_range:
            command = [self.git, "log", "--pretty=format:%s", "HEAD^!"]
        else:
            r1, r2 = revision_range.split(":")
            command = [self.git, "log", "--pretty=format:%s", "%s^!" % r2]

        return execute(command, ignore_errors=True).strip()

    def extract_description(self, revision_range=None):
        """Extracts the description based on the provided revision range."""
        if revision_range and ":" not in revision_range:
            command = [self.git, "log", "--pretty=format:%s%n%n%b",
                       revision_range + ".."]
        elif revision_range:
            r1, r2 = revision_range.split(":")
            command = [self.git, "log", "--pretty=format:%s%n%n%b",
                       "%s..%s" % (r1, r2)]
        else:
            parent_branch = self.get_parent_branch()
            head_ref = self.get_head_ref()
            merge_base = self._get_merge_base(head_ref, self.upstream_branch)
            command = [self.git, "log", "--pretty=format:%s%n%n%b",
                       (parent_branch or merge_base) + ".."]

        return execute(command, ignore_errors=True).strip()

    def _set_summary(self, revision_range=None):
        """Sets the summary based on the provided revision range.

        Extracts and sets the summary if guessing is enabled and summary is not
        yet set.
        if (getattr(self.options, 'guess_summary', None) and
                not getattr(self.options, 'summary', None)):
            self.options.summary = self.extract_summary(revision_range)

    def _set_description(self, revision_range=None):
        """Sets the description based on the provided revision range.

        Extracts and sets the description if guessing is enabled and
        description is not yet set.
        if (getattr(self.options, 'guess_description', None) and
                not getattr(self.options, 'description', None)):
            self.options.description = self.extract_description(revision_range)

    def get_parent_branch(self):
        """Returns the parent branch."""
        return parent_branch

    def get_head_ref(self):
        """Returns the HEAD reference."""

        return head_ref
    def _get_merge_base(self, rev1, rev2):
        """Returns the merge base."""
        return execute([self.git, "merge-base", rev1, rev2]).strip()
    def _rev_parse(self, revisions):
        """Runs `git rev-parse` and returns a list of revisions."""
        if not isinstance(revisions, list):
            revisions = [revisions]
        return execute([self.git, 'rev-parse'] + revisions).strip().split('\n')

    def _diff(self, revisions):
        """
        Handle the internals of generating a diff from the given revisions.
        """
        # TODO: this will get refactored yet again once all the SCMClients
        # implement the revision parsing method and 'rbt post' and
        # 'post-review' get changed to orchestrate the whole process.
        revisions = self.parse_revision_spec(revisions)

        diff_lines = self.make_diff(revisions['base'], revisions['tip'])

        if 'parent_base' in revisions:
            parent_diff_lines = self.make_diff(revisions['parent_base'],
                                               revisions['base'])
            base_commit_id = revisions['parent_base']
        else:
            parent_diff_lines = None
            base_commit_id = revisions['base']
            'base_commit_id': base_commit_id,
    def diff(self, args):
        """Performs a diff across all modified files in the branch.

        The diff takes into account the parent branch.
        # TODO: this should use the parsed revisions
        self._set_summary()
        self._set_description()

        return self._diff([])

    def diff_between_revisions(self, revision_range, args, repository_info):
        """Perform a diff between two arbitrary revisions."""
        # TODO: this should use the parsed revisions
        self._set_summary(revision_range)
        self._set_description(revision_range)

        return self._diff([revision_range])

    def make_diff(self, ancestor, commit=""):
        """Performs a diff on a particular branch range."""
            m = re.search(r'[rd]epo.-paths = "(.+)": change = (\d+)\]', log, re.M)

            else:
                # We should really raise an error here, base_path is required
                pass
    def has_pending_changes(self):
        """Checks if there are changes waiting to be committed.
        Returns True if the working directory has been modified or if changes
        have been staged in the index, otherwise returns False.
        """
        status = execute(['git', 'status', '--porcelain'])
        return status != ''

    def create_commmit(self, message, author):
        modified_message = edit_text(message)
        execute(['git', 'add', '--all', ':/'])
        execute(['git', 'commit', '-m', modified_message,
                 '--author="%s <%s>"' % (author.fullname, author.email)])

    def get_current_branch(self):
        """Returns the name of the current branch."""
        return execute([self.git, "rev-parse", "--abbrev-ref", "HEAD"],
                       ignore_errors=True).strip()