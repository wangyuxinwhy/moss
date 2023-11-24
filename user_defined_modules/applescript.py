from subprocess import run as sub_run


def run(script: str):
    output = sub_run(['osascript', '-e', script], check=False, capture_output=True, text=True)
    return {
        'returncode': output.returncode,
        'stdout': output.stdout.strip(),
        'stderr': output.stderr.strip(),
    }
