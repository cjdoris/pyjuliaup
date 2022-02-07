# pyjuliaup

A Python interface to [JuliaUp](https://github.com/JuliaLang/juliaup), the Julia version
manager.

## Install

```sh
pip install juliaup
```

## Usage

### Find JuliaUp
- `executable()` finds the JuliaUp executable.
- `version()` returns version of the JuliaUp executable.
- `available()` returns True if JuliaUp is available.
- `install(interactive=True)` installs JuliaUp. You don't normally need to call this as the
  other API functions automatically install JuliaUp if required.
- `meta()` returns the parsed contents of `juliaup.json`, which includes information about
  installed versions of Julia.

### Run JuliaUp
- `status()` print the status.
- `add(channel)` adds a channel.
- `remove(channel)` removes a channel.
- `update(channel=None)` updates all channels or the given channel.
- `default(channel)` sets the default channel.
- `link(channel, file)` links a Julia executable to a channel.
- `self_update()` updates JuliaUp itself.
- `run(args, **kw)` runs JuliaUp with the given arguments. Keyword arguments are passed on to
  `subprocess.run`.
