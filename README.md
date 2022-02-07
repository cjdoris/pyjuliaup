# juliaup

A Python interface to [juliaup](https://github.com/JuliaLang/juliaup), the Julia version
manager.

## Install

```sh
pip install juliaup
```

## Usage

### Find juliaup
- `executable()` finds the juliaup executable.
- `version()` returns version of the juliaup executable.
- `available()` returns True if juliaup is available.
- `install(interactive=True)` installs juliaup. You don't normally need to call this as the
  other API functions automatically install juliaup if required.
- `meta()` returns the parsed contents of `juliaup.json`, which includes information about
  installed versions of Julia.

### Run juliaup
- `add(channel)` adds a channel.
- `default(channel)` sets the default channel.
- `link(channel, file)` links a Julia executable to a channel.
- `remove(channel)` removes a channel.
- `status()` print the status.
- `update(channel=None)` updates all channels or the given channel.
- `update_self()` updates juliaup itself.
- `run(args, **kw)` run juliaup with the given arguments. Keyword arguments are passed on to
  `subprocess.run`.
