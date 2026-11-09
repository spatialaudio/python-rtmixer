# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## What this is

python-rtmixer (`rtmixer` on PyPI) provides reliable low-latency audio playback and recording
from Python. It builds on [sounddevice](https://python-sounddevice.readthedocs.io/) and
PortAudio, but the audio callback is written in C (compiled with CFFI) so that it never enters
the Python interpreter and is not affected by the GIL or garbage collection. It is a small
project maintained by volunteers: one Python module, one C file, and one C header.

## Working with humans (read first)

Every change here is reviewed by a volunteer maintainer and then maintained by humans for years.
The human you are working with is the author of anything that leaves their machine, and they are
the one who talks to the maintainers.

- **The human is the sole author.** Do not add `Co-Authored-By:` trailers for Claude / Copilot /
  Cursor / any other tool, and do not make a bot the commit author. The human opening the PR
  takes full responsibility for it and must be able to explain and defend every line on request.
  Disclose which tools were used, and for what, in the PR description instead.
- **Do not speak for the human in public.** Do not post agent-written text to issues, PRs, review
  comments, or discussions, and do not open, comment on, or close them on the human's behalf.
  Draft for the human if they ask; they decide whether to post and rewrite it in their own words.
- **Do not commit or push unless asked**, and never force-push, rewrite published history, or
  create tags or releases.
- **Agree on the design before writing code.** For anything beyond a local fix, describe the
  approach to the human in a few sentences and confirm it is the smallest one that works. If the
  change touches the C callback or the Python/C memory-ownership contract (see Architecture), say
  so explicitly; those are the changes a maintainer will look at hardest.
- **Report what actually happened.** If a build failed, an example was not run, or something
  could not be tested without audio hardware, say so plainly rather than implying it works.

## Keep code and tests brief

A big diff is a cost, not an accomplishment. The whole library is about 850 lines of Python and C; a change that
adds a large fraction of that needs a very good reason.

- **Stop and re-plan at roughly 50 new lines of implementation.** Growth past that, or reaching
  for a new module, a new dependency, or a new action type, is a signal that the design is too
  elaborate. Stop, tell the human, and offer the smaller version.
- **YAGNI.** No retry logic, configuration knobs, platform-specific fallbacks, extension points,
  or "robustness" that nothing in the change needs. New public API (a method, a keyword argument,
  a new `actiontype`) needs a demonstrated user need, because it is documented and supported
  forever. Hard-code the single behavior that is wanted and add the option when someone asks.
- **DRY.** Reuse what exists: `_Base._enqueue`, `_check_channels`, the `sounddevice` stream
  machinery, `pa_ringbuffer`. When the four `play_*`/`record_*` methods or the C action handlers
  need the same new logic, factor it into one private helper rather than editing four copies.
- **Implement at the highest layer that exists.** Behavior shared by `Mixer`, `Recorder`, and
  `MixerAndRecorder` belongs in `_Base`.
- **Keep tests and verification just as brief.** There is currently no unit test suite (CI only
  builds wheels and checks that `import rtmixer` works). Do not add a test framework, test
  directory, mock audio backend, or CI job without asking the human first. When a test is
  warranted, prefer a few compact assertions over a large harness, and prefer extending an
  existing example in `examples/` over writing a new script. Throwaway verification scripts go in
  a scratch directory, not the repo.
- **Do not add or bump dependencies** (runtime or build) without asking first.

## Common commands

Development install (the `portaudio` git submodule is needed to compile the extension):
```bash
git submodule update --init
python -m pip install -e .
```

After changing `src/rtmixer.c`, `src/rtmixer.h`, or `rtmixer_build.py`, rebuild the extension
(rerun the editable install; the compiled `_rtmixer*.so` lands in `src/`). A quick smoke test:
```bash
python -c "import rtmixer; print(rtmixer.__version__)"
python examples/fetch_stats.py   # needs a working audio device
```

Docs (Sphinx, built on CircleCI and Read the Docs):
```bash
python -m pip install -r doc/requirements.txt
python -m sphinx doc _build
python -m sphinx doc _build -b linkcheck
```

Wheels are built with cibuildwheel (`.github/workflows/build_wheels.yml`, configured in
`pyproject.toml`) as abi3 wheels for CPython >= 3.10 plus PyPy.

Before handing work back, at minimum rebuild the extension if C code changed, check that
`import rtmixer` works, run whichever example exercises the changed code if an audio device is
available (and say so if not), and build the docs if docstrings or `doc/` changed.

## Boundaries

Ask the human first before:
- adding or bumping a dependency, or changing the minimum Python version;
- editing CI / release configuration (`.github/`, `.circleci/`, `.readthedocs.yml`, `tools/`,
  `[tool.cibuildwheel]` in `pyproject.toml`) or the `portaudio` submodule pointer;
- adding, renaming, or removing public API, including new action types or keyword arguments;
- changing the version number or editing existing `NEWS.rst` entries for released versions.

Never:
- add AI co-authorship trailers or post agent-written text to issues or PRs (see above);
- call into Python, allocate or free memory, take locks, or do I/O in the C audio callback;
- silence compiler warnings or weaken a `CALLBACK_ASSERT` instead of fixing the cause;
- commit build products (`_rtmixer*.so`, `*.egg-info`, `build/`, `_build/`) or audio files;
- adapt code whose license is not compatible with this project's MIT license or cannot be
  determined.

## Architecture

### Files
- `src/rtmixer.py`: the public Python API. `_Base` (a subclass of `sounddevice._StreamBase`)
  owns the queues and state; `Mixer` (output), `Recorder` (input), and `MixerAndRecorder`
  (duplex) add `play_buffer`/`play_ringbuffer` and `record_buffer`/`record_ringbuffer`.
  `RingBuffer` is re-exported from `pa_ringbuffer`. Upper-case constants from the C library
  (`PLAY_BUFFER`, `CANCEL`, ...) are copied into the module namespace at import.
- `src/rtmixer.h`: declarations shared by C and CFFI (`enum actiontype`, `struct action`,
  `struct stats`, `struct state`). It is parsed by `ffibuilder.cdef()`, so it must stay within
  what CFFI's parser accepts (no `#include`, no macros beyond what is already there).
- `src/rtmixer.c`: the PortAudio callback and its helpers.
- `rtmixer_build.py`: the CFFI build script that produces the `_rtmixer` extension, compiling
  `rtmixer.c` together with `pa_ringbuffer.c` from the `portaudio` submodule. PortAudio itself
  is not linked; the callback is handed to sounddevice's already-loaded PortAudio.
- `doc/`: Sphinx docs. `doc/api.rst` uses `literalinclude` on ranges of `src/rtmixer.h`, so
  editing `struct action` or `struct stats` changes the rendered docs. `doc/fake_rtmixer.py` and
  `doc/fake_sounddevice.py` stand in for the compiled modules during the docs build.
- `examples/`: runnable scripts; these double as the manual test suite.

### Actions and queues
Each command (`play_buffer`, `cancel`, `fetch_and_reset_stats`, ...) allocates a
`struct action` with `ffi.new()` in Python and writes the pointer into `action_q`, a lock-free
PortAudio ring buffer. Once per audio block the callback reads new actions into a singly linked
list (`CANCEL` actions go to the front, everything else to the back), processes each one against
the block's timing info (`requested_time`, `allow_belated` encoded via `actual_time`), and moves
finished actions to `done_actions`, which is sent to `result_q` as one linked list per block
(and kept for the next block if `result_q` is full). Python drains `result_q` in
`_drain_result_q()` (called from `_enqueue()` and the `actions` property), walks each list,
and drops its references.

### Memory ownership
The C callback only ever holds raw pointers; Python owns all memory. `_Base._actions` maps each
in-flight action to the object it depends on (`keep_alive`: the audio buffer, the ring buffer,
or the action being cancelled), and an entry is removed only after the callback has handed the
action back through `result_q`. `_Base.__del__` aborts and closes the stream before that memory
can be freed. Any change that adds a pointer to `struct action` or `struct state` must keep this
contract, and is the most likely place for a use-after-free or crash.

### Real-time constraints
The callback runs on PortAudio's audio thread. It must be bounded-time and must not allocate,
lock, block, or call into Python. `CALLBACK_ASSERT` prints and returns `paAbort` on failure
(debug builds only; `NDEBUG` disables it).

## Changelog (`NEWS.rst`)

Add a `NEWS.rst` entry for changes that users would notice: new or changed API or behavior, bug
fixes in the callback or Python API, new or dropped Python versions or wheel platforms, and new
or changed dependencies. Skip it for refactoring, docs-only edits, examples, and CI or tooling
changes that do not change what gets shipped. Put the entry at the top of the file under a
`Version x.y.z -- unreleased` heading (create one with the next patch version if it is missing).
The maintainer fills in the date and the `PyPI__` / `diff__` links at release time. Use the same
style as the existing entries: one short bullet per change, starting with a verb ("Add", "Fix",
"Drop"), describing the effect on users rather than the implementation.

## Code conventions

- Python: PEP 8, lines at most 79 characters (see `.editorconfig`); single quotes are used
  throughout. Docstrings are reStructuredText rendered by Sphinx with `default_role = 'any'`, so
  single backticks cross-reference (`` `wait()` ``, `` `sounddevice.Stream` ``) and
  `nitpicky = True` means unresolved references break the docs build.
- C: C99, two-space indentation, braces on their own lines, leading commas on continued
  parameter lists, `//` comments, as in `src/rtmixer.c`.
- Private names start with an underscore; imported third-party modules are aliased privately
  (`import sounddevice as _sd`) so they do not show up in the public namespace.
- Match the surrounding style rather than reformatting existing code; there is no
  auto-formatter, and unrelated whitespace changes make review harder.
- Code adapted from an outside source must be under an MIT-compatible license (MIT, BSD, ISC,
  Apache-2.0, public domain, ...); attribute it in a comment directly above the adapted code,
  naming the source and its license, as `setup.py` and `.circleci/config.yml` already do.
