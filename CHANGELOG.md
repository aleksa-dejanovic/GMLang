# gmlang changelog

All _notable_ changes to this project will be documented in this file.

The format is based on _[Keep a Changelog][keepachangelog]_, and this project
adheres to _[Semantic Versioning][semver]_.


Backward incompatible changes are marked with **(BIC)**. These changes are the
reason for the major version increase so when upgrading between major versions
please take a look at related PRs and issues and see if the change affects you.

## [Unreleased]

### Added

- Explicit AST dataclasses, source spans, and a parglare 0.22.0 GLR frontend.
- `create_parser()` with string/file parsing and public AST class lookup.
- Recorded TextX compatibility cases and local packed-forest ambiguity checks.

### Fixed

- Invalid-node-name tests now assert syntax errors instead of swallowing assertions.
- Empty and whitespace-only documents consistently return `File(commands=[])`.

### Changed

- **(BIC)** Connection aliases require parentheses around the complete edge
  expression, including tags and attributes: `(A -- B tag) as Alias`.
  Node aliases and `let` assignments retain their existing syntax.
- **(BIC)** Removed TextX dependencies, language registry, and metamodel metadata.
  Use `gmlang.create_parser()` instead of `textx.metamodel_for_language("gmlang")`.
  Direct `gmlang_language()` imports remain supported as an ordinary factory.
- **(BIC)** Parser/interpreter errors now use GMLang-owned syntax, semantic,
  and ambiguity errors instead of TextX exceptions.
- Replaced the old metamodel diagram with parser-automaton export tooling.


[Unreleased]: https://github.com/aleksa-dejanovic/GMLang/commits/master


[keepachangelog]: https://keepachangelog.com/
[semver]: https://semver.org/spec/v2.0.0.html
