# Contributor agreement

This project uses the [Developer Certificate of Origin (DCO) version 1.1](https://developercertificate.org/) to record a contributor's right to submit work. Read the complete certificate at that link before signing off a commit. The explanations here supplement the certificate; they do not replace or modify its terms.

## Licensing status

The repository does not yet have a project-wide license. This agreement does not supply one, grant rights on behalf of other authors, or authorize relicensing third-party material. Maintainers must establish the applicable license before merging external contributions. Draft proposals and review can proceed while that decision is pending; contributors must see and accept the actual applicable license before final sign-off.

Datasets, papers, dependencies, and other external materials retain their own licenses. See [dataset provenance](data/README.md) for SciFact. A link to a resource does not grant permission to copy its content into this repository.

## What contributors agree to

When submitting a contribution for merge:

1. Read the applicable license and the DCO. Submit only work you have the right to contribute, including any required employer or coauthor authorization.
2. Identify reused or adapted material, its original source, license, and any required notices. Explain substantial adaptations in the pull request.
3. Follow the [contribution guidelines](CONTRIBUTING.md) and [code of conduct](CODE_OF_CONDUCT.md).
4. Review and verify the contribution, including AI-assisted code or writing. Do not submit fabricated sources, results, permissions, or testing claims.
5. Keep credentials, private datasets, personal records, and confidential employer material out of commits, notebook outputs, and issue attachments.

No copyright assignment or additional right to relicense your work is requested by this document. You retain whatever copyright you hold, subject to the applicable contribution license. Submitting a pull request does not guarantee acceptance, payment, or a maintainer role.

## Sign off your commits

Once the applicable license is established, add your own sign-off to each contribution commit:

```bash
git commit -s -m "Add BM25 retrieval experiment"
```

Git appends a trailer using your configured identity:

```text
Signed-off-by: Your Name <your-email@example.com>
```

Use an identity and email you are comfortable publishing, consistent with your Git author information. GitHub's verified no-reply email can be used. Commit history and sign-offs are public records. A DCO sign-off is a certification; it is different from a cryptographic commit signature.

To add a missing sign-off to your own latest commit:

```bash
git commit --amend --no-edit --signoff
```

Amending changes the commit ID. Coordinate with collaborators before changing already shared history. Do not sign on behalf of another contributor or add their certification yourself. For a multi-author change, preserve attribution and have each contributor certify their own work.

## Review and enforcement

Maintainers review source attribution, licensing compatibility, and sign-offs before merge. The repository currently has no automated DCO app or branch-protection enforcement configured by these files. A checked pull-request box alone does not replace the commit sign-offs or license review.

If the terms change while a contribution is under review, maintainers should explain the change and obtain the contributor's agreement before merging. This document does not automatically apply a future license to existing submissions.
