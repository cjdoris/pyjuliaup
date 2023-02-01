import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import urllib.request

__version__ = '0.1.1'

STATE = {
    'depot_dir': None,
    'dir': None,
    'meta_file': None,
    'available': None,
    'executable': None,
    'version': None,
}

def depot_dir():
    """The Julia depot directory."""
    if not STATE['depot_dir']:
        depot = os.environ.get('JULIA_DEPOT_PATH')
        if not depot:
            depot = os.path.join(os.path.expanduser('~'), '.julia')
        else:
            sep = ';' if os.name == 'nt' else ':'
            depot = depot.split(sep)[0]
        STATE['depot_dir'] = depot
    return STATE['depot_dir']

def dir():
    """The JuliaUp directory."""
    if not STATE['dir']:
        STATE['dir'] = os.path.join(depot_dir(), 'juliaup')
    return STATE['dir']

def meta_file():
    """The JuliaUp metadata json file."""
    if not STATE['meta_file']:
        STATE['meta_file'] = os.path.join(dir(), 'juliaup.json')
    return STATE['meta_file']

def _find():
    # search in the path
    exe = shutil.which('juliaup')
    if exe:
        return exe
    # try ~/.juliaup/bin/juliaup
    if not exe:
        exe = os.path.join(os.path.expanduser('~'), '.juliaup', 'bin', 'juliaup')
        if os.path.exists(exe):
            return exe
    # look in ~/.profile and ~/.bashrc
    for fn in [os.path.expanduser('~/.profile'), os.path.expanduser('~/.bashrc')]:
        if os.path.exists(fn):
            with open(fn) as fp:
                ok = False
                for line in fp:
                    if '>>> juliaup initialize >>>' in line:
                        ok = True
                    elif '<<< juliaup initialize <<<' in line:
                        ok = False
                    elif ok:
                        m = re.search('^ *export +PATH=([^ $;#]+)', line)
                        if m:
                            exe = os.path.join(m.group(1), 'juliaup')
                            if os.path.exists(exe):
                                return exe

def _version(exe):
    try:
        proc = subprocess.run([exe, '--version'], capture_output=True, check=True, encoding='utf8')
        words = proc.stdout.strip().split()
        if words[0].lower() == 'juliaup':
            return words[1]
    except:
        return

def _check(exe):
    ver = _version(exe)
    if not ver:
        raise Exception(f'Not a valid JuliaUp executable: {exe!r}')
    STATE['available'] = True
    STATE['executable'] = exe
    STATE['version'] = ver

def install(interactive=True):
    """Install JuliaUp.

    Args:
        interactive: By default this is True, meaning nothing will be installed without
            consent. Set this to False to install without interruption. On Windows this
            passes --accept-package-agreements and --accept-source-agreements to winget.
            On other operating systems this passes --yes to the JuliaUp install script.
    """
    if os.name == 'nt':
        cmd = ['winget', 'install', 'julia', '--source', 'msstore', '--force']
        if not interactive:
            cmd += ['--accept-package-agreements', '--accept-source-agreements']
        print(f'[juliaup] Installing: {shlex.join(cmd)}')
        subprocess.run(cmd, check=True)
    else:
        with tempfile.TemporaryDirectory() as dn:
            url = 'https://install.julialang.org'
            print(f'[juliaup] Downloading install script: {url}')
            fn = os.path.join(dn, 'script.sh')
            with urllib.request.urlopen(url) as fp:
                script = fp.read()
            with open(fn, 'wb') as fp:
                fp.write(script)
            cmd = ['/bin/sh', fn]
            print(f'[juliaup] Installing: {shlex.join(cmd)}')
            subprocess.run(cmd, check=True)
    exe = _find()
    if not exe:
        raise Exception('Just installed JuliaUp but cannot find it!')
    _check(exe)
    return exe

def executable():
    """Return the JuliaUp executable.

    If the executable cannot be found, JuliaUp will be automatically installed.
    """
    if STATE['available'] is None:
        STATE['available'] = False
        exe = os.environ.get('PYTHON_JULIAUP_EXE')
        if not exe:
            exe = _find()
        if not exe:
            print('[juliaup] JuliaUp is required but not installed. It will now be installed interactively.')
            print('[juliaup] Alternatively you may install it following the instructions at')
            print('[juliaup]     https://github.com/JuliaLang/juliaup')
            print('[juliaup] You could instead do juliaup.install(interactive=False).')
            exe = install()
        _check(exe)
    return STATE['executable']

def version():
    """The version of executable()."""
    executable()
    return STATE['version']

def available():
    """Test if JuliaUp is available."""
    if STATE['available'] is None:
        try:
            executable()
        except:
            STATE['available'] = False
    return STATE['available']

def run(args=[], **kw):
    """Run JuliaUp.

    Args:
        args: The arguments to juliaup.
        kw: Passed on to subprocess.run.
    """
    if isinstance(args, str):
        cmd = shlex.split(args)
    return subprocess.run([executable(), *args], **kw)

def _run(cmd, **kw):
    run(cmd, check=True, **kw)

def add(channel):
    """Add a channel."""
    _run(['add', channel])

def default(channel):
    """Set the default channel."""
    _run(['default', channel])

def link(channel, file):
    """Link a julia executable to a channel."""
    _run(['link', channel, file])

def remove(channel):
    """Remove a channel."""
    _run(['rm', channel])

def status():
    """Print the status."""
    _run(['status'])

def update(channel=None):
    """Update all channels or the given channel."""
    _run(['update'] if channel is None else ['update', channel])

def self_update():
    """Update JuliaUp itself."""
    _run(['self', 'update'])
    exe = _find()
    if not exe:
        raise Exception('Just installed JuliaUp but cannot find it!')
    _check(exe)

def meta():
    """The JuliaUp metadata.

    It is essentially the parsed contents of juliaup.json, except:
    - paths are absolute
    - versions now have an 'Executable' key
    - channels inherit keys from their version

    Hence to get the Julia executable for the channel '1.6' you can do
        meta()['InstalledChannels']['1.6']['Executable']
    """
    # read the metadata
    fn = meta_file()
    dn = os.path.dirname(fn)
    with open(fn) as fp:
        meta = json.load(fp)
    versions = meta.get('InstalledVersions', {})
    channels = meta.get('InstalledChannels', {})
    # make version.Path absolute
    # add version.Executable
    for x in versions.values():
        if 'Path' in x:
            x['Path'] = os.path.abspath(os.path.join(dn, x['Path']))
            x['Executable'] = os.path.abspath(os.path.join(x['Path'], 'bin', 'julia.exe' if os.name=='nt' else 'julia'))
    # have channels inherit items from their version
    for x in channels.values():
        if 'Version' in x and x['Version'] in versions:
            for (k,v) in versions[x['Version']].items():
                if k not in x:
                    x[k] = v
    return meta
